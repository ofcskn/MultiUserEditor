import threading
import json
from PySide6.QtWidgets import (QMenu, QLineEdit, QPushButton, QVBoxLayout, QWidget, QListWidget, QMessageBox, QLabel, QAbstractItemView)
from PySide6.QtCore import Signal
from client.views.layout_view import BaseWindow
from core.constants import MSG_CREATE_FILE, MSG_ERROR, MSG_FILE_LIST, MSG_FILE_LOAD_VIEWER, MSG_JOIN_FILE, MSG_FILE_LOAD
from core.user_manager import load_users
from client.views.editor_view import EditorWindow
from PySide6.QtCore import Qt
from core.utils import send_json

class FileSelector(BaseWindow):
    open_editor_signal = Signal(str, str, bool)  # filename, content, isViewed
    def __init__(self, sock, session):
        super().__init__(sock, session)
        self.sock = sock

        # Get username from the session
        current_username = self.session.get_user()

        self.open_editors = {}
        self.open_editor_signal.connect(self.open_editor_window)

        self.setWindowTitle(f"Choose a file - {current_username}")
        self.layout = QVBoxLayout()
        self.user_label = QLabel(f"Active User: {current_username}")

        self.file_list = QListWidget()

        self.new_file_input_label = QLabel("Filename")
        self.new_file_input = QLineEdit()
        self.new_file_input.setPlaceholderText("New file name")

        # Scrollable list for viewers
        self.viewers_list_label = QLabel(f"Viewers (choose)")
        self.file_viewers_list = QListWidget()
        self.file_viewers_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.file_viewers_list.setFixedHeight(100)  # adjust as needed

        self.editors_list_label = QLabel(f"Editors (choose)")
        # Scrollable list for editors
        self.file_editors_list = QListWidget()
        self.file_editors_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.file_editors_list.setFixedHeight(100)  # adjust as needed

        # Get all usernames without current user
        for user in load_users():
            if user["username"] != current_username:
                self.file_viewers_list.addItem(user["username"])
                self.file_editors_list.addItem(user["username"])

        self.new_file_btn = QPushButton("Create a file")

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

        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.on_right_click_to_file_name)
        
    def on_right_click_to_file_name(self, position):
        item = self.file_list.itemAt(position)
        if item:
            # Or show a context menu if needed:
            menu = QMenu()
            open_action = menu.addAction("Open File")
            action = menu.exec_(self.file_list.viewport().mapToGlobal(position))
            if action == open_action:
                self.join_file(item)

    def open_editor_window(self, filename, content, isViewer=False):
        # Eğer dosya zaten açıksa, mevcut pencereyi göster ve odakla
        if filename in self.open_editors:
            editor = self.open_editors[filename]
            editor.activateWindow()
            editor.raise_()
            return
        
        editor = EditorWindow(self.sock, self.session, filename=filename, parent=self)
        editor.text_edit.setText(content)

        if isViewer:
            editor.text_edit.setReadOnly(True)

        editor.show()
        self.open_editors[filename] = editor

    def create_file(self):
        name = self.new_file_input.text().strip()
        
        selected_viewers = [item.text() for item in self.file_viewers_list.selectedItems()]
        selected_editors = [item.text() for item in self.file_editors_list.selectedItems()]

        # Get the logged user for ownership
        owner_username = self.session.get_user()

        if name:
            msg = {"cmd": MSG_CREATE_FILE, "filename": name, "owner": owner_username, "viewers": selected_viewers, "editors": selected_editors}
            send_json(self.sock, msg)

    def join_file(self, item):
        filename = item.text()
        msg = {"cmd": MSG_JOIN_FILE, "filename": filename}
        send_json(self.sock, msg)

    def handle_server_message(self, msg: dict):
        if msg.get("cmd") == MSG_FILE_LIST:
            self.file_list.clear()
            for f in msg.get("files", []):
                self.file_list.addItem(f)

        elif msg.get("cmd") in [MSG_FILE_LOAD, MSG_FILE_LOAD_VIEWER]:
            filename = msg.get("filename", "[dosya]")
            content = msg.get("content", "")
            is_viewer = msg.get("cmd") == MSG_FILE_LOAD_VIEWER
            self.open_editor_signal.emit(filename, content, is_viewer)

        elif msg.get("cmd") == MSG_ERROR:
            QMessageBox.critical(self, "Hata", msg.get("message", "Bir hata oluştu."))
