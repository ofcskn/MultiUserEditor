

def broadcast_update(clients, filename, message, exclude_sock=None):
    """Broadcasts a file update to all connected clients except the sender."""
    for client, info in clients.items():
        if info.get('file') == filename and client != exclude_sock:
            try:
                client.sendall(message.encode())
            except:
                continue
