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

---

## Server Commands

### **General / Server Shell**

| Command                  | Description |
|---------------------------|-------------|
| `exit` / `quit`           | Ends the server communication shell (server-side only) |
| `list`                     | Lists all connected clients with their index |
| `connect <index>`          | Connects to a client given its index |
| `back`                     | Returns to the main server shell from a client session |

---

### **Client Shell**

| Command                  | Description |
|---------------------------|-------------|
| `endcon` / `disconnect`   | Ends the connection with the current client (permanent disconnect) |
| `upload <path>`           | Uploads a file from the server to the client |
| `download <path>`         | Downloads a file from the client to the server |
| `help`                     | Shows this help dialogue |

---

### **Basic Shell Commands**

These are executed on the client system:

- `ls` / `dir` – list files in current directory  
- `cd <directory>` – change directory  
- `pwd` – print current working directory  
- `grep <pattern>` – search text in files  
- And other standard shell commands  

---

### **Notes**

- When a client disconnects unexpectedly, it will automatically attempt to reconnect.  
- The server can interact with multiple clients at once, and you can switch between them with `connect <index>` and `back`.  
- Colored terminal output improves readability of commands and statuses.  
