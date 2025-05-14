import sys
import socket
import threading
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit, QPushButton,
      QVBoxLayout, QWidget, QListWidget, QTextEdit, QMessageBox, QLabel)
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QTextEdit, QPushButton, QAbstractItemView, QListWidget)
from PySide6.QtGui import QActionEvent
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QTextEdit, QPushButton, QMenu, QWidget, QToolBar)
from PySide6.QtGui import QTextCharFormat, QFont, QAction, Qt
from constants import HOST, MSG_CREATE_FILE, MSG_ERROR, MSG_FILE_LIST, MSG_FILE_UPDATE, MSG_JOIN_FILE, MSG_LOAD, MSG_LOGIN, MSG_LOGIN_ERROR, PORT
from file_manager import load_files
from session import AppSession
from user_manager import load_users

session = AppSession()
lock = threading.Lock()

class Communicator(QObject):
    update_signal = Signal(str)

class EditorWindow(QMainWindow):
    def __init__(self, sock, filename, parent=None):
        super().__init__(parent)
        self.parent_selector = parent  # FileSelector referansını burada tutalım
        self.sock = sock
        self.filename = filename

        # Get username from the session
        username = session.get_user()

        self.setWindowTitle(f"{username} - Düzenleniyor: {filename}")
  
        # Create a rich text editor (QTextEdit for RTF support)
        self.text_edit = QTextEdit()
        self.setCentralWidget(self.text_edit)

        # Create toolbar for formatting buttons
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # Bold button
        bold_action = QAction("Bold", self)
        bold_action.triggered.connect(self.set_bold)
        self.toolbar.addAction(bold_action)

        # Italic button
        italic_action = QAction("Italic", self)
        italic_action.triggered.connect(self.set_italic)
        self.toolbar.addAction(italic_action)

        # Underline button
        underline_action = QAction("Underline", self)
        underline_action.triggered.connect(self.set_underline)
        self.toolbar.addAction(underline_action)

        # Save button
        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save_file)

        # Layout setup
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Layout setup
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.text_edit.textChanged.connect(self.save_file)
        self.comm = Communicator()
        self.comm.update_signal.connect(self.apply_update)

        threading.Thread(target=self.listen_server, daemon=True).start()

    def set_bold(self):
        """Apply bold formatting"""
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            cursor.mergeCharFormat(self.get_bold_format())
        else:
            cursor.insertText("Bold")  # Insert text as an example, replace this with actual handling

    def set_italic(self):
        """Apply italic formatting"""
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            cursor.mergeCharFormat(self.get_italic_format())
        else:
            cursor.insertText("Italic")  # Insert text as an example, replace this with actual handling

    def set_underline(self):
        """Apply underline formatting"""
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            cursor.mergeCharFormat(self.get_underline_format())
        else:
            cursor.insertText("Underlined")  # Insert text as an example, replace this with actual handling

    def get_bold_format(self):
        """Return bold text format"""
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        return bold_format

    def get_italic_format(self):
        """Return italic text format"""
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        return italic_format

    def get_underline_format(self):
        """Return underline text format"""
        underline_format = QTextCharFormat()
        underline_format.setFontUnderline(True)
        return underline_format

    def save_file(self):
        """
        Save the RTF content: Send the current text content as HTML (RTF-like) format to the server.
        """
        content = self.text_edit.toHtml()  # Use toHtml() for rich text content
        msg = {"cmd": MSG_FILE_UPDATE, "content": content}
        self.sock.sendall(json.dumps(msg).encode())
        print(f"[+] {self.filename} kaydedildi.")

    def closeEvent(self, event):
        """
        Editor kapatildiginda bu fonksiyon calisir.
        """
        if self.parent_selector:
            self.parent_selector.open_editors.pop(self.filename, None)
        super().closeEvent(event)

    def apply_update(self, content):
        """
        Apply updates from the server. This method will receive rich text content.
        """
        self.text_edit.blockSignals(True)
        self.text_edit.setHtml(content)  # Apply the HTML content (formatted text)
        self.text_edit.blockSignals(False)

    def listen_server(self):
        """
        Listen for updates from the server.
        """
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                msg = json.loads(data.decode())
                if msg.get("cmd") == MSG_FILE_UPDATE:
                    self.comm.update_signal.emit(msg.get("content"))
            except:
                break

