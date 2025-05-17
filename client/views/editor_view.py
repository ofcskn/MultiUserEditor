import os
from client.views.layout_view import BaseWindow
from core.constants import MSG_SERVER_FAILURE, MSG_CLIENT_UPDATE_FILE, MSG_SERVER_UPDATE_FILE_SUCCESS
import threading
import json
from PySide6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QToolBar)
from PySide6.QtGui import QTextCharFormat, QFont, QAction
from PySide6.QtCore import Signal, QObject

from core.utils import send_json

class Communicator(QObject):
    update_signal = Signal(str)

class EditorWindow(BaseWindow):  # Inherits BaseWindow, not QMainWindow
    def __init__(self, sock, session, receiver, controller, filename, parent=None):
        super().__init__(sock, session, receiver, controller)
        self.parent_selector = parent 
        self.filename = filename
        
        self.extension = os.path.splitext(self.filename)[1] 

        username = self.session.get_user()
        self.setWindowTitle(f"{username} - Düzenleniyor: {filename}")

        # --- Components ---
        self.comm = Communicator()
        self.comm.update_signal.connect(self.apply_update)

        self.text_edit = QTextEdit()

        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save_file)

        # --- Layout ---
        self.layout = QVBoxLayout()
        if self.extension == ".html":
            self.toolbar = QToolBar()
            self.init_toolbar()
            self.layout.addWidget(self.toolbar)

        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.save_button)

        # Final widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setLayout(self.layout)  # For QWidget (not QMainWindow)

        self.text_edit.textChanged.connect(self.save_file)

    def init_toolbar(self):
        bold_action = QAction("Bold", self)
        bold_action.triggered.connect(self.set_bold)
        self.toolbar.addAction(bold_action)

        italic_action = QAction("Italic", self)
        italic_action.triggered.connect(self.set_italic)
        self.toolbar.addAction(italic_action)

        underline_action = QAction("Underline", self)
        underline_action.triggered.connect(self.set_underline)
        self.toolbar.addAction(underline_action)

    def set_bold(self):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            cursor.mergeCharFormat(self.get_bold_format())
        else:
            cursor.insertText("Bold")

    def set_italic(self):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            cursor.mergeCharFormat(self.get_italic_format())
        else:
            cursor.insertText("Italic")

    def set_underline(self):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            cursor.mergeCharFormat(self.get_underline_format())
        else:
            cursor.insertText("Underlined")

    def get_bold_format(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold)
        return fmt

    def get_italic_format(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(True)
        return fmt

    def get_underline_format(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(True)
        return fmt

    def save_file(self):
        if self.extension == ".html":
            content = self.text_edit.toHtml()
        else:
            content = self.text_edit.toPlainText()

        msg = {"cmd": MSG_CLIENT_UPDATE_FILE, "filename": self.filename, "content": content}
        send_json(self.sock, msg)

    def closeEvent(self, event):
        if self.parent_selector:
            self.parent_selector.open_editors.pop(self.filename, None)
        super().closeEvent(event)

    def route_message_to_editors(self, msg):
        filename = msg.get("filename")
        editor = self.parent_selector.open_editors.get(filename)
        
        if editor and editor.isVisible():
            editor.handle_server_message(msg)

    def apply_update(self, content):
        self.text_edit.blockSignals(True)
        if self.extension == ".html":
            self.text_edit.setHtml(content)
        else:
            self.text_edit.setPlainText(content)
        self.text_edit.blockSignals(False)

    def handle_server_message(self, msg):
        try:
            cmd = msg.get("cmd")
            if cmd == MSG_CLIENT_UPDATE_FILE:
                content = msg.get("content", "")
                self.comm.update_signal.emit(content)
            elif cmd == MSG_SERVER_UPDATE_FILE_SUCCESS:
                print("File update was successful.")
            elif cmd == MSG_SERVER_FAILURE:
                error_msg = msg.get("message", "An error occurred.")
                print(f"Server Error: {error_msg}")
        except Exception as e:
            print(f"[Client] Error while handling message: {e}")