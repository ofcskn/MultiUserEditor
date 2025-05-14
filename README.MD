# MULTI USER EDITOR

## FILE STRUCTURE

MultiUserEditor/
│
├──.venv/ # Python virtual environment
├── www/files/
├── data/ # JSON database
│ └── files.json # Files table
│ └── users.json # Users table
├── .gitignore # Ignored .git files
├── broadcast.py
├── client.py # PySide6 client
├── constants.py
├── file_manager.py
├── handler.py
└── requirements.txt # Required modules
└── README.md
└── server.py # Socket server
└── session.py # Session server
└── user_manager.py # User manage actions
└── utils.py # Utilities

# VERSIONS

## VERSION 1.0 ROADMAP

1. Create a basic socket server and client.
2. Use PySide6 for GUI.
3. Add JSON databases for user and file management.
4. Add permission management for users.
5. Refactor the code.
