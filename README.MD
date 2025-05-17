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

## 🗂️ Project Structure

```

MultiUserEditor/
│
├── run.py # Unified launcher for client and server
├── files/ # Shared editable files
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

```

## 🔧 Requirements

- Python 3.9+
- PySide6
- (No external server or database required)

## 🔧 Create a virtual environment and install dependencies

- Create a virtual environment:

- For Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

- For Windows:

```bash
python -m venv .venv
.venv/Scripts/activate
```

- Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the App

### Option 1: Full App (Server + Client)

- Run both server and client with one command:

```bash
python main.py
```

### Option 2: Manual Mode (Separate Terminals)

- Run the server:

```bash
python run_server.py
```

- In another terminal, run the client:

```bash
python run_client.py
```

## Build

- Check the pyinstaller is installed:

```bash
pip install pyinstaller
```

```bash
pyinstaller --noconfirm --clean --windowed main.py
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
    "last_modified": "2025-05-14T12:00:00"
  }
]
```

# 📚 Future Improvements

- ✅ Password encryption
- 🔁 Live synchronization with document diffing
- 🔒 Role-based access control

# PROTOCOL

[Protocol-Turkish](protocols/PROTOCOL_TR.MD)
[Protocol-English](protocols/PROTOCOL_EN.MD)

# 👨‍💻 Author

Ömer Faruk COŞKUN (@ofcskn)
