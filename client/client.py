import socket
import sys
from PySide6.QtWidgets import (QApplication)
from client.session import AppSession
from client.views.layout_view import BaseWindow
from client.views.login_view import LoginWindow
from core.constants import HOST, PORT
from core.socker_receiver import SocketReceiver

def start_client():
    app = QApplication(sys.argv)
    # Initialize shared socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    # Initialize shared session object (if necessary)
    session = AppSession()

    win = LoginWindow(sock, session) 
    win.show()

    sys.exit(app.exec())