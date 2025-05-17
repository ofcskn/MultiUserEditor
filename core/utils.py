import hashlib
import os
import json
import datetime
import random
import re
import string
import struct

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
        # Pack the message length in 4 bytes (big-endian)
        length = struct.pack('>I', len(message))
        sock.sendall(length + message)
    except Exception as e:
        print(f"[ERROR] Failed to send data: {e}")

def recv_json(sock):
    try:
        # First, read the 4-byte message length
        raw_length = recvall(sock, 4)
        if not raw_length:
            return None
        message_length = struct.unpack('>I', raw_length)[0]

        # Then read the actual message
        message = recvall(sock, message_length)
        if not message:
            return None
        return json.loads(message.decode())
    except (ConnectionError, json.JSONDecodeError) as e:
        print(f"[RECEIVE ERROR] {e}")
        return None
    except Exception as e:
        print(f"[RECEIVE UNEXPECTED ERROR] {e}")
        return None

def recvall(sock, n):
    """Helper function to receive exactly n bytes or return None."""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def sanitize_filename(filename: str) -> str:
    return re.sub(r'[^A-Za-z0-9._-]', '_', filename)

def generate_unique_filename(owner_username: str, filename: str, extension: str) -> str:
    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    safe_filename = sanitize_filename(filename)

    unique_filename = f"{safe_filename}-{now}-{owner_username}{extension}"
    return unique_filename

def get_filenames(files):
    return [file.get("filename") for file in files if "filename" in file]