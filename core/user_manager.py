import os
import json
from core.constants import USERS_JSON
from core.utils import hash_password

def load_users():
    """Loads all users from users.json."""
    if not os.path.exists(USERS_JSON):
        return []
    with open(USERS_JSON, 'r') as f:
        return json.load(f)

def save_user(username, password):
    """Saves a new user to the users.json file."""
    users = load_users()
    if not any(u['username'] == username for u in users):
        users.append({"username": username, "password": hash_password(password)})
        with open(USERS_JSON, 'w') as f:
            json.dump(users, f, indent=4)

def validate_user(username, password):
    """Validates if the user exists and the password matches."""
    users = load_users()
    user = next((u for u in users if u['username'] == username), None)
    if user and user['password'] == hash_password(password):
        return True
    return False

def isValidUser(username):
    """
    Checks if the given username is NOT present in users.json.
    Returns True if the username is not found, or if the file doesn't exist or is invalid.
    """
    if not os.path.exists("users.json"):
        return True  # File doesn't exist, treat user as invalid

    try:
        with open("users.json", "r", encoding="utf-8") as f:
            users = json.load(f)

        # Check if username exists in any user dict
        for user in users:
            if user.get("username") == username:
                return True  # Valid user found

        return False  # Username not found

    except (json.JSONDecodeError, IOError, TypeError):
        return False  # Error in reading/parsing the file → invalid user

def user_can_edit(username, file_metadata):
    return username == file_metadata.get("owner") or username in file_metadata.get("editors", [])

def user_can_view(username, file_metadata):
    return username == file_metadata.get("owner") or username in file_metadata.get("viewers", []) or username in file_metadata.get("editors", [])