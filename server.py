import asyncio

chats = []

clients = []

# Server Code
async def handle_client(reader: asyncio.ReadTransport, writer: asyncio.WriteTransport):
    addr = writer.get_extra_info('peername')
    print(f"Connection from {addr}")
    
    if not addr in clients:
        name = await reader.read(100)
        clients.append(addr)
        print(f"Name {name.decode()} from {addr}")
        
        writer.write("Welcome to the chat!".encode())

        if chats:
            for chat in chats:
                writer.write(chat.encode())
                await writer.drain()

    while True:
        data = await reader.read(100)
        if not data:
            break
        message = data.decode()
        print(f"Received {message}")
        writer.write(message.encode())
        await writer.drain()

    print(f"Connection closed from {addr}")
    clients.remove(addr)
    writer.close()
    await writer.wait_closed()

async def start_server():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(start_server())