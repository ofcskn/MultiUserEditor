import os
import json
from datetime import datetime
from core.constants import FILES_JSON, SAVE_FOLDER
from core.user_manager import isValidUser

def read_file_content(filename):
    """Reads and returns the content of a single file by filename (with extension)."""
    filepath = os.path.join(SAVE_FOLDER, filename)
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {filename}:", str(e))
        return None

def load_files(username):
    """Loads all file contents from files.json that belong to the specified username (as owner)."""
    files = []
    try:
        if not isValidUser(username):
            return files

        with open(FILES_JSON, 'r', encoding='utf-8') as f:
            metadata_list = json.load(f)

            for meta in metadata_list:
                if meta.get('owner') == username:
                    filename = meta.get('filename')
                    filepath = os.path.join(SAVE_FOLDER, filename)

                    if os.path.exists(filepath):
                        with open(filepath, 'r', encoding='utf-8') as file:
                            content = file.read()
                            files.append({
                                "filename": filename,
                                "content": content,
                                "metadata": meta
                            })
    except Exception as e:
        print("There are no files on the server or an error occurred:", str(e))

    return files

def load_filenames(username):
    """Returns a list of filenames from files.json owned by the specified username."""
    filenames = []
    try:
        if not isValidUser(username):
            return filenames

        with open(FILES_JSON, 'r', encoding='utf-8') as f:
            metadata_list = json.load(f)

            for meta in metadata_list:
                if meta.get('owner') == username:
                    filename = meta.get('filename')
                    full_filename = filename
                    filenames.append(full_filename)
    except Exception as e:
        print("Error loading filenames:", str(e))

    return filenames

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


def add_file_metadata(filename, extension, owner, viewers=None, editors=None):
    """Adds a new file's metadata to files.json."""
    metadata = []
    if os.path.exists(FILES_JSON):
        with open(FILES_JSON, 'r') as f:
            try:
                metadata = json.load(f)
            except json.JSONDecodeError:
                print("Warning: files.json was invalid. Reinitializing.")
                metadata = []

    metadata.append({
        "filename": filename,
        "extension": extension,
        "create_date": datetime.now().isoformat(),
        "size": 0,
        "owner": owner,
        "viewers": viewers or [],
        "editors": editors or []
    })

    with open(FILES_JSON, 'w') as f:
        json.dump(metadata, f, indent=4)

def save_file_content(filename, content):
    """Saves the file content to the save folder."""
    with open(os.path.join(SAVE_FOLDER, filename), 'w', encoding='utf-8') as f:
        f.write(content)
