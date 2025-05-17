import os
from PySide6.QtWidgets import (QMainWindow)
from client.views.editor_view import EditorWindow
from client.views.file_selector_view import FileSelector
from client.views.login_view import LoginWindow

class MainApp(QMainWindow):
    def __init__(self, sock, session, receiver):
        super().__init__()
        self.sock = sock
        self.session = session
        self.receiver = receiver
        self.current_view = None
        self.showMaximized()
        self.show_login()

 
    def updateAlert(self, text):
        print("The alert is updated", text)      

    def show_login(self):
        # Disconnect old view if exists
        if self.current_view:
            try:
                self.receiver.message_received.disconnect(self.current_view.handle_server_message)
            except TypeError:
                pass  # already disconnected or was never connected

        self.current_view = LoginWindow(self.sock, self.session, self.receiver, self)
        self.setWindowTitle("Login or Register")
        self.setCentralWidget(self.current_view)

        # Connect new view
        self.receiver.message_received.connect(self.current_view.handle_server_message)

    def show_selector(self, files):
        if self.current_view:
            try:
                self.receiver.message_received.disconnect(self.current_view.handle_server_message)
            except TypeError:
                pass  # already disconnected or was never connected

        self.current_view = FileSelector(self.sock, self.session, self.receiver, self)
        self.setWindowTitle("File Selector")
        self.setCentralWidget(self.current_view)

        # Connect new view to receiver
        self.receiver.message_received.connect(self.current_view.handle_server_message)

        # Load initial file list
        self.current_view.load_files(files)

    def show_editor(self, filename, content, fileSelector, isViewer=False):
        # If the file is already open, close and remove it
        if any(fileSelector.open_editors):
            fileSelector.open_editors = {}
            self.current_view.close()  # Triggers closeEvent automatically

        # Create new editor window passing all required references
        self.current_view = EditorWindow(
            self.sock,
            self.session,
            self.receiver,
            self,
            filename=filename,
            parent=fileSelector
        )
        self.setWindowTitle("Editor Page")

        # Set the content of the editor
        self.current_view.text_edit.setText(content)

        # If user is a viewer, set editor to read-only
        if isViewer:
            self.current_view.text_edit.setReadOnly(True)

        self.receiver.message_received.connect(self.current_view.route_message_to_editors)

        fileSelector.open_editors[filename] = self.current_view

        # Show the editor window and track it
        self.current_view.show()