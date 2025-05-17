from PySide6.QtWidgets import QWidget

class BaseWindow(QWidget):
    def __init__(self, sock, session, receiver, controller, parent=None):
        super().__init__(parent)
        self.session = session
        self.sock = sock
        self.receiver = receiver
        self.controller = controller