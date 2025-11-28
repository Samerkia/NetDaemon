import socket
import threading
import subprocess
import os
import struct
import sys
from getopt import *

# Function for colored output
def color(r=None, g=None, b=None, text=None, col=None):
    colors = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "white": (255, 255, 255),
        "black": (0, 0, 0)
    }

    if col and col in colors:
        r, g, b = colors[col]

    if r is not None and g is not None and b is not None and text is not None:
        return f"\033[38;2;{r};{g};{b}m{text}\033[38;2;255;255;255m"
    return text

# Global list of connected clients
clients = []  # List of tuples (socket, address)
# Default host and port
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 12345

# Print help dialogue
def printHelp():
    # Looks better but still working on making this look good
    commands = [
        ("Command Line Arguments:", "Used for starting the server with custom options"),
        ("-t, --target <IP>", "Optional, IP address to bind the server to. Default: 127.0.0.1"),
        ("-p, --port <PORT>", "Optional, Port to bind the server to. Default: 12345"),
        ("-h, --help", "Optional, Shows this dialogue"),
        ("", ""),
        ("Custom Commands:", "Used in the shell to control clients and server operations"),
        ("exit / quit", "Ends the server communication side only"),
        ("list", "Lists all available clients with their index"),
        ("connect <index>", "Connects to a client given the index"),
        ("upload", "Upload a file to client"),
        ("download", "Download a file from the client"),
        ("back", "Works inside a client shell, returns to main server shell"),
        ("endcon / disconnect", "Works inside a client shell, ends the connection with that client and returns to main server shell"),
        ("help", "Shows this dialogue")
    ]

    print("\n" + "_"*120)
    for cmd, desc in commands:
        # Pad the plain command to 25 characters
        padded_cmd = f"{cmd:<25}"
        # Apply color only to the padded command
        if cmd: print(f"{color(col='yellow', text=padded_cmd)} ----->  {desc}")
        else: print("_"*120)
    print("_"*120)
    print(f"{color(col='yellow', text='NOTE:')}\tYou also have your other basic shell commands like ls, dir, cd, etc\n")

# Create and return a server socket
def createServerSocket(host='127.0.0.1', port=12345):
    servSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servSocket.bind((host, port))
    servSocket.listen()
    print(f"{color(col='green', text='Server started on')} <{color(col='cyan', text=host)} : {color(col='cyan', text=port)}>\nListening for connections...")
    return servSocket

# Accept incoming client connections
def acceptClients(servSocket):
    while True:
        try:
            clientSocket, address = servSocket.accept()
            clients.append((clientSocket, address))
            print(f"{color(col='green', text='New client connected:')} {address}")
        except Exception as e:
            print(color(col='red', text=f"Error accepting client: {e}"))

