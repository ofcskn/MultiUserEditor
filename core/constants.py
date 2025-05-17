import os

# Message types
MSG_LOGIN = "LOGIN"                       # Login
MSG_FILE_UPDATE = "FILE_UPDATE"           # File update
MSG_FILE_LIST = "FILES"                   # List of shared files
MSG_CREATE_FILE = "CREATE_FILE"           # Request to create a new file
MSG_CREATE_FILE_ERROR = "CREATE_FILE_ERROR" # If an error occurs when a file is created
MSG_FILE_LOAD = "LOAD"                    # Load file
MSG_FILE_LOAD_VIEWER = "LOAD_VIEWER"      # Load file as read-only/viewer
MSG_JOIN_FILE = "JOIN_FILE"               # User joined the file
MSG_ERROR = "ERROR"                       # General error
MSG_PERMISSION_ERROR = "PERMISSION_ERROR" # Permission error
MSG_LOGIN_ERROR = "LOGIN_ERROR"           # Login error
MSG_SUCCESS = "SUCCESS"                   # Successful action
MSG_FILE_UPDATE_SUCCESS = "FILE_UPDATE_SUCCESS" # If an error does not occurs when a file is updated
MSG_FILE_UPDATE_ERROR = "FILE_UPDATE_ERROR" # If an error occurs when a file is updated
MSG_USER_ACTIVE_SESSION = "USER_ACTIVE_SESSION" # If there is an active client with an username
MSG_FILES_PAGE_REDIRECT = "FILES_PAGE_REDIRECT" # Redirect to files 
MSG_FILE_LIST_UPDATE = "FILE_LIST_UPDATE" # Update the file list

HOST = '127.0.0.1'
PORT = 65433

DATA_FOLDER = 'data'
SAVE_FOLDER = 'files'

USERS_JSON = os.path.join(DATA_FOLDER, 'users.json')
FILES_JSON = os.path.join(DATA_FOLDER, 'files.json')
