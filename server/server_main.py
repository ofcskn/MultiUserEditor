import socket
import threading
import os 
import json

HOST = '127.0.0.1'
PORT = 65432

clients = {}  # socket -> {'username': str, 'file': str}
files = {}    # filename -> content (str)
lock = threading.Lock()

SAVE_INTERVAL = 5  # seconds
SAVE_FOLDER = 'data'
os.makedirs(SAVE_FOLDER, exist_ok=True)

def broadcast_update(filename, message, exclude_sock=None):
    for client, info in clients.items():
        if info.get('file') == filename and client != exclude_sock:
            try:
                client.sendall(message.encode())
            except:
                continue

def save_files():
    with lock:
        for filename, content in files.items():
            with open(os.path.join(SAVE_FOLDER, filename), 'w', encoding='utf-8') as f:
                f.write(content)
    threading.Timer(SAVE_INTERVAL, save_files).start()

def handle_client(conn, addr):
    with conn:
        print(f"[+] Connected by {addr}")
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                msg = json.loads(data.decode())
                cmd = msg.get("cmd")

                if cmd == "LOGIN":
                    username = msg.get("username")
                    clients[conn] = {'username': username, 'file': None}
                    conn.sendall(json.dumps({"cmd": "FILES", "files": list(files.keys())}).encode())

                elif cmd == "CREATE_FILE":
                    filename = msg.get("filename")
                    with lock:
                        files[filename] = ""
                    conn.sendall(json.dumps({"cmd": "FILES", "files": list(files.keys())}).encode())

                elif cmd == "JOIN_FILE":
                    filename = msg.get("filename")
                    clients[conn]['file'] = filename
                    content = files.get(filename, "")
                    conn.sendall(json.dumps({"cmd": "LOAD", "content": content}).encode())

                elif cmd == "TEXT_UPDATE":
                    filename = clients[conn]['file']
                    content = msg.get("content")
                    with lock:
                        files[filename] = content
                    broadcast_update(filename, json.dumps({"cmd": "TEXT_UPDATE", "content": content}), exclude_sock=conn)

            except Exception as e:
                print("[-] Error:", e)
                break
    clients.pop(conn, None)
    print(f"[-] Disconnected {addr}")

def main():
    save_files()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("[+] Server listening...")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
