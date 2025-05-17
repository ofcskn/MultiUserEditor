# English Protocol Document

**Client-Server Communication Protocol**

---

## 1. General Description of the Protocol

This protocol is designed for file sharing, editing, and user management between the client and server.
Its purpose is to allow correct message exchanges without either side needing to understand the other's internal implementation.
Messages are exchanged using predefined message types and structured content.
Each message has a specific meaning and defines the action to be taken by the receiving side.

---

## 2. Message Types and Descriptions

| Message Type                        | Sender | Description                                              |
| ----------------------------------- | ------ | -------------------------------------------------------- |
| `MSG_CLIENT_LOGIN`                  | Client | User login request                                       |
| `MSG_CLIENT_UPDATE_FILE`            | Client | Client sends file content updates to the server          |
| `MSG_CLIENT_LIST_FILES`             | Client | Request to retrieve the list of shared files             |
| `MSG_CLIENT_CREATE_FILE`            | Client | Request to create a new file                             |
| `MSG_CLIENT_JOIN_FILE`              | Client | Request to join a file for editing                       |
| `MSG_SERVER_LOAD_FILE`              | Server | Server sends the file content to the client              |
| `MSG_SERVER_CREATE_FILE_FAILURE`    | Server | Error occurred while creating a file                     |
| `MSG_SERVER_LOAD_FILE_VIEWER`       | Server | Server sends the file in read-only (viewer) mode         |
| `MSG_SERVER_PERMISSION_FAILURE`     | Server | Permission error message                                 |
| `MSG_SERVER_LOGIN_FAILURE`          | Server | Login failed message                                     |
| `MSG_SERVER_FAILURE`                | Server | General server error                                     |
| `MSG_SERVER_SUCCESS`                | Server | General successful operation message                     |
| `MSG_SERVER_UPDATE_FILE_SUCCESS`    | Server | File update was successful                               |
| `MSG_SERVER_UPDATE_FILE_FAILURE`    | Server | Error occurred during file update                        |
| `MSG_SERVER_USER_ACTIVE_SESSION`    | Server | An active session already exists with the given username |
| `MSG_SERVER_REDIRECT_TO_FILES_VIEW` | Server | Redirect client to the file list view                    |
| `MSG_SERVER_UPDATE_LISTED_FILES`    | Server | Update the displayed file list                           |

---

## 3. Protocol Flow

### 3.1. User Login

| State               | Client Message     | Server Message                                                    | Description                              |
| ------------------- | ------------------ | ----------------------------------------------------------------- | ---------------------------------------- |
| User attempts login | `MSG_CLIENT_LOGIN` | `MSG_SERVER_REDIRECT_TO_FILES_VIEW` or `MSG_SERVER_LOGIN_FAILURE` | Username/password is sent and validated  |
| User does not exist | `MSG_CLIENT_LOGIN` | `MSG_SERVER_CREATE_USER` (if supported)                           | New user created and login is successful |
| Incorrect password  | `MSG_CLIENT_LOGIN` | `MSG_SERVER_LOGIN_FAILURE`                                        | Login rejected with error message        |
| User already active | `MSG_CLIENT_LOGIN` | `MSG_SERVER_USER_ACTIVE_SESSION`                                  | Login denied due to active session       |

---

### 3.2. File Listing and Management

| State             | Client Message           | Server Message                                                                              | Description                                                |
| ----------------- | ------------------------ | ------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Request file list | `MSG_CLIENT_LIST_FILES`  | `MSG_SERVER_UPDATE_LISTED_FILES`                                                            | Server returns the list of files based on user permissions |
| Create new file   | `MSG_CLIENT_CREATE_FILE` | `MSG_SERVER_SUCCESS`, `MSG_SERVER_UPDATE_LISTED_FILES`, or `MSG_SERVER_CREATE_FILE_FAILURE` | File is created or an error message is returned            |

---

### 3.3. File Editing

| State               | Client Message           | Server Message                                                       | Description                                                      |
| ------------------- | ------------------------ | -------------------------------------------------------------------- | ---------------------------------------------------------------- |
| File is opened      | `MSG_CLIENT_JOIN_FILE`   | `MSG_SERVER_LOAD_FILE` or `MSG_SERVER_LOAD_FILE_VIEWER`              | File content is sent to client in either editable or viewer mode |
| File update is sent | `MSG_CLIENT_UPDATE_FILE` | `MSG_SERVER_UPDATE_FILE_SUCCESS` or `MSG_SERVER_UPDATE_FILE_FAILURE` | Update is processed or error message returned                    |

---

## 4. Message Format and Structure

All messages are exchanged in JSON format.
Each message contains the following structure:

```json
{
  "cmd": "<MESSAGE_TYPE>",
  "payload": {
    // Message-specific content
  }
}
```

### Examples:

- For `MSG_CLIENT_LOGIN`:

```json
{
  "cmd": "MSG_CLIENT_LOGIN",
  "payload": {
    "username": "user1",
    "password": "hashed_password"
  }
}
```

- For `MSG_SERVER_LOAD_FILE`:

```json
{
  "cmd": "MSG_SERVER_LOAD_FILE",
  "payload": {
    "filename": "document.txt",
    "content": "File content goes here"
  }
}
```

---

## 5. Finite State Machine (FSM) / State Diagram

1. **Initial State:** Login screen is active
2. **Login Success:** Transition to file list screen
3. **File Selection:** File content is loaded and EditorView is shown
4. **Editing State:** Real-time updates are sent and received
5. **File Creation:** User creates a new file; if successful, it is added to the list
6. **Error States:** Permission, login, and operation errors result in appropriate error messages

---

## 6. Error Handling

| Error Message                    | Meaning              | Client Reaction             |
| -------------------------------- | -------------------- | --------------------------- |
| `MSG_SERVER_LOGIN_FAILURE`       | Login failed         | Show error, allow retry     |
| `MSG_SERVER_PERMISSION_FAILURE`  | No permission        | Access denied, show warning |
| `MSG_SERVER_CREATE_FILE_FAILURE` | File creation failed | Show error message          |
| `MSG_SERVER_UPDATE_FILE_FAILURE` | File update failed   | Show error message          |
| `MSG_SERVER_FAILURE`             | General failure      | Display general error       |

---

## 7. Summary

- The protocol enables real-time file sharing and user management through clear client-server messaging.
- All messages use a consistent JSON format.
- Each message type is clearly defined along with its expected behavior.
- The protocol is platform-independent and can be used in cross-language systems.
