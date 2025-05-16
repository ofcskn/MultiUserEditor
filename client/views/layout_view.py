from PySide6.QtWidgets import QMainWindow
from core.socker_receiver import SocketReceiver
from PySide6.QtWidgets import (QMainWindow)

class BaseWindow(QMainWindow):
    def __init__(self, sock, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.sock = sock

        # Initialize the receiver and connect to the handle_server_message method
        self.receiver = SocketReceiver(self.sock)
        self.receiver.message_received.connect(self.handle_server_message)
        self.receiver.start()

    def handle_server_message(self, msg: dict):
        """Handle server messages based on their commands."""
        print(msg)  # For debugging purposes, print the received message