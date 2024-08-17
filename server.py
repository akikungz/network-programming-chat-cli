import socket, threading, datetime, json

# Room object
rooms: dict[str, list[dict]] = {}

# Create a socket server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server to the port 8081
server.bind(('0.0.0.0', 8081))

# Listen for incoming connections
server.listen()

# Handle the client connection
def handle_client(client_socket):
    global rooms
    # Send a response to the client
    client_socket.send('Hello, client! use /help for show commands'.encode())

    while True:
        # Receive data from the client
        request = client_socket.recv(1024)

        message: str = request.decode()
        print(f'Received: {message}')
        
        if message.startswith("/"):
            command = message.split(" ")[0]
            if command == "/help":
                commands = [
                    '/help: Show commands',
                    '/clear: Clear the console',
                    '/create <room_name>: Create a room',
                    '/join <room_name> <username>: Join a room',
                    '/leave: Leave a room',
                    '/list: List all rooms',
                    '/exit: Exit the server'
                ]
                client_socket.send('\n'.join(commands).encode())
            elif command == "/create":
                try:
                    room_name = message.split(" ")[1]
                    if (room_name == ""):
                        client_socket.send('Please enter a room name'.encode())
                        continue
                    
                    if room_name in rooms:
                        client_socket.send(f'Room {room_name} already exists'.encode())
                        continue
                    
                    rooms[room_name] = []
                    client_socket.send(f'Room {room_name} created'.encode())
                except:
                    client_socket.send('Please enter a room name or server error'.encode())
            elif command == "/join":
                try:
                    room_name = message.split(" ")[1]
                    username = message.split(" ")[2]
                    
                    if room_name == "":
                        client_socket.send('Please enter a room name'.encode())
                        continue
                    
                    if username == "":
                        client_socket.send('Please enter a username'.encode())
                        continue
                    
                    if room_name in rooms:
                        # Check username in the room
                        existing_username = False
                        for room_client in rooms[room_name]:
                            if room_client["username"] == username:
                                client_socket.send('Username already exists in the room'.encode())
                                existing_username = True
                                break
                        
                        if existing_username:
                            continue
                        
                        rooms[room_name].append({
                            "socket": client_socket,
                            "username": username
                        })
                        client_socket.send(f'Joined room {room_name}'.encode())
                        
                        # Boardcast to all clients in the room
                        for room_client in rooms[room_name]:
                            if room_client["socket"] != client_socket:
                                room_client["socket"].send(f'{username} joined the room'.encode())
                    else:
                        client_socket.send(f'Room {room_name} not found'.encode())
                except:
                    client_socket.send('Please enter a room name and username'.encode())
            elif command == "/leave":
                have_room = False
                for room_name, room_clients in rooms.items():
                    for room_client in room_clients:
                        if room_client["socket"] == client_socket:
                            rooms[room_name].remove(room_client)
                            client_socket.send(f'Left room {room_name}'.encode())
                            have_room = True
                            break
                
                if not have_room:
                    client_socket.send('System: You are not in a room'.encode())
            elif command == "/list":
                try:
                    rooms = [room_name for room_name in rooms.keys()]
                    if len(rooms) > 0:
                        client_socket.send(f'Rooms: {", ".join(rooms)}'.encode())
                    else:
                        client_socket.send('No rooms'.encode())
                except:
                    client_socket.send('No rooms'.encode())
            elif command == "/exit":
                have_room = False
                try:
                    for room_name, room_clients in rooms.items():
                        for room_client in room_clients:
                            if room_client["socket"] == client_socket:
                                rooms[room_name].remove(room_client)
                                client_socket.send(f'Left room {room_name}'.encode())
                                have_room = True
                                break
                        if have_room:
                            break
                    client_socket.send('Goodbye!'.encode())
                except:
                    client_socket.send('Goodbye!'.encode())
                break
            elif command == "/clear":
                continue
            else:
                client_socket.send('Invalid command'.encode())
        else:
            # Send the message to all clients in the room with json format { message: "message", from: "client", time: "time" }
            try:
                have_room = False
                for room_name, room_clients in rooms.items():
                    for room_client in room_clients:
                        if room_client["socket"] == client_socket:
                            have_room = True
                            for room_client in room_clients:
                                room_client["socket"].send(json.dumps({
                                    "message": message,
                                    "from": room_client["username"],
                                    "time": datetime.datetime.now().strftime("%H:%M:%S")
                                }).encode())
                            break
                
                if not have_room:
                    client_socket.send('System: You are not in a room'.encode())
                    print('System: You are not in a room')
            except:
                client_socket.send('System: You are not in a room'.encode())
                print('Error: You are not in a room')
    
    # Close the client connection
    client_socket.close()

# Accept client connections
print('Server is listening for connections')

try:
    while True:
        # Accept the client connection
        client, addr = server.accept()
        print(f'Accepted connection from {addr}')

        # Create a thread to handle the client connection
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()
except KeyboardInterrupt:
    print('Server stopped')
    server.close()
    exit()
