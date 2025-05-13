import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

clients = []

def handle_client(conn, addr):
    print(f"[+] Yeni bağlantı: {addr}")
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            print(f"[{addr}] {data.decode()}")
            for c in clients:
                if c != conn:
                    try:
                        c.sendall(data)
                    except:
                        pass
        except:
            break
    print(f"[-] Bağlantı kapandı: {addr}")
    clients.remove(conn)
    conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[Server] Dinleniyor: {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            clients.append(conn)
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
