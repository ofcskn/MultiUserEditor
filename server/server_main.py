import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

clients = []

def handle_client(conn, addr):
    print(f"[+] Yeni bağlantı: {addr}")
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            print(f"[{addr}] {data.decode()}")
            # Şimdilik herkese geri yayınla
            for c in clients:
                if c != conn:
                    c.sendall(data)
        except:
            break
    conn.close()
    clients.remove(conn)
    print(f"[-] Bağlantı kapandı: {addr}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[Server] Dinleniyor: {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        clients.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
