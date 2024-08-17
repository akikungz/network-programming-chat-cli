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
                if message.startswith("exit"):
                    client_socket.close()
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
            break

# Create a client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# IP Validation
def is_valid_ipv4(ip: str) -> bool:
    try:
        socket.inet_pton(socket.AF_INET, ip)
        return True
    except:
        return False

server_address = input("Enter the server address: ")
while not is_valid_ipv4(server_address):
    print("Invalid IP address")
    server_address = input("Enter the server address: ")

port_number = int(input("Enter the port number: "))
while port_number < 1024 or port_number > 49151:
    print("Invalid port number")
    port_number = int(input("Enter the port number: "))

# Connect to the server
client_socket.connect((server_address, port_number))

# Receive data from the server
threading.Thread(target=receive_messages, args=(client_socket,)).start()

# Send data to the server
threading.Thread(target=send_messages, args=(client_socket,)).start()