import json
import threading
from core.utils import generate_unique_filename, get_filenames, recv_json, send_json
from server.broadcast import broadcast_update, broadcast_update_for_new_file
from core.user_manager import load_users, save_user, validate_user
from core.file_manager import get_permissions, load_filenames, load_files, add_file_metadata, read_file_content, save_file_content
from core.constants import MSG_SERVER_CREATE_FILE_FAILURE, MSG_SERVER_CREATE_USER, MSG_SERVER_UPDATE_LISTED_FILES, MSG_SERVER_LOAD_FILE, MSG_SERVER_LOAD_FILE_VIEWER, MSG_SERVER_UPDATE_FILE_FAILURE, MSG_SERVER_UPDATE_FILE_SUCCESS, MSG_SERVER_REDIRECT_TO_FILES_VIEW, MSG_CLIENT_LOGIN, MSG_CLIENT_CREATE_FILE, MSG_CLIENT_LIST_FILES, MSG_CLIENT_JOIN_FILE, MSG_CLIENT_UPDATE_FILE, MSG_SERVER_FAILURE, MSG_SERVER_LOGIN_FAILURE, MSG_SERVER_PERMISSION_FAILURE, MSG_SERVER_SUCCESS, MSG_SERVER_USER_ACTIVE_SESSION, SAVE_FOLDER
import os 

clients = {}  # {conn: {'username': ..., 'file': ...}}
client_files = {}

lock = threading.Lock()
files = []


def handle_update_file(conn, filename, new_content, username):
    if not filename or new_content is None:
        print("Invalid filename or content")
        send_json(conn, {"msg": MSG_SERVER_FAILURE, "content": "Invalid filename or content"})
        return

    permission = get_permissions(filename, username)
    if permission not in ("owner", "editor"):
        print("Permission denied for updating the file.")
        send_json(conn, {"cmd": MSG_SERVER_FAILURE, "payload": { "content": "Permission denied"}})
        return

    # Save to memory
    with lock:
        client_files[filename] = new_content
    
    # Save to disk
    file_path = os.path.join(SAVE_FOLDER, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        send_json(conn, {"cmd": MSG_SERVER_UPDATE_FILE_FAILURE, "payload": { "content": f"Failed to save file: {str(e)}"}})
        return

    # Confirm save to sender
    send_json(conn, {"cmd": MSG_SERVER_UPDATE_FILE_SUCCESS, "payload": { "content": "File updated", "filename": filename}})

    # Notify other users
    broadcast_update(clients, filename, {
        "cmd": MSG_CLIENT_UPDATE_FILE, "payload": { "content": new_content, "filename": filename }
    }, exclude_sock=conn)


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

                if cmd == MSG_CLIENT_LOGIN:
                    username = msg.get("payload", {}).get("username")
                    password = msg.get("payload", {}).get("password")
                    users = load_users()

                    # Save the user if there is no user with the username
                    if not any(user['username'] == username for user in users):
                        save_user(username, password)
                        send_json(conn, {
                            "cmd": MSG_SERVER_CREATE_USER,
                            "payload": {
                                "username": username,
                                "message": f"Your  is created: {username}."
                            }
                        })
                    
                    if validate_user(username, password):
                        if any(data['username'] == username for data in clients.values()):
                            send_json(conn, {
                                "cmd": MSG_SERVER_USER_ACTIVE_SESSION,
                                "payload": {
                                    "username": username,
                                    "message": f"There is a session for {username}."
                                }
                            })
                        else:
                            clients[conn] = {'username': username, 'file': None}
                            filenames = load_filenames(username) 
                            send_json(conn, {
                                "cmd": MSG_SERVER_REDIRECT_TO_FILES_VIEW,
                                "payload": {
                                    "files": filenames,
                                    "username": username
                                }
                            })
                    else:
                        print("Invalid credentials. Login is not successful.")
                        # send error response
                        send_json(conn, {
                            "cmd": MSG_SERVER_LOGIN_FAILURE, 
                            "payload": {
                                "message": "Invalid credentials. Login is not successful."
                            }
                        })
                elif cmd == MSG_CLIENT_CREATE_FILE:
                    owner = msg.get("payload", {}).get("owner")
                    filename = msg.get("payload", {}).get("filename")
                    extension = msg.get("payload", {}).get("extension")

                    if (filename == None or filename == "") or extension == None: 
                        send_json(conn, {"cmd": MSG_SERVER_CREATE_FILE_FAILURE, "payload": { "message": "The extension or filename is not valid."}})
 
                    # Create a new filename
                    new_filename = generate_unique_filename(owner, filename, extension)
                    viewers = msg.get("payload", {}).get("viewers", [])  # Ensure fallback to empty list
                    editors = msg.get("payload", {}).get("editors", [])
                    
                    with threading.Lock():
                        client_files[new_filename] = ""
                        # Save the file to the
                        save_file_content(new_filename, "")
                        add_file_metadata(new_filename, extension, owner, viewers, editors)

                    send_json(conn, {"cmd": MSG_SERVER_UPDATE_LISTED_FILES, "payload": { "filename": new_filename}})

                    broadcast_update_for_new_file(clients, new_filename, conn)

                elif cmd == MSG_CLIENT_JOIN_FILE:
                    filename = msg.get("payload", {}).get("filename")
                    username = clients[conn]['username']
                    clients[conn]['file'] = filename
                    content = read_file_content(filename)

                    # permission for the file 
                    permission_of_file = get_permissions(filename, username)
                    if permission_of_file == "owner" or permission_of_file == "editor":
                        send_json(conn, {
                            "cmd": MSG_SERVER_LOAD_FILE,
                            "payload": {
                                "content": content,
                                "filename": filename
                            }
                        })
                    elif permission_of_file == "viewer":
                        send_json(conn, {
                            "cmd": MSG_SERVER_LOAD_FILE_VIEWER,
                            "payload": {
                                "content": content,
                                "filename": filename
                            }
                            })
                    else:
                        print("The user has not permission to open the file.")
                        # send error response
                        send_json(conn, {
                            "cmd": MSG_SERVER_PERMISSION_FAILURE,
                            "payload": {
                                "message": "You do not have permission to open this file."
                            }
                        })

                elif cmd == MSG_CLIENT_UPDATE_FILE:
                    filename = clients[conn]['file']
                    username = clients[conn]['username']
                    content = msg.get("payload", {}).get("content")

                    # the permission to update
                    permission_of_file = get_permissions(filename, username)
                    if permission_of_file == "owner" or permission_of_file == "editor":
                        handle_update_file(conn, filename, content, username)
                    else:
                        print("The user has not permission to update the file.")
                        # send error response
                        send_json(conn, {
                            "cmd": MSG_SERVER_PERMISSION_FAILURE,
                            "payload": { 
                                "message": "You do not have permission to update this file."
                            }
                        })

            except json.JSONDecodeError as e:
                print("Failed to decode JSON:", e)
                return  # or handle the error gracefully  
                           
            except Exception as e:
                print("[-] Error:", e)
                break

    clients.pop(conn, None)
    print(f"[-] Disconnected {addr}")
