# NetDaemon

**NetDaemon** is a multi-client TCP server-client communication system. The server can manage multiple clients simultaneously, execute shell commands remotely, and transfer files between server and clients. It also supports automatic client reconnection if the connection is lost.

---

## Features

- Multi-client support  
- Remote command execution  
- File upload and download  
- Automatic client reconnection  
- Interactive client selection  
- Simple, colorful terminal interface  
- Command-line arguments for custom server startup options  

---

## Command-Line Arguments

These arguments let you start the server with customized settings:

| Argument | Description |
|---------|-------------|
| `-t, --target <IP>` | Optional. The IP address for the server to bind to. Default: `127.0.0.1` |
| `-p, --port <PORT>` | Optional. The port for the server to bind to. Default: `12345` |
| `-h, --help` | Optional. Displays the help dialogue and exits |

---

## Server Commands

### **General / Server Shell**

| Command | Description |
|---------|-------------|
| `exit` / `quit` | Ends the server communication shell (server-side only) |
| `list` | Lists all connected clients with their index |
| `connect <index>` | Connects to a client given its index |
| `back` | Returns to the main server shell from a client session |

---

## Client Shell Commands

These are available after connecting to a specific client:

| Command | Description |
|---------|-------------|
| `endcon` / `disconnect` | Permanently disconnects from the client and returns to the main server shell |
| `upload <path>` | Uploads a file *from the server to the client* |
| `download <path>` | Downloads a file *from the client to the server* |
| `help` | Shows the help dialogue |

---

## Basic Shell Commands (Executed on the Client)

NetDaemon forwards many normal shell commands to the connected client:

- `ls` / `dir` – list files in the current directory  
- `cd <directory>` – change directory  
- `pwd` – print working directory  
- `grep <pattern>` – search text inside files  
- …and most standard shell commands supported by the client OS  

---

## Notes

- Clients automatically attempt to reconnect if disconnected unexpectedly.  
- Multiple clients can be connected concurrently; switch between them using `connect <index>` and `back`.  
- Color-coded terminal output improves readability of commands, statuses, and errors.  
- Use the `--help` flag or the in-shell `help` command to display the full help dialogue.