class FileSelector(QMainWindow):
    open_editor_signal = Signal(str, str)  # filename, content
    def __init__(self, sock):
        super().__init__()
        self.customContextMenuRequested.connect(self.show_context_menu)

        # Get username from the session
        current_username = session.get_user()

        self.open_editors = {}
        self.sock = sock
        self.setWindowTitle(f"Dosya Seç - {current_username}")
        self.open_editor_signal.connect(self.open_editor_window)
        self.layout = QVBoxLayout()
        self.user_label = QLabel(f"Kullanıcı: {current_username}")
        self.file_list = QListWidget()

        self.new_file_input_label = QLabel("Dosya Adı")
        self.new_file_input = QLineEdit()
        self.new_file_input.setPlaceholderText("Yeni dosya adı")

        
        # Scrollable list for viewers
        self.viewers_list_label = QLabel(f"Dosya Görüntüleyecekler (seçiniz)")
        self.file_viewers_list = QListWidget()
        self.file_viewers_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.file_viewers_list.setFixedHeight(100)  # adjust as needed

        self.editors_list_label = QLabel(f"Dosya Düzenleyecekler (seçiniz)")
        # Scrollable list for editors
        self.file_editors_list = QListWidget()
        self.file_editors_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.file_editors_list.setFixedHeight(100)  # adjust as needed

        # Get all usernames without current user
        users = load_users()

        for user in users:
            if user["username"] != current_username:
                self.file_viewers_list.addItem(user["username"])
                self.file_editors_list.addItem(user["username"])

        self.new_file_btn = QPushButton("Dosya Oluştur")

        self.layout.addWidget(self.user_label)
        self.layout.addWidget(self.file_list)

        self.layout.addWidget(self.new_file_input_label)
        self.layout.addWidget(self.new_file_input)

        self.layout.addWidget(self.viewers_list_label)
        self.layout.addWidget(self.file_viewers_list)

        self.layout.addWidget(self.editors_list_label)
        self.layout.addWidget(self.file_editors_list)

        self.layout.addWidget(self.new_file_btn)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.new_file_btn.clicked.connect(self.create_file)
        self.file_list.itemDoubleClicked.connect(self.join_file)

        threading.Thread(target=self.listen_server, daemon=True).start()


    def show_context_menu(self, pos):
        item = self.itemAt(pos)
        if not item:
            return

        filename = item.text()
        username = session.get_user()

        menu = QMenu(self)
        view_action = menu.addAction("View")
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")

        action = menu.exec_(self.mapToGlobal(pos))

        if action == view_action:
            self.try_view_file(filename, username)
        elif action == edit_action:
            self.try_edit_file(filename, username)
        elif action == delete_action:
            self.try_delete_file(filename, username)

    # def try_view_file(self, filename, username):
    #     file_info = files.get(filename, {})
    #     if username not in file_info.get("viewers", []):
    #         QMessageBox.warning(self, "Permission Denied", "You are not allowed to view this file.")
    #         return
    #     self.open_viewer_window(filename)

    # def try_edit_file(self, filename, username):
    #     file_info = files.get(filename, {})
    #     if username not in file_info.get("editors", []):
    #         QMessageBox.warning(self, "Permission Denied", "You are not allowed to edit this file.")
    #         return
    #     self.open_editor_window(filename)

    # def try_delete_file(self, filename, username):
    #     file_info = files.get(filename, {})
    #     if username not in file_info.get("editors", []):  # Only editors can delete
    #         QMessageBox.warning(self, "Permission Denied", "You are not allowed to delete this file.")
    #         return

    #     confirm = QMessageBox.question(self, "Delete File", f"Are you sure you want to delete '{filename}'?")
    #     if confirm == QMessageBox.Yes:
    #         with lock:
    #             files.pop(filename, None)
    #         self.takeItem(self.row(self.findItems(filename, Qt.MatchExactly)[0]))

    def open_editor_window(self, filename, content):
        # FileSelector içinde EditorWindow açıldığında:
        editor = EditorWindow(self.sock, filename=filename, parent=self)
        editor.text_edit.setText(content)
        editor.show()
        self.open_editors[filename] = editor 

    def create_file(self):
        name = self.new_file_input.text().strip()
        
        selected_viewers = [item.text() for item in self.file_viewers_list.selectedItems()]
        selected_editors = [item.text() for item in self.file_editors_list.selectedItems()]

        # Get the logged user for ownership
        owner_username = session.get_user()

        if name:
            msg = {"cmd": MSG_CREATE_FILE, "filename": name, "owner": owner_username, "viewers": selected_viewers, "editors": selected_editors}
            self.sock.sendall(json.dumps(msg).encode())

    def join_file(self, item):
        filename = item.text()
        self.sock.sendall(json.dumps({"cmd": MSG_JOIN_FILE, "filename": filename}).encode())

    def listen_server(self):
        while True:
            
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                msg = json.loads(data.decode())
                if msg.get("cmd") == MSG_FILE_LIST:
                    self.file_list.clear()
                    for f in msg.get("files", []):
                        self.file_list.addItem(f)
                elif msg.get("cmd") == MSG_LOAD:
                    filename = msg.get("filename", "[dosya]")
                    if filename in self.open_editors:
                        self.open_editors[filename].raise_()  # pencere zaten açıksa öne getir
                        self.open_editors[filename].activateWindow()
                    else:
                        self.open_editor_signal.emit(filename, msg.get("content", ""))

                elif msg.get("cmd") == MSG_ERROR:
                    QMessageBox.critical(self, "Hata", msg.get("message", "Bilinmeyen hata"))
            except Exception as e:
                print("Client Error:", e)
                break

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Giriş")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        self.layout = QVBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcı Adı")

        # password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Şifre giriniz")
        
        self.login_button = QPushButton("Giriş Yap ya da Kaydol")
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.login_button.clicked.connect(self.login)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if username and password:
            msg = {"cmd": MSG_LOGIN, "username": username, "password": password}
            self.sock.sendall(json.dumps(msg).encode())
            data = self.sock.recv(4096)
            msg = json.loads(data.decode())
            
            # Create a session to hold important informations
            session.set_user(username)

            if msg.get("cmd") == MSG_LOGIN_ERROR:
                QMessageBox.warning(self, "Giriş Hatalı: ", msg.get("message"))
                return
            
            elif msg.get("cmd") == MSG_FILE_LIST:
                self.selector = FileSelector(self.sock)
                self.selector.file_list.clear()
                for f in msg.get("files", []):
                    self.selector.file_list.addItem(f)
                self.selector.show()
                self.close()

if __name__ == '__main__':
    # files = load_files()
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec())
