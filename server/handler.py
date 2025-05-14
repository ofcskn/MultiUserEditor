import json
import threading
from core.utils import generate_unique_filename, recv_json, send_json
from server.broadcast import broadcast_update
from core.user_manager import load_users, save_user, validate_user
from core.file_manager import load_files, add_file_metadata, save_file_content
from core.constants import FILES_JSON, MSG_FILE_LOAD, MSG_FILE_LOAD_VIEWER, MSG_FILE_UPDATE_ERROR, MSG_FILE_UPDATE_SUCCESS, MSG_LOGIN, MSG_CREATE_FILE, MSG_FILE_LIST, MSG_JOIN_FILE, MSG_FILE_UPDATE, MSG_ERROR, MSG_LOGIN_ERROR, MSG_PERMISSION_ERROR, MSG_SUCCESS, SAVE_FOLDER
import os 

clients = {}  # {conn: {'username': ..., 'file': ...}}
files = load_files()    # {filename: content}
lock = threading.Lock()

def get_permissions(filename, username):
    # Load permissions from files.json
    with open(FILES_JSON) as f:
        file_permissions = json.load(f)

    for entry in file_permissions:
        if entry['filename'] == filename:
            if username == entry['owner']:
                return 'owner'
            elif username in entry['editors']:
                return 'editor'
            elif username in entry['viewers']:
                return 'viewer'
    return None

def handle_update_file(conn, filename, new_content, username):
    if not filename or new_content is None:
        print("Invalid filename or content")
        send_json(conn, {"msg": MSG_ERROR, "content": "Invalid filename or content"})
        return

    permission = get_permissions(filename, username)
    if permission not in ("owner", "editor"):
        print("Permission denied for updating the file.")
        send_json(conn, {"cmd": MSG_ERROR, "content": "Permission denied"})
        return

    # Save to memory
    with lock:
        files[filename] = new_content
    
    # Save to disk
    file_path = os.path.join(SAVE_FOLDER, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        send_json(conn, {"cmd": MSG_FILE_UPDATE_ERROR, "content": f"Failed to save file: {str(e)}"})
        return

    # Confirm save to sender
    send_json(conn, {"cmd": MSG_FILE_UPDATE_SUCCESS, "content": "File updated"})

    # # Notify other users
    # broadcast_update(clients, filename, {
    #     "cmd": MSG_FILE_UPDATE,
    #     "content": new_content
    # }, exclude_sock=conn)

    # Notify other users
    broadcast_update(clients, filename, json.dumps({
        "cmd": MSG_FILE_UPDATE,
        "content": new_content
    }), exclude_sock=conn)


def handle_client(conn, addr):
    """Handles a client connection."""
    with conn:
        print(f"[+] Connected by {addr}")
        while True:
            msg = recv_json(conn)

            if not msg:
                print("No data received. Connection may be closed.")
                break
            
            try:
                cmd = msg.get("cmd")

                if cmd == MSG_LOGIN:
                    username = msg.get("username")
                    password = msg.get("password")
                    users = load_users()

                    # Save the user if there is no user with the username
                    if not (username in users):
                        save_user(username, password)

                    if validate_user(username, password):
                        clients[conn] = {'username': username, 'file': None}
                        send_json(conn, {
                            "cmd": MSG_FILE_LIST,
                            "files": list(files.keys()),
                            "username": username
                        })
                    else:
                        print("Invalid credentials. Login is not successful.")
                        # send error response
                        send_json(conn, {
                            "cmd": MSG_LOGIN_ERROR,
                            "message": "Invalid credentials. Login is not successful."
                        })

                elif cmd == MSG_CREATE_FILE:
                    owner = msg.get("owner")
                    filename = msg.get("filename")
                    # Create a new filename
                    filename = generate_unique_filename(owner, filename)
                    viewers = msg.get("viewers", [])  # Ensure fallback to empty list
                    editors = msg.get("editors", [])

                    # Save the file to the
                    save_file_content(filename, "")
                    
                    with threading.Lock():
                        files[filename] = ""
                        add_file_metadata(filename, owner, viewers, editors)

                    # send_json(conn, {"cmd": MSG_FILE_LIST, "files": list(files.keys())})
                    conn.sendall(json.dumps({"cmd": MSG_FILE_LIST, "files": list(files.keys())}).encode())

                    # broadcast update for MSG_FILE_LIST
                    for client in clients:
                        if client != conn:
                            try:
                                client.sendall(json.dumps({"cmd": MSG_FILE_LIST, "files": list(files.keys())}).encode())
                                # send_json(conn, {"cmd": MSG_FILE_LIST, "files": list(files.keys())})
                            except:
                                continue

                elif cmd == MSG_JOIN_FILE:
                    filename = msg.get("filename")
                    username = clients[conn]['username']
                    clients[conn]['file'] = filename
                    content = files.get(filename, "")

                    # permission for the file 
                    permission_of_file = get_permissions(filename, username)

                    if permission_of_file == "owner" or permission_of_file == "editor":
                        send_json(conn, {
                            "cmd": MSG_FILE_LOAD,
                            "content": content,
                            "filename": filename
                        })
                    elif permission_of_file == "viewer":
                            send_json(conn, {
                            "cmd": MSG_FILE_LOAD_VIEWER,
                            "content": content,
                            "filename": filename
                        })
                    else:
                        print("The user has not permission to open the file.")
                        # send error response
                        send_json(conn, {
                            "cmd": MSG_PERMISSION_ERROR,
                            "message": "You do not have permission to open this file."
                        })

                elif cmd == MSG_FILE_UPDATE:
                    filename = clients[conn]['file']
                    username = clients[conn]['username']
                    content = msg.get("content")

                    # the permission to update
                    permission_of_file = get_permissions(filename, username)
                    if permission_of_file == "owner" or permission_of_file == "editor":
                        handle_update_file(conn, filename, content, username)
                    else:
                        print("The user has not permission to update the file.")
                        # send error response
                        send_json(conn, {
                            "cmd": MSG_PERMISSION_ERROR,
                            "message": "You do not have permission to update this file."
                        })

            except json.JSONDecodeError as e:
                print("Failed to decode JSON:", e)
                return  # or handle the error gracefully  
                           
            except Exception as e:
                print("[-] Error:", e)
                break

    clients.pop(conn, None)
    print(f"[-] Disconnected {addr}")
