import os

# Client Message types
MSG_CLIENT_LOGIN = "MSG_CLIENT_LOGIN"                       # Login
MSG_CLIENT_UPDATE_FILE = "MSG_CLIENT_UPDATE_FILE"           # File update
MSG_CLIENT_LIST_FILES = "MSG_CLIENT_LIST_FILES"                   # List of shared files
MSG_CLIENT_CREATE_FILE = "MSG_CLIENT_CREATE_FILE"           # Request to create a new file
MSG_CLIENT_JOIN_FILE = "MSG_CLIENT_JOIN_FILE"               # User joined the file

# Server Message types
MSG_SERVER_LOAD_FILE = "MSG_SERVER_LOAD_FILE"                    # Load file from the server
MSG_SERVER_CREATE_FILE_FAILURE = "MSG_SERVER_CREATE_FILE_FAILURE" # If an error occurs when a file is created
MSG_SERVER_LOAD_FILE_VIEWER = "MSG_SERVER_LOAD_FILE_VIEWER"      # Load file as read-only/viewer
MSG_SERVER_PERMISSION_FAILURE = "MSG_SERVER_PERMISSION_FAILURE" # Permission failure
MSG_SERVER_LOGIN_FAILURE = "MSG_CLIENT_LOGIN_FAILURE"           # Login error
MSG_SERVER_FAILURE = "MSG_SERVER_FAILURE"                       # General server error
MSG_SERVER_SUCCESS = "MSG_SERVER_SUCCESS"                   # General server success
MSG_SERVER_UPDATE_FILE_SUCCESS = "MSG_SERVER_UPDATE_FILE_SUCCESS" # If an error does not occurs when a file is updated
MSG_SERVER_UPDATE_FILE_FAILURE = "MSG_SERVER_UPDATE_FILE_FAILURE" # If an error occurs when a file is updated
MSG_SERVER_USER_ACTIVE_SESSION = "MSG_SERVER_USER_ACTIVE_SESSION" # If there is an active client with an username
MSG_SERVER_REDIRECT_TO_FILES_VIEW = "MSG_SERVER_REDIRECT_TO_FILES_VIEW" # Redirect to files 
MSG_SERVER_UPDATE_LISTED_FILES = "MSG_SERVER_UPDATE_LISTED_FILES" # Update the listed files
MSG_SERVER_CREATE_USER = "MSG_SERVER_CREATE_USER" # Create a new user

HOST = '127.0.0.1'
PORT = 65433

DATA_FOLDER = 'data'
SAVE_FOLDER = 'files'

USERS_JSON = os.path.join(DATA_FOLDER, 'users.json')
FILES_JSON = os.path.join(DATA_FOLDER, 'files.json')