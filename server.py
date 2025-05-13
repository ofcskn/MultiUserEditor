import socket
import threading
import os 
import json
import csv
from datetime import datetime
import hashlib
from constants import MSG_CREATE_FILE, MSG_ERROR, MSG_FILE_LIST, MSG_JOIN_FILE, MSG_LOGIN, MSG_FILE_UPDATE

HOST = '127.0.0.1'
PORT = 65433
SAVE_INTERVAL = 5  # seconds

DATA_FOLDER = 'data'
SAVE_FOLDER = 'www/files'

USERS_CSV = f'data/users.csv'
FILES_CSV = f'data/files.csv'

clients = {}  # socket -> {'username': str, 'file': str}
files = {}    # filename -> content (str)
lock = threading.Lock()

os.makedirs(SAVE_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_files():
    if not os.path.exists(FILES_CSV):
        return

    with open(FILES_CSV, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 1:
                filename = row[0]
                filepath = os.path.join(SAVE_FOLDER, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as content_file:
                        files[filename] = content_file.read()

def load_users():
    if not os.path.exists(USERS_CSV):
        return {}
    with open(USERS_CSV, newline='') as file:
        reader = csv.reader(file)
        return {row[0]: row[1] for row in reader if len(row) >= 2}

def save_user(username, password):
    users = load_users()
    if username not in users:
        with open(USERS_CSV, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([username, hash_password(password)])

def add_file_metadata(filename, owner, viewers=None, editors=None):
    extension = os.path.splitext(filename)[1]
    size = len(files[filename].encode('utf-8'))
    create_date = datetime.now().isoformat()
    with open(FILES_CSV, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([filename, extension, create_date, size, owner, viewers, editors])

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

                if cmd == MSG_LOGIN:
                    username = msg.get("username")
                    password = msg.get("password")
                    users = load_users()
                    hashed = hash_password(password)

                    if username in users:
                        if users[username] != hashed:
                            conn.sendall(json.dumps({"cmd": MSG_ERROR, "message": "Şifre yanlış."}).encode())
                            continue
                    else:
                        save_user(username, password)

                    clients[conn] = {'username': username, 'file': None}
                    conn.sendall(json.dumps({
                        "cmd": MSG_FILE_LIST,
                        "files": list(files.keys()),
                        "username": username
                    }).encode())

                elif cmd == MSG_CREATE_FILE:
                    filename = msg.get("filename")
                    owner = msg.get("owner")
                    viewers = msg.get("viewers")
                    editors = msg.get("editors")
                    with lock:
                        files[filename] = ""
                        add_file_metadata(filename, owner, viewers, editors)
                    conn.sendall(json.dumps({"cmd": MSG_FILE_LIST, "files": list(files.keys())}).encode())

                    for client in clients:
                        if client != conn:
                            try:
                                client.sendall(json.dumps({"cmd": MSG_FILE_LIST, "files": list(files.keys())}).encode())
                            except:
                                continue

                elif cmd == MSG_JOIN_FILE:
                    filename = msg.get("filename")
                    clients[conn]['file'] = filename
                    content = files.get(filename, "")
                    conn.sendall(json.dumps({
                        "cmd": MSG_JOIN_FILE,
                        "content": content,
                        "filename": filename
                    }).encode())

                elif cmd == MSG_FILE_UPDATE:
                    filename = clients[conn]['file']
                    content = msg.get("content")
                    with lock:
                        files[filename] = content
                    broadcast_update(filename, json.dumps({
                        "cmd": MSG_FILE_UPDATE,
                        "content": content
                    }), exclude_sock=conn)

            except Exception as e:
                print("[-] Error:", e)
                break

    clients.pop(conn, None)
    print(f"[-] Disconnected {addr}")

def main():
    load_files()
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