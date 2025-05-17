from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox, QLineEdit)
from client.views.layout_view import BaseWindow
from core.constants import MSG_FILES_PAGE_REDIRECT, MSG_LOGIN, MSG_LOGIN_ERROR, MSG_USER_ACTIVE_SESSION
from client.views.file_selector_view import FileSelector
from core.utils import send_json

class LoginWindow(BaseWindow):
    def __init__(self, sock, session, receiver, controller):
        super().__init__(sock, session, receiver, controller)
        self.setWindowTitle("Login")

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
        self.setLayout(self.layout)

        self.login_button.clicked.connect(self.login)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if username and password:
            send_json(self.sock, {"cmd": MSG_LOGIN, "username": username, "password": password})

            # Create a session to hold important informations
            self.session.set_user(username)

    def handle_server_message(self, msg):
        cmd = msg.get("cmd")
        if cmd == MSG_LOGIN_ERROR:
            QMessageBox.warning(self, "Login error: ", msg.get("message"))
            return
        elif cmd == MSG_USER_ACTIVE_SESSION:
            QMessageBox.warning(self, "Login error: ", msg.get("message"))
            return
        elif cmd == MSG_FILES_PAGE_REDIRECT:
            self.controller.show_selector(msg.get("files", []))