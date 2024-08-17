import socket, threading, time, json

# Room object
rooms = {}

# Create a socket server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server to the port 8081
server.bind(('0.0.0.0', 8081))

# Listen for incoming connections
server.listen()

# Handle the client connection
def handle_client(client_socket):
    # Send a response to the client
    client_socket.send('Hello, client! use /help for show commands'.encode())

    while True:
        # Receive data from the client
        request = client_socket.recv(1024)
        print(f'Received: {request.decode()}')

        message: str = request.decode()
        
        if message.startswith("/"):
            command = message.split(" ")[0]
            if command == "/help":
                client_socket.send('Commands: /help, /create_room, /join_room, /leave_room, /list_rooms, /send_message, /exit'.encode())
            elif command == "/create_room":
                room_name = message.split(" ")[1]
                rooms[room_name] = []
                client_socket.send(f'Room {room_name} created'.encode())
            elif command == "/join_room":
                room_name = message.split(" ")[1]
                if room_name in rooms:
                    rooms[room_name].append(client_socket)
                    client_socket.send(f'Joined room {room_name}'.encode())
                else:
                    client_socket.send(f'Room {room_name} not found'.encode())
            elif command == "/leave_room":
                room_name = message.split(" ")[1]
                if room_name in rooms:
                    rooms[room_name].remove(client_socket)
                    client_socket.send(f'Left room {room_name}'.encode())
                else:
                    client_socket.send(f'Room {room_name} not found'.encode())
            elif command == "/list_rooms":
                client_socket.send(f'Rooms: {", ".join(rooms.keys())}'.encode())
            elif command == "/exit":
                client_socket.send('Goodbye!'.encode())
                break
            else:
                client_socket.send('Invalid command'.encode())
        else:
            # Send the message to all clients in the room with json format { message: "message", from: "client", time: "time" }
            for room_name, room_clients in rooms.items():
                if client_socket in room_clients:
                    for room_client in room_clients:
                        if room_client != client_socket:
                            data = json.dumps({
                                "message": message,
                                "from": client_socket.getpeername(),
                                "time": time.time()
                            })
                            room_client.send(data.encode())
                    break
    
    # Close the client connection
    client_socket.close()

# Accept client connections
print('Server is listening for connections')

while True:
    # Accept the client connection
    client, addr = server.accept()
    print(f'Accepted connection from {addr}')

    # Create a thread to handle the client connection
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()
