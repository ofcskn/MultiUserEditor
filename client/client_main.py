import sys
import threading
import socket
from PySide6.QtWidgets import QApplication, QTextEdit, QWidget, QVBoxLayout
from PySide6.QtCore import Signal, QObject

HOST = '127.0.0.1'
PORT = 65432

class Communicator(QObject):
    update_text = Signal(str)

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
        self.communicator.update_text.connect(self.update_text_from_server)

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
                self.communicator.update_text.emit(text)
            except:
                break

    def update_text_from_server(self, text):
        self.ignore_changes = True
        self.text_edit.setPlainText(text)
        self.ignore_changes = False

    def closeEvent(self, event):
        self.sock.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = CollaborativeEditor()
    editor.show()
    sys.exit(app.exec())