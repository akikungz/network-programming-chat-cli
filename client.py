import socket, threading, json, sys

# Client socket for receiving messages from the server
def receive_messages(client_socket: socket.socket):
    while True:
        try:
            message: str = client_socket.recv(1024).decode()
        
            if message.startswith("{") and message.endswith("}"):
                data = json.loads(message)
                # print(data)
                print(f'[{data["from"]}] {data["time"]}\n{data["message"]}\n')
            else:
                print(message)
        except:
            break

# Client socket for sending messages to the server
def send_messages(client_socket):
    while client_socket.fileno() != -1:
        message = input()
        
        if message == "/clear":
            sys.stdout.write("\033[H\033[J")
            print("Type /help to see the commands")
            continue
        
        client_socket.send(message.encode())
        if message == "/exit":
            client_socket.close()

# Create a client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect(('127.0.0.1', 8081))

# Receive data from the server
threading.Thread(target=receive_messages, args=(client_socket,)).start()

# Send data to the server
threading.Thread(target=send_messages, args=(client_socket,)).start()