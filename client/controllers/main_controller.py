from PySide6.QtWidgets import (QMainWindow)
from client.views.file_selector_view import FileSelector
from client.views.login_view import LoginWindow

class MainApp(QMainWindow):
    def __init__(self, sock, session, receiver):
        super().__init__()
        self.sock = sock
        self.session = session
        self.receiver = receiver

        self.current_view = None

        self.show_login()

    def show_login(self):
        # Disconnect old view if exists
        if self.current_view:
            try:
                self.receiver.message_received.disconnect(self.current_view.handle_server_message)
            except TypeError:
                pass  # already disconnected or was never connected

        self.current_view = LoginWindow(self.sock, self.session, self.receiver, self)
        self.setCentralWidget(self.current_view)

        # Connect new view
        self.receiver.message_received.connect(self.current_view.handle_server_message)

    def show_selector(self, files):
        if self.current_view:
            try:
                print("receiver", self.receiver)
                self.receiver.message_received.disconnect(self.current_view.handle_server_message)
            except TypeError:
                pass  # already disconnected or was never connected

        self.current_view = FileSelector(self.sock, self.session, self.receiver, self)
        self.setCentralWidget(self.current_view)

        # Connect new view to receiver
        self.receiver.message_received.connect(self.current_view.listen_server)

        # Load initial file list
        self.current_view.load_files(files)
