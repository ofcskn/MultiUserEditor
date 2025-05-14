from views.login_view import LoginWindow
import sys
import threading
from PySide6.QtWidgets import (QApplication)
from session import AppSession

session = AppSession()
lock = threading.Lock()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = LoginWindow(session)
    win.show()
    sys.exit(app.exec())
