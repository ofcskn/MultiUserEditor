from PySide6.QtWidgets import (QMenu, QLineEdit, QPushButton, QVBoxLayout, QWidget, QListWidget, QMessageBox, QLabel, QAbstractItemView)
from PySide6.QtCore import Signal
from client.views.layout_view import BaseWindow
from core.constants import MSG_CLIENT_CREATE_FILE, MSG_SERVER_CREATE_FILE_FAILURE, MSG_SERVER_FAILURE, MSG_CLIENT_LIST_FILES, MSG_SERVER_UPDATE_LISTED_FILES, MSG_SERVER_LOAD_FILE_VIEWER, MSG_CLIENT_JOIN_FILE, MSG_SERVER_LOAD_FILE
from core.user_manager import load_users
from PySide6.QtCore import Qt
from core.utils import send_json
from PySide6.QtWidgets import QListWidgetItem

class FileSelector(BaseWindow):
    open_editor_signal = Signal(str, str, bool)  # filename, content, isViewed
    def __init__(self, sock, session, receiver, controller):
        super().__init__(sock, session, receiver, controller)
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

        # Create a select box to choose a file type 
        self.selected_extension = ".txt"  # Default extension
        self.file_extension_list_label = QLabel(f"Choose a file type")
        self.file_extension_list = QListWidget()
        self.file_extension_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Connect selection
        self.file_extension_list.itemClicked.connect(self.on_extension_selected)

        # Scrollable list for viewers
        self.viewers_list_label = QLabel(f"Viewers (choose)")
        self.file_viewers_list = QListWidget()
        self.file_viewers_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.file_viewers_list.setFixedHeight(50) 

        self.editors_list_label = QLabel(f"Editors (choose)")
        # Scrollable list for editors
        self.file_editors_list = QListWidget()
        self.file_editors_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.file_editors_list.setFixedHeight(50)  # adjust as needed

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

        self.layout.addWidget(self.file_extension_list_label)
        self.layout.addWidget(self.file_extension_list)

        # Add known file extensions
        known_extensions = [".py", ".txt", ".md", ".json", ".csv", ".html", ".xml", ".yaml", ".ini"]
        for ext in known_extensions:
            self.file_extension_list.addItem(ext)


        self.layout.addWidget(self.viewers_list_label)
        self.layout.addWidget(self.file_viewers_list)

        self.layout.addWidget(self.editors_list_label)
        self.layout.addWidget(self.file_editors_list)

        self.layout.addWidget(self.new_file_btn)

        self.new_file_btn.clicked.connect(self.create_file)
        self.file_list.itemDoubleClicked.connect(self.join_file)

        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.on_right_click_to_file_name)
        
        self.setLayout(self.layout)

    def on_extension_selected(self, item):
        self.selected_extension = item.text()

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
        self.controller.show_editor(filename, content, self, isViewer)

    def create_file(self):
        file_extension = self.selected_extension
        name = self.new_file_input.text().strip()
        
        selected_viewers = [item.text() for item in self.file_viewers_list.selectedItems()]
        selected_editors = [item.text() for item in self.file_editors_list.selectedItems()]

        # Get the logged user for ownership
        owner_username = self.session.get_user()

        if name:
            msg = {"cmd": MSG_CLIENT_CREATE_FILE, "filename": name, "owner": owner_username, "viewers": selected_viewers, "editors": selected_editors, "extension": file_extension}
            send_json(self.sock, msg)
        else:
            QMessageBox.critical(self, "Hata", "Please enter a filename.")

    def join_file(self, item):
        filename = item.text()
        msg = {"cmd": MSG_CLIENT_JOIN_FILE, "filename": filename}
        send_json(self.sock, msg)

    def handle_server_message(self, msg):
        if msg.get("cmd") == MSG_CLIENT_LIST_FILES:
            self.file_list.clear()
            for filename in msg.get("files", []):
                item = QListWidgetItem(filename)
                self.file_list.addItem(item)
        if msg.get("cmd") == MSG_SERVER_UPDATE_LISTED_FILES:
            self.file_list.addItem(msg.get("filename"))
        if msg.get("cmd") in [MSG_SERVER_LOAD_FILE, MSG_SERVER_LOAD_FILE_VIEWER]:
            filename = msg.get("filename")
            content = msg.get("content", "")
            is_viewer = msg.get("cmd") == MSG_SERVER_LOAD_FILE_VIEWER
            self.open_editor_signal.emit(filename, content, is_viewer)
        if msg.get("cmd") == MSG_SERVER_FAILURE:
            QMessageBox.critical(self, "Hata", msg.get("message", "An error occured.."))
        if msg.get("cmd") == MSG_SERVER_CREATE_FILE_FAILURE:
            QMessageBox.critical(self, "Hata", msg.get("message", "An error occured."))

    def load_files(self, files):
        self.file_list.clear()
        for filename in files:
            self.file_list.addItem(QListWidgetItem(filename))