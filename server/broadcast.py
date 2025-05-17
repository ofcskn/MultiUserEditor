

import json
from core.constants import FILES_JSON, MSG_FILE_LIST_UPDATE
from core.file_manager import get_permissions
from core.utils import send_json


def broadcast_update(clients, filename, message, exclude_sock=None):
    """Broadcasts a file update to all connected clients except the sender."""
    for client, info in clients.items():
        if info.get('file') == filename and client != exclude_sock:
            try:
                client.sendall(message.encode())
            except:
                continue

def broadcast_update_for_new_file(clients, filename, exclude_sock=None):
    """
    Notify all users who were granted permission (edit/view) for a *newly created file*
    so they can refresh their file list.
    
    Parameters:
    - clients: dict of {socket: {"username": str}}
    - filename: str (e.g., "example.txt")
    - exclude_sock: socket (the creator's socket, not to be notified)
    """
    try:
        with open(FILES_JSON, 'r', encoding='utf-8') as f:
            file_data = json.load(f)

        target_file = next((f for f in file_data if f["filename"] == filename), None)

        if not target_file:
            return

        affected_users = set(target_file.get("editors", []) + target_file.get("viewers", []))
        for client_sock, client_info in clients.items():
            if client_sock == exclude_sock:
                continue

            username = client_info.get("username")
            if username in affected_users:
                try:
                    send_json(client_sock, {"cmd": MSG_FILE_LIST_UPDATE, "filename": filename})
                except Exception as e:
                    print(f"Failed to notify {username} about new file: {e}")

    except Exception as e:
        print(f"broadcast_update_for_new_file error: {e}")
