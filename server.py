import socket
import threading
from constants import FILES_JSON, HOST, PORT, SAVE_FOLDER, SAVE_INTERVAL, USERS_JSON
from file_manager import load_files
from handler import handle_client
import json
import os 

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("[+] Server listening...")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    # If the files.json is not valid, save it 
    if not os.path.exists(FILES_JSON) or os.stat(FILES_JSON).st_size == 0:
        with open(FILES_JSON, 'w') as f:
            json.dump([], f)

    # If the users.json is not valid, save it 
    if not os.path.exists(USERS_JSON) or os.stat(USERS_JSON).st_size == 0:
        with open(USERS_JSON, 'w') as f:
            json.dump([], f)

    main()