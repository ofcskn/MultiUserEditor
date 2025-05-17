import socket
import sys
from PySide6.QtWidgets import (QApplication)
from client.controllers.main_controller import MainApp
from client.session import AppSession
from core.constants import HOST, PORT
from core.socker_receiver import SocketReceiver

def start_client():
    app = QApplication(sys.argv)
    # Initialize shared socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    # Initialize shared session object (if necessary)
    session = AppSession()

    # ✅ Create ONE SocketReceiver instance globally
    receiver = SocketReceiver(sock)
    receiver.start()

    win = MainApp(sock, session, receiver)
    win.show()

    sys.exit(app.exec())