# Handle file upload from server to client
def handleUpload(clientSocket, path):
    try:
        if not os.path.exists(path):
            clientSocket.send(b"ERROR: File not found on server.")
            return

        file_size = os.path.getsize(path)
        clientSocket.send(struct.pack(">Q", file_size))
        file_name = os.path.basename(path).encode('utf-8')
        clientSocket.send(struct.pack(">I", len(file_name)) + file_name)

        with open(path, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                clientSocket.sendall(data)
        print(f"{color(col='green', text='Upload complete:')} {path}")
    except Exception as e:
        clientSocket.send(f"Error during upload: {e}".encode('utf-8'))

# Handle file download from client to server
def handleDownload(clientSocket, path):
    try:
        clientSocket.send(f"download {path}".encode('utf-8'))

        raw_size = clientSocket.recv(8)
        if not raw_size:
            raise Exception("Did not receive file size.")
        file_size = struct.unpack(">Q", raw_size)[0]

        raw_name_length = clientSocket.recv(4)
        if not raw_name_length:
            raise Exception("Did not receive file name length.")
        name_length = struct.unpack(">I", raw_name_length)[0]

        file_name = clientSocket.recv(name_length).decode('utf-8')
        if not file_name:
            raise Exception("Did not receive file name.")

        with open(file_name, 'wb') as f:
            bytes_received = 0
            while bytes_received < file_size:
                data = clientSocket.recv(1024)
                if not data:
                    break
                f.write(data)
                bytes_received += len(data)
        print(f"{color(col='green', text='Download complete:')} {file_name}")
        clientSocket.send(b"Download complete.")
    except Exception as e:
        print(color(col='red', text=f"Error during download: {e}"))
        clientSocket.send(f"Error: {e}".encode('utf-8'))

# Interact with a selected connected client
def interactWithClient(clientIndex):
    clientSocket, address = clients[clientIndex]
    print(f"{color(col='green', text='Connected to client:')} {address}")
    try:
        while True:
            command = input(f"[Client {clientIndex}] >> ").strip()
            if command.lower() in ["back"]:
                print("Returning to main shell...")
                break
            if command.lower() == "help":
                printHelp()
                continue
            if command.lower().startswith("upload "):
                path = command[7:].strip()
                handleUpload(clientSocket, path)
                continue
            if command.lower().startswith("download "):
                path = command[9:].strip()
                handleDownload(clientSocket, path)
                continue
            if command.lower() in ["endcon", "disconnect"]:
                check = input("Are you sure? >> ")
                if check.lower() in ["y", "yes"]:
                    print(color(col='red', text=f"Disconnecting client {address}"))
                    clientSocket.send(b"TERMINATE")
                    clientSocket.close()
                    clients.pop(clientIndex)
                else:
                    print("Disconnect cancelled.")
                break

            # Send the command to client
            clientSocket.send(command.encode('utf-8'))

            # Receive output
            try:
                output = clientSocket.recv(4096).decode('utf-8')
                print(output)
            except Exception as e:
                print(color(col='red', text=f"Error receiving data: {e}"))
                break

    except KeyboardInterrupt:
        print("Returning to main shell...")
    except ConnectionResetError:
        print(color(col='red', text=f"Client {address} disconnected"))
        clients.pop(clientIndex)

#Gets arguments
def get_arguments():

    try:
        #option map
        options = getopt(sys.argv[1:],
                         shortopts="t:p:h",
                         longopts=["text=", "prints=", "help"])
    except GetoptError as e:
        print ("ERROR: Wrong option used --> ", e)

    host = DEFAULT_HOST
    port = DEFAULT_PORT
    if options:
        for (opt, args) in options[0]:

            #Help options
            if opt in ("-h", "--help"):
                sys.exit(printHelp())
            #IP/Host option
            if opt in ("-t", "--target"):
                host = args
            #Port option
            try:
                if opt in ("-p", "--port"):
                    port = int(args)
            except ValueError as e:
                print("ERROR: Port must be an int value --> ", e)
                sys.exit(printHelp())
    
    return host, port

# Main server loop
def main():
    host, port = get_arguments()
    servSocket = createServerSocket(host, port)
    threading.Thread(target=acceptClients, args=(servSocket,), daemon=True).start()

    try:
        while True:
            command = input("Server >> ").strip()
            if command.lower() == "help":
                printHelp()
            elif command.lower() == "list":
                for i, (sock, addr) in enumerate(clients):
                    print(f"[{i}] {addr}")
            elif command.lower().startswith("connect "):
                try:
                    index = int(command.split()[1])
                    if 0 <= index < len(clients):
                        interactWithClient(index)
                    else:
                        print(color(col='red', text="Invalid client index"))
                except Exception as e:
                    print(color(col='red', text=f"Error: {e}"))
            elif command.lower() in ["exit", "quit"]:
                print("Shutting down server...")
                break
            else:
                print("Unknown command. Type 'help' for options.")

    except KeyboardInterrupt:
        print("\nServer shutting down...")

    finally:
        for sock, _ in clients:
            sock.close()
        servSocket.close()
        print("Server socket closed.")

if __name__ == "__main__":
    main()
