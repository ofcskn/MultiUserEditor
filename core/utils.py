import hashlib
import os
import json
import datetime
import random
import re
import string

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def ensure_folder_exists(path):
    """Checks if the folder exists, and creates it if not."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ Folder created: {path}")
    else:
        print(f"📂 Folder already exists: {path}")

def send_json(sock, data):
    try:
        message = json.dumps(data).encode()
        sock.sendall(message)
    except Exception as e:
        print(f"[ERROR] Failed to send data: {e}")

def recv_json(sock):
    try:
        data = sock.recv(4096)
        return json.loads(data.decode())
    except (ConnectionError, json.JSONDecodeError) as e:
        print(f"[RECEIVE ERROR] {e}")
        return None 

    except Exception as e:
        print(f"[RECEIVE UNEXPECTED ERROR] {e}")
        return None

def sanitize_filename(filename: str) -> str:
    return re.sub(r'[^A-Za-z0-9._-]', '_', filename)

def generate_unique_filename(owner_username: str, filename: str) -> str:
    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    safe_filename = sanitize_filename(filename)

    unique_filename = f"{owner_username}-{safe_filename}-{now}-{random_part}"
    return unique_filename