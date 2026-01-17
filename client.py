import socket
import threading
import sys

# הגדרות חיבור (חייב להיות זהה לשרת)
HOST = '127.0.0.1'
PORT = 5555

def receive_messages(client_socket):
    """
    פונקציה שרצה ברקע ומדפיסה הודעות שמגיעות מהשרת
    """
    while True:
        try:
            # קבלת הודעה
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("\n[DISCONNECTED] Server closed connection.")
                client_socket.close()
                sys.exit() # יציאה מהתוכנית
            
            # הדפסת ההודעה שהתקבלה
            # ה- \r מוחק את השורה הנוכחית כדי שהפלט לא יתערבב עם ה '>>>'
            print(f"\r{message}\n>>> ", end="")
            
        except Exception as e:
            print(f"\n[ERROR] Connection lost: {e}")
            client_socket.close()
            break

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((HOST, PORT))
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        return

    # שלב 1: הזדהות מול השרת
    name = input("Enter your username: ")
    # שליחת הודעת הזדהות לפי הפרוטוקול: NAME|MyName
    register_msg = f"NAME|{name}"
    client_socket.send(register_msg.encode('utf-8'))

    # שלב 2: הפעלת תנליכון להאזנה להודעות נכנסות
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True # ייסגר אוטומטית כשהתוכנית הראשית נסגרת
    receive_thread.start()

    print(f"Connected as {name}!")
    print("To send message: @username message")
    print("Type 'exit' to quit.")
    print(">>> ", end="")

    # שלב 3: לולאת שליחת הודעות (התהליכון הראשי)
    while True:
        user_input = input() # מחכה לקלט מהמשתמש
        
        if user_input.lower() == 'exit':
            client_socket.send("EXIT".encode('utf-8'))
            break
        
        # בדיקה אם הפורמט הוא @name message
        if user_input.startswith("@"):
            try:
                # פירוק הקלט: @danny hello world -> target=danny, content=hello world
                parts = user_input.split(' ', 1)
                target = parts[0][1:] # מוריד את ה-@
                content = parts[1]
                
                # בניית ההודעה לפי הפרוטוקול: MSG|target|content
                protocol_msg = f"MSG|{target}|{content}"
                client_socket.send(protocol_msg.encode('utf-8'))
                
            except IndexError:
                print("Invalid format. Use: @username message")
        else:
            print("Invalid format. Start with @username to send a message.")
            print(">>> ", end="")

    client_socket.close()

if __name__ == "__main__":
    start_client()