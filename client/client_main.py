import socket
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

HOST = '127.0.0.1'
PORT = 65432

class ClientApp:
    def __init__(self, master):
        self.master = master
        master.title("Çok Kullanıcılı Editör")

        self.text_area = ScrolledText(master, wrap=tk.WORD, width=60, height=20)
        self.text_area.pack()

        self.entry = tk.Entry(master, width=50)
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", self.send_text)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        self.receiver_thread = threading.Thread(target=self.receive)
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def send_text(self, event):
        message = self.entry.get()
        self.sock.sendall(message.encode())
        self.entry.delete(0, tk.END)

    def receive(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                self.text_area.insert(tk.END, f"{data.decode()}\n")
                self.text_area.see(tk.END)
            except:
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
