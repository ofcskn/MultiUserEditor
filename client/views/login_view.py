import socket
import json
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox, QLineEdit)
from core.constants import HOST, MSG_FILE_LIST, MSG_LOGIN, MSG_LOGIN_ERROR, PORT
from client.views.file_selector_view import FileSelector

class LoginWindow(QMainWindow):
    def __init__(self, session):
        super().__init__()
        self.setWindowTitle("Login")

        self.session = session
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        self.layout = QVBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        # password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Password")
        
        self.login_button = QPushButton("Login/Register")
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.login_button.clicked.connect(self.login)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if username and password:
            msg = {"cmd": MSG_LOGIN, "username": username, "password": password}
            self.sock.sendall(json.dumps(msg).encode())
            data = self.sock.recv(4096)
            msg = json.loads(data.decode())
            
            # Create a session to hold important informations
            self.session.set_user(username)

            if msg.get("cmd") == MSG_LOGIN_ERROR:
                QMessageBox.warning(self, "Login error: ", msg.get("message"))
                return
            
            elif msg.get("cmd") == MSG_FILE_LIST:
                self.selector = FileSelector(self.sock, self.session)
                self.selector.file_list.clear()
                for f in msg.get("files", []):
                    self.selector.file_list.addItem(f)
                self.selector.show()
                self.close()