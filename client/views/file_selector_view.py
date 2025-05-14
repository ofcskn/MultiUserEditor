import threading
import json
from PySide6.QtWidgets import (QMenu, QLineEdit, QPushButton, QVBoxLayout, QWidget, QListWidget, QMessageBox, QLabel, QAbstractItemView)
from PySide6.QtCore import Signal
from client.views.layout_view import BaseWindow
from core.constants import MSG_CREATE_FILE, MSG_ERROR, MSG_FILE_LIST, MSG_FILE_LOAD_VIEWER, MSG_JOIN_FILE, MSG_FILE_LOAD
from client.session import AppSession
from core.user_manager import load_users
from client.views.editor_view import EditorWindow
from PySide6.QtCore import Qt
from core.utils import send_json, recv_json

class FileSelector(BaseWindow):
    open_editor_signal = Signal(str, str, AppSession, bool)  # filename, content, AppSession, isViewed
    def __init__(self, sock, session):
        super().__init__()
        self.sock = sock
        self.session = session

        # Get username from the session
        current_username = session.get_user()

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

        threading.Thread(target=self.listen_server, daemon=True).start()

    def on_right_click_to_file_name(self, position):
        item = self.file_list.itemAt(position)
        if item:
            # Or show a context menu if needed:
            menu = QMenu()
            open_action = menu.addAction("Open File")
            action = menu.exec_(self.file_list.viewport().mapToGlobal(position))
            if action == open_action:
                self.join_file(item)


    def open_editor_window(self, filename, content, session, isViewer=False):
        # Eğer dosya zaten açıksa, mevcut pencereyi göster ve odakla
        if filename in self.open_editors:
            editor = self.open_editors[filename]
            editor.activateWindow()
            editor.raise_()
            return
        
        editor = EditorWindow(self.sock, filename=filename, session=session, parent=self)
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

    def listen_server(self):
        while True:
            try:
                msg = recv_json(self.sock)
                if not msg:
                    break
                if msg.get("cmd") == MSG_FILE_LIST:
                    self.file_list.clear()
                    for f in msg.get("files", []):
                        self.file_list.addItem(f)
                elif msg.get("cmd") == MSG_FILE_LOAD or msg.get("cmd") == MSG_FILE_LOAD_VIEWER:
                    filename = msg.get("filename", "[dosya]")
                    self.open_editor_signal.emit(filename, msg.get("content", ""), self.session, True if msg.get("cmd") == MSG_FILE_LOAD_VIEWER else False)
                # elif msg.get("cmd") == MSG_PERMISSION_ERROR:
                #     QMessageBox.critical(self, "Hata", msg.get("message", "An permission error occured."))
                elif msg.get("cmd") == MSG_ERROR:
                    QMessageBox.critical(self, "Hata", msg.get("message", "An error occured."))
            except Exception as e:
                print("Client Error:", e)
                break
