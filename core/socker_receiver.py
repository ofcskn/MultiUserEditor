from PySide6.QtCore import QThread, Signal
from core.utils import recv_json

class SocketReceiver(QThread):
    # Signal to notify that a message has been received
    message_received = Signal(dict)

    def __init__(self, sock, parent=None):
        super().__init__(parent)
        self.sock = sock
        self.running = True
        self._target = None

    def set_target(self, target):
        self._target = target

    def run(self):
        while self.running:
            try:
                msg = recv_json(self.sock)  # Blocking call to receive data
                if msg:
                    self.message_received.emit(msg)  # Emit signal to notify the message has been received
            except Exception as e:
                print(f"[SocketReceiver] Error: {e}")
                break

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
