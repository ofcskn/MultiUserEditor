import json
from datetime import datetime
from constants import FILES_JSON, SAVE_FOLDER
import os

def load_files():
    """Loads all file metadata from files.json."""
    files = {}
    try:
        if os.path.exists(FILES_JSON):
            with open(FILES_JSON, 'r') as f:
                metadata_list = json.load(f)
                for meta in metadata_list:
                    filename = meta['filename']
                    filepath = os.path.join(SAVE_FOLDER, filename)
                    if os.path.exists(filepath):
                        with open(filepath, 'r', encoding='utf-8') as file:
                            files[filename] = file.read()
    except:
        print("There is no files in the server..")
    return files

def add_file_metadata(filename, owner, viewers=None, editors=None):
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
        "extension": os.path.splitext(filename)[1],
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
