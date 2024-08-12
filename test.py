import curses
from datetime import datetime

def main(stdscr):
    # Clear screen
    stdscr.clear()

    # Get screen height and width
    height, width = stdscr.getmaxyx()

    # Create a window for the chat history
    chat_window = curses.newwin(height - 3, width, 0, 0)

    # Create a window for user input
    input_window = curses.newwin(3, width, height - 3, 0)
    input_window.addstr(0, 0, "Type your message: ")

    # List to store chat history
    chat_history = []

    while True:
        # Refresh chat window with history
        chat_window.clear()
        for i, msg in enumerate(chat_history[-(height-4):]):
            chat_window.addstr(i, 0, msg)
        chat_window.refresh()

        # Get user input
        input_window.clear()
        input_window.addstr(0, 0, "Type your message: ")
        input_window.refresh()
        curses.echo()
        user_input = input_window.getstr(1, 0).decode("utf-8")
        curses.noecho()

        # Check if user wants to quit
        if user_input.lower() == "quit":
            break

        # Add timestamp and message to chat history
        timestamp = datetime.now().strftime("%H:%M:%S")
        chat_history.append(f"[{timestamp}] {user_input}")

if __name__ == "__main__":
    curses.wrapper(main)
