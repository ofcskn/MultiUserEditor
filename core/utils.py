import hashlib
import os

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def ensure_folder_exists(path):
    """Checks if the folder exists, and creates it if not."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ Folder created: {path}")
    else:
        print(f"📂 Folder already exists: {path}")