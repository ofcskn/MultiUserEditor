from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton

class BaseWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set the main window size
        self.setFixedSize(800, 800)

        # Optional: Set window title
        self.setWindowTitle("MultiUserEditor")
