import socket
import threading
from core.constants import DATA_FOLDER, FILES_JSON, HOST, PORT, SAVE_FOLDER, USERS_JSON
from server.handler import handle_client
import json
import os
from core.utils import ensure_folder_exists 

def start_server():
    # If the files.json is not valid, save it 
    if not os.path.exists(FILES_JSON) or os.stat(FILES_JSON).st_size == 0:
        with open(FILES_JSON, 'w') as f:
            json.dump([], f)

    # If the users.json is not valid, save it 
    if not os.path.exists(USERS_JSON) or os.stat(USERS_JSON).st_size == 0:
        with open(USERS_JSON, 'w') as f:
            json.dump([], f)

    ensure_folder_exists(DATA_FOLDER)
    ensure_folder_exists(SAVE_FOLDER)

    try:
        # Start a socket for a client
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            print("[+] Server listening...")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    except OSError as e:
        if e.errno == 98:  # Address already in use
            print("Error: Address already in use. Please try a different port.")
        else:
            print(f"An error occurred: {e}")
