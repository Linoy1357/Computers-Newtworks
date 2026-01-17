import socket
import threading

# הגדרות חיבור
HOST = '127.0.0.1'  # Localhost
PORT = 5555         # פורט שרירותי (מעל 1024)

# מילון לשמירת הלקוחות המחוברים: {שם_לקוח: סוקט}
clients = {}

def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    
    name = None
    
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            
            if not message:
                break 
            
            # הדפסה בשרת לצורך מעקב (Log)
            print(f"[LOG] {name if name else client_address}: {message}")
            
            parts = message.split('|')
            command = parts[0]
            
            if command == "NAME":
                name = parts[1]
                # בדיקה אם השם כבר תפוס
                if name in clients:
                    client_socket.send("[SERVER] Name already taken. Please reconnect with a different name.".encode('utf-8'))
                    break
                else:
                    clients[name] = client_socket
                    print(f"[REGISTERED] Client name is: {name}")
                    client_socket.send(f"[SERVER] Welcome {name}! You are now connected.".encode('utf-8'))
                
            elif command == "MSG":
                # המבנה: MSG|TargetName|Content
                if len(parts) < 3:
                     continue # הגנה מפני הודעה שבורה

                target_name = parts[1]
                msg_content = parts[2]
                
                # --- הלב של שלב 3: ניתוב ההודעה ---
                if target_name in clients:
                    target_socket = clients[target_name]
                    try:
                        # עיצוב ההודעה שתגיע לצד השני: [SenderName]: Message
                        final_msg = f"[{name}]: {msg_content}"
                        target_socket.send(final_msg.encode('utf-8'))
                    except Exception as e:
                        # אם השליחה נכשלה (למשל הלקוח התנתק פתאום)
                        print(f"[ERROR] Sending to {target_name} failed: {e}")
                else:
                    # אם המשתמש לא נמצא, נחזיר הודעת שגיאה לשולח
                    error_msg = f"[SERVER] User '{target_name}' not found or offline."
                    client_socket.send(error_msg.encode('utf-8'))

            elif command == "EXIT":
                break
                
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        if name and name in clients:
            del clients[name]
        client_socket.close()
        print(f"[DISCONNECTED] {name if name else client_address} disconnected.")

def start_server():
    """
    הפונקציה הראשית שמפעילה את השרת
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5) # מאפשר עד 5 ממתינים בתור (אבל ה-Threads יטפלו ביותר)
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")
    
    while True:
        # המתנה ללקוח חדש (פעולה חוסמת)
        client_socket, client_address = server.accept()
        
        # יצירת Thread חדש לטיפול בלקוח הזה
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()