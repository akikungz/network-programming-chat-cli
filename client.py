import socket, threading, time, json

# Client socket for receiving messages from the server
def receive_messages(client_socket: socket.socket):
    while True:
        try:
            message: str = client_socket.recv(1024).decode()
            
            if message.startswith("{"):
                data = json.loads(message)
                print(f'{data["from"]}: {data["message"]}')
            else:
                print(message)
        except:
            break

# Client socket for sending messages to the server
def send_messages(client_socket):
    while True:
        message = input()
        client_socket.send(message.encode())
        if message == "/exit":
            break

# Create a client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect(('127.0.0.1', 8081))

# Receive data from the server
threading.Thread(target=receive_messages, args=(client_socket,)).start()

# Send data to the server
threading.Thread(target=send_messages, args=(client_socket,)).start()