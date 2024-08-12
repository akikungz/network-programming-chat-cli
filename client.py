import asyncio, curses, threading
from datetime import datetime

# Chat history
chat_history = []

# Client Code
async def receive_messages(reader, chat_window, height):
    while True:
        data = await reader.read(100)
        if not data:
            break
        message = data.decode()
        chat_history.append(message)
        chat_window.clear()
        for i, msg in enumerate(chat_history[-(height-4):]):
            chat_window.addstr(i, 0, msg)
        chat_window.refresh()

async def send_message(writer, message):
    writer.write(message.encode())
    await writer.drain()

# Chat client
async def chat_client(stdscr: curses.window, reader: asyncio.ReadTransport, writer: asyncio.WriteTransport):
    curses.echo()
    height, width = stdscr.getmaxyx()

    # Create windows
    user_info = curses.newwin(1, width, 0, 0)
    chat_window = curses.newwin(height - 3, width, 0, 0)
    input_window = curses.newwin(1, width, height - 2, 0)

    # Start the receive_messages coroutine
    asyncio.create_task(receive_messages(reader, chat_window, height))
    
    input_window.clear()
    input_window.addstr(0, 1, "Username: ")
    input_window.refresh()
    curses.echo()
    username = input_window.getstr(0, 11).decode("utf-8")
    curses.noecho()
    
    user_info.addstr(0, 0, f"Username: {username}")
    user_info.refresh()
    
    await send_message(writer, username)
    
    # Send messages
    while True:
        # Get user input
        input_window.clear()
        input_window.addstr(1, 1, "Message: ")
        input_window.refresh()
        curses.echo()
        user_input = input_window.getstr(1, 10).decode("utf-8")
        curses.noecho()

        # Check if user wants to quit
        if user_input.lower() == "exit":
            break

        # Add timestamp and message to chat history
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"[{timestamp}] - {username}: {user_input}"
        chat_history.append(message)
        
        # Send message to server
        await send_message(writer, message)
        
    writer.close()
    await writer.wait_closed()

async def main(stdscr):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    await chat_client(stdscr, reader, writer)

if __name__ == "__main__":
    # Start the server in a separate thread
    asyncio.get_event_loop()\
        .run_until_complete(asyncio.gather(curses.wrapper(main)))