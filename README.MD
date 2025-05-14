# 📝 MultiUserEditor

**MultiUserEditor** is a real-time collaborative text editor built with **Python**, **PySide6** for GUI, and **sockets** for client-server communication. Multiple users can log in, view available files, edit content collaboratively, and see changes reflected in real time.

---

## 🚀 Features

- 🧑‍🤝‍🧑 Multi-user login system
- 📄 Shared file listing and management
- ✍️ Real-time collaborative editing (text/RTF)
- 🔐 Simple session control and file-based persistence
- ⚡ Socket-based custom protocol (no third-party server)
- 🌐 JSON-based lightweight database

---

## 🗂️ Project Structure

MultiUserEditor/
│
├── run.py # Unified launcher for client and server
├── www/files/ # Shared editable files
├── data/ # JSON-based storage
│ ├── users.json
│ └── files.json
│
├── client/ # PySide6 GUI client
│ ├── client.py # Entry point (exposed as start_client())
│ ├── views/ # Login, file list, editor windows
│ ├── controllers/ # Business logic and event handlers
│ ├── models/ # Optional: user/file models
│ └── session.py # Tracks client-side state
│
├── server/ # Socket server components
│ ├── server.py # Entry point (exposed as start_server())
│ ├── handler.py # Request handler
│ ├── broadcast.py # Broadcasts updates to all clients
│ └── session.py # Tracks connected clients
│
├── core/ # Shared logic
│ ├── constants.py # Configurations, socket commands, etc.
│ ├── user_manager.py # User login, creation, validation
│ ├── file_manager.py # File metadata and access logic
│ └── utils.py # Utility functions
│
├── requirements.txt # Python dependencies
├── .gitignore # Files to ignore in Git
└── README.md # This file

---

## 🔧 Requirements

- Python 3.9+
- PySide6
- (No external server or database required)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the App

### Option 1: Full App (Server + Client)

- Run both server and client with one command:

```bash
python run.py
```

### Option 2: Manual Mode (Separate Terminals)

- Run the server:

```bash
python server/server.py
```

- In another terminal, run the client:

```bash
python client/client.py
```

## 🧪 JSON Database Example

### data/users.json

```bash
[
  {
    "username": "admin",
    "password": "€âß123123asdasd#",
  }
]
```

### data/files.json

```bash
[
  {
    "filename": "notes.txt",
    "owner": "admin",
    "editors": "user",
    "viewers": "user",
    "siz": 0,
    "last_modified": "2025-05-14T12:00:00"
  }
]
```

# 📚 Future Improvements

- ✅ Password encryption
- 🔁 Live synchronization with document diffing
- 🔒 Role-based access control

# 👨‍💻 Author

Ömer Faruk COŞKUN (@ofcskn)

# VERSIONS

## VERSION 1.0 ROADMAP

1. Create a basic socket server and client.
2. Use PySide6 for GUI.
3. Add JSON databases for user and file management.
4. Add permission management for users.
5. Refactor the code.
