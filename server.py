import socket, threading, datetime, json

# Room object
rooms: dict[str, list[dict]] = {}

# Create a socket server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server to the port 8081
server.bind(('0.0.0.0', 8081))

# Listen for incoming connections
server.listen()

# Leave the room
def leave_room(client_socket):
    global rooms
    
    have_room = False
    room = None
    
    for room_name, room_clients in rooms.items():
        for room_client in room_clients:
            room = room_name
            if room_client["socket"] == client_socket:
                user_leave = room_client["username"]
                client_socket.send(f'Left room {room_name}'.encode())
                rooms[room_name].remove(room_client)
                have_room = True
                break
        if have_room:
            break
    
    if have_room:
        # Boardcast to all clients in the room
        try:
            for room_client in rooms[room]:
                room_client["socket"].send(f'{user_leave} left the room'.encode())
        except:
            pass
    
    return have_room

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
            args = message.split(" ")[1:]
            if command == "/help":
                commands = [
                    '/help: Show commands',
                    '/clear: Clear the console',
                    '/create <room_name>: Create a room',
                    '/join <room_name> <username>: Join a room',
                    '/leave: Leave a room',
                    '/list: List all rooms',
                    '/users: List all users in the room',
                    '/exit: Exit the server'
                ]
                client_socket.send('\n'.join(commands).encode())
            elif command == "/create":
                try:
                    room_name = args[0]
                    if (room_name == ""):
                        client_socket.send('Please enter a room name'.encode())
                        continue
                    
                    if room_name in rooms:
                        client_socket.send(f'Room {room_name} already exists'.encode())
                        continue
                    
                    rooms[room_name] = []
                    client_socket.send(f'Room {room_name} created'.encode())
                except:
                    print("Server error")
                    client_socket.send('Please enter a room name'.encode())
            elif command == "/join":
                leave_room(client_socket)
                try:
                    room_name = args[0]
                    username = args[1]
                    
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
                            room_client["socket"].send(f'{username} joined the room'.encode())
                    else:
                        client_socket.send(f'Room {room_name} not found'.encode())
                except:
                    print("Server error")
                    client_socket.send('Please enter a room name and username'.encode())
            elif command == "/leave":
                have_room = leave_room(client_socket)
                
                if not have_room:
                    client_socket.send('System: You are not in a room'.encode())
            elif command == "/list":
                room_names = list(rooms.keys())
                if len(room_names) == 0:
                    client_socket.send('No rooms available'.encode())
                else:
                    client_socket.send('\n'.join(room_names).encode())
            elif command == "/users":
                have_room = False
                for room_name, room_clients in rooms.items():
                    for room_client in room_clients:
                        if room_client["socket"] == client_socket:
                            have_room = True
                            users = [room_client["username"] for room_client in room_clients]
                            # Highlight the current user
                            for i, user in enumerate(users):
                                if user == room_client["username"]:
                                    users[i] = f'* {user}'
                        
                            users.sort()
                            client_socket.send('\n'.join(users).encode())
                            break
                
                if not have_room:
                    client_socket.send('System: You are not in a room'.encode())
            elif command == "/exit":
                leave_room(client_socket)
                client_socket.send('exit'.encode())
                break
            elif command == "/clear":
                continue
            else:
                client_socket.send('Invalid command'.encode())
        else:
            try:
                have_room = False
                for room_name, room_clients in rooms.items():
                    for room_client in room_clients:
                        if room_client["socket"] == client_socket:
                            have_room = True
                            sender_username = room_client["username"]
                            for room_client in room_clients:
                                data = json.dumps({
                                    "message": message,
                                    "from": sender_username,
                                    # Format the time as HH:MM:SS - DD/MM/YYYY
                                    "time": datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
                                })
                                room_client["socket"].send(data.encode())
                            break
                
                if not have_room:
                    client_socket.send('System: You are not in a room'.encode())
            except:
                print('Server error')
                client_socket.send('System: You are not in a room'.encode())
    
    # Close the client connection
    client_socket.close()

# Accept client connections
print('Server is listening for connections')
print('Server listening on port 8081')
# Get all host ip address
host_ip = socket.gethostbyname(socket.gethostname())
print(f'Host IP: {host_ip}')
print('Type /exit to shutdown the server')

def handle_exit():
    try:
        while True:
            if input() == "/exit":
                print("Server is shutting down...")
                server.close()
                exit(0)
    except KeyboardInterrupt:
        exit()

threading.Thread(target=handle_exit).start()

while True:
    # Accept the client connection
    client, addr = server.accept()
    print(f'Accepted connection from {addr}')

    # Create a thread to handle the client connection
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()