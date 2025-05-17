from PySide6.QtWidgets import (QVBoxLayout, QWidget, QPushButton, QMessageBox, QLineEdit)
from client.views.layout_view import BaseWindow
from core.constants import MSG_SERVER_REDIRECT_TO_FILES_VIEW, MSG_CLIENT_LOGIN, MSG_SERVER_LOGIN_FAILURE, MSG_SERVER_USER_ACTIVE_SESSION
from core.utils import send_json
from PySide6.QtCore import Qt

class LoginWindow(BaseWindow):
    def __init__(self, sock, session, receiver, controller):
        super().__init__(sock, session, receiver, controller)
        self.setWindowTitle("Login")
        
        # Main layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(100, 100, 100, 100)
        self.layout.setAlignment(Qt.AlignTop)  # Align widgets to the top
        self.layout.setSpacing(10)  # Optional: control spacing between widgets

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
            send_json(self.sock, {"cmd": MSG_CLIENT_LOGIN, "username": username, "password": password})

            # Create a session to hold important informations
            self.session.set_user(username)
        else:
            QMessageBox.warning(self, "Login error: ","Please enter your username and password.")

    def handle_server_message(self, msg):
        cmd = msg.get("cmd")
        if cmd == MSG_SERVER_LOGIN_FAILURE:
            QMessageBox.warning(self, "Login error: ", msg.get("message"))
            return
        elif cmd == MSG_SERVER_USER_ACTIVE_SESSION:
            QMessageBox.warning(self, "Login error: ", msg.get("message"))
            return
        elif cmd == MSG_SERVER_REDIRECT_TO_FILES_VIEW:
            self.controller.show_selector(msg.get("files", []))