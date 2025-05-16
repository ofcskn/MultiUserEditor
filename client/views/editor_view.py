from client.views.layout_view import BaseWindow
from core.constants import MSG_ERROR, MSG_FILE_UPDATE, MSG_FILE_UPDATE_SUCCESS
import threading
import json
from PySide6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QToolBar)
from PySide6.QtGui import QTextCharFormat, QFont, QAction
from PySide6.QtCore import Signal, QObject

from core.utils import send_json, recv_json

class Communicator(QObject):
    update_signal = Signal(str)

class EditorWindow(BaseWindow):
    def __init__(self, sock, session, filename, parent=None):
        super().__init__(sock, session, parent)
        self.parent_selector = parent 
        self.filename = filename

        # Get username from the session
        username = self.session.get_user()

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

        self.text_edit.textChanged.connect(self.save_file)
        self.comm = Communicator()
        self.comm.update_signal.connect(self.apply_update)

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
        send_json(self.sock, msg)

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

    def handle_server_message(self, msg: dict):
        """
        Handle a single message received from the server.
        """
        try:
            cmd = msg.get("cmd")

            if cmd == MSG_FILE_UPDATE:
                content = msg.get("content", "")
                self.comm.update_signal.emit(content)

            elif cmd == MSG_FILE_UPDATE_SUCCESS:
                print("File update was successful.")
                # Optionally emit a signal to stop a loading spinner here

            elif cmd == MSG_ERROR:
                error_msg = msg.get("message", "An error occurred.")
                print(f"Server Error: {error_msg}")
                # Optionally emit a signal to show this in a QMessageBox

        except Exception as e:
            print(f"[Client] Error while handling message: {e}")