import sys
import socket
import threading
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit, QPushButton,
      QVBoxLayout, QWidget, QListWidget, QTextEdit, QMessageBox, QLabel)
from PySide6.QtCore import Signal, QObject

HOST = '127.0.0.1'
PORT = 65432

class Communicator(QObject):
    update_signal = Signal(str)

class EditorWindow(QMainWindow):
    def __init__(self, sock, filename, username, parent=None):
        super().__init__(parent)
        self.parent_selector = parent  # FileSelector referansını burada tutalım
        self.sock = sock
        self.filename = filename
        self.setWindowTitle(f"{username} - Düzenleniyor: {filename}")
        
        # Metin düzenleyicisi
        self.text_edit = QTextEdit()
        self.setCentralWidget(self.text_edit)

        # Kaydet butonu
        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save_file)  # Kaydet butonuna tıklama işlevini bağla

        # Butonu layout'a ekle
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.save_button)
        
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.text_edit.textChanged.connect(self.send_update)
        self.comm = Communicator()
        self.comm.update_signal.connect(self.apply_update)

        threading.Thread(target=self.listen_server, daemon=True).start()


    def save_file(self):
        """
        Kaydetme işlemi: Dosyadaki içeriği sunucuya gönder.
        """
        content = self.text_edit.toPlainText()
        msg = {"cmd": "TEXT_UPDATE", "content": content}
        self.sock.sendall(json.dumps(msg).encode())
        print(f"[+] {self.filename} kaydedildi.")

    def closeEvent(self, event):
        """
        Editor kapatildiginda bu fonksiyon calisir.
        """
        if self.parent_selector:
            self.parent_selector.open_editors.pop(self.filename, None)
        super().closeEvent(event)

    def send_update(self):
        msg = {"cmd": "TEXT_UPDATE", "content": self.text_edit.toPlainText()}
        self.sock.sendall(json.dumps(msg).encode())

    def apply_update(self, content):
        self.text_edit.blockSignals(True)
        self.text_edit.setPlainText(content)
        self.text_edit.blockSignals(False)

    def listen_server(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                msg = json.loads(data.decode())
                if msg.get("cmd") == "TEXT_UPDATE":
                    self.comm.update_signal.emit(msg.get("content"))
            except:
                break

class CollaborativeEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerçek Zamanlı Ortak Editör")
        self.resize(600, 400)

        self.text_edit = QTextEdit()
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        self.communicator = Communicator()
        self.communicator.update_signal.connect(self.update_text_from_server)

        self.text_edit.textChanged.connect(self.on_text_changed)
        self.ignore_changes = False

        threading.Thread(target=self.listen_to_server, daemon=True).start()

    def on_text_changed(self):
        if self.ignore_changes:
            return
        text = self.text_edit.toPlainText()
        try:
            self.sock.sendall(text.encode('utf-8'))
        except:
            pass

    def listen_to_server(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                text = data.decode('utf-8')
                self.communicator.update_signal.emit(text)
            except:
                break

    def update_text_from_server(self, text):
        self.ignore_changes = True
        self.text_edit.setPlainText(text)
        self.ignore_changes = False

    def closeEvent(self, event):
        self.sock.close()

class FileSelector(QMainWindow):
    open_editor_signal = Signal(str, str)  # filename, content
    def __init__(self, sock, username):
        super().__init__()
        self.open_editors = {}
        self.sock = sock
        self.username = username
        self.setWindowTitle(f"Dosya Seç - {username}")
        self.open_editor_signal.connect(self.open_editor_window)
        self.layout = QVBoxLayout()
        self.user_label = QLabel(f"Kullanıcı: {username}")
        self.file_list = QListWidget()
        self.new_file_input = QLineEdit()
        self.new_file_input.setPlaceholderText("Yeni dosya adı")
        self.new_file_btn = QPushButton("Dosya Oluştur")

        self.layout.addWidget(self.user_label)
        self.layout.addWidget(self.file_list)
        self.layout.addWidget(self.new_file_input)
        self.layout.addWidget(self.new_file_btn)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.new_file_btn.clicked.connect(self.create_file)
        self.file_list.itemDoubleClicked.connect(self.join_file)

        threading.Thread(target=self.listen_server, daemon=True).start()

    def open_editor_window(self, filename, content):
        # FileSelector içinde EditorWindow açıldığında:
        editor = EditorWindow(self.sock, filename=filename, username=self.username, parent=self)
        editor.text_edit.setPlainText(content)
        editor.show()
        self.open_editors[filename] = editor 

    def create_file(self):
        name = self.new_file_input.text().strip()
        if name:
            msg = {"cmd": "CREATE_FILE", "filename": name}
            self.sock.sendall(json.dumps(msg).encode())

    def join_file(self, item):
        filename = item.text()
        self.sock.sendall(json.dumps({"cmd": "JOIN_FILE", "filename": filename}).encode())

    def listen_server(self):
        while True:
            
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                msg = json.loads(data.decode())
                if msg.get("cmd") == "FILES":
                    self.file_list.clear()
                    for f in msg.get("files", []):
                        self.file_list.addItem(f)
                elif msg.get("cmd") == "LOAD":
                    filename = msg.get("filename", "[dosya]")
                    if filename in self.open_editors:
                        self.open_editors[filename].raise_()  # pencere zaten açıksa öne getir
                        self.open_editors[filename].activateWindow()
                    else:
                        self.open_editor_signal.emit(filename, msg.get("content", ""))

                elif msg.get("cmd") == "ERROR":
                    QMessageBox.critical(self, "Hata", msg.get("message", "Bilinmeyen hata"))
            except Exception as e:
                print("Client Error:", e)
                break

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Giriş")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        self.layout = QVBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcı Adı")
        self.login_button = QPushButton("Giriş Yap")
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.login_button)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.login_button.clicked.connect(self.login)

    def login(self):
        username = self.username_input.text().strip()
        if username:
            msg = {"cmd": "LOGIN", "username": username}
            self.sock.sendall(json.dumps(msg).encode())
            data = self.sock.recv(4096)
            msg = json.loads(data.decode())
            if msg.get("cmd") == "ERROR":
                QMessageBox.warning(self, "Hata", msg.get("message"))
                return
            elif msg.get("cmd") == "FILES":
                self.selector = FileSelector(self.sock, username=username)
                self.selector.file_list.clear()
                for f in msg.get("files", []):
                    self.selector.file_list.addItem(f)
                self.selector.show()
                self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec())
