import sys
import threading
from PySide6.QtWidgets import (QApplication)
from client.views.login_view import LoginWindow
from client.session import AppSession

session = AppSession()
lock = threading.Lock()

def start_client():
    app = QApplication(sys.argv)
    win = LoginWindow(session)
    win.show()
    sys.exit(app.exec())
