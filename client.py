import asyncio, curses, threading, time
from datetime import datetime

# Chat history
chat_history: list[str] = []

# Last message
last_message = ""

# Function to handle receiving messages
async def receive_messages(reader: asyncio.StreamReader, chat_window: curses.window):
    while True:
        data = await reader.read(100)
        if not data:
            break
        message = data.decode()
        chat_history.append(message)

# Function to handle updating the chat window
def update_chat_window(chat_window: curses.window):
    while True:
        chat_window.clear()
        for i, msg in enumerate(chat_history[-(chat_window.getmaxyx()[0]-1):]):
            chat_window.addstr(i, 0, msg)
            if i == len(chat_history) - 1:
                chat_window.addstr(i, 0, last_message)

        chat_window.refresh()

# Main function
def main(stdscr):
    global last_message
    # Clear screen
    stdscr.clear()

    # Get screen height and width
    height, width = stdscr.getmaxyx()

    # Create a title bar
    title_bar = curses.newwin(1, width-2, 1, 1)
    title_bar.addstr("Welcome to the chat!")
    title_bar.refresh()
    
    # Create a chat window
    chat_window = curses.newwin(height-5, width-2, 3, 1)
    
    # Create an input window
    input_window = curses.newwin(1, width-2, height-2, 1)

    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Connect to the server
    reader, writer = loop.run_until_complete(asyncio.open_connection('127.0.0.1', 8888))
    
    # Handle updating the chat window
    chat_thread = threading.Thread(target=update_chat_window, args=(chat_window,))
    chat_thread.daemon = True
    chat_thread.start()
    
    # Get user name
    input_window.addstr("Enter your name: ")
    curses.echo()
    user_name = input_window.getstr().decode()
    curses.noecho()
    writer.write(user_name.encode())
    loop.run_until_complete(writer.drain())
    
    # Start receiving messages
    loop.create_task(receive_messages(reader, chat_window))
    
    # Start sending messages
    while True:
        input_window.clear()
        input_window.addstr(f"{user_name}: ")
        curses.echo()
        user_input = input_window.getstr().decode()
        curses.noecho()
        input_window.refresh()
        
        if user_input.lower() == "quit":
            exit_message = f"{user_name} has left the chat."
            writer.write(exit_message.encode())
            loop.run_until_complete(writer.drain())
            
            break
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"[{timestamp}] - {user_name}: {user_input}\n"
        last_message = message
        writer.write(message.encode())
        loop.run_until_complete(writer.drain())
        input_window.clear()
        
    writer.close()
    loop.run_until_complete(writer.wait_closed())
    
    loop.close()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except:
        pass