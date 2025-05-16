import curses
import random
import time

def main(stdscr):
    # Initialize curses settings
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)   # Non-blocking input
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Snake color
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Food color

    # Get screen dimensions
    sh, sw = stdscr.getmaxyx()

    while True:
        # **Start Screen**
        stdscr.clear()
        msg = "Press any key to start"
        stdscr.addstr(sh // 2, (sw - len(msg)) // 2, msg)
        stdscr.refresh()
        stdscr.getch()  # Wait for user input to start

        # Initialize game state
        snake_y = sh // 2
        snake_x = sw // 4
        snake = [(snake_y, snake_x)]
        food = (sh // 2, sw // 2)
        direction = curses.KEY_RIGHT
        score = 0
        paused = False

        # Draw initial food
        stdscr.addch(food[0], food[1], '*', curses.color_pair(2))

        # Game loop
        while True:
            # Adjust speed based on score
            timeout = max(50, 100 - (score // 5) * 10)  # Decrease timeout every 5 points
            stdscr.timeout(timeout)

            # Display score
            stdscr.addstr(0, 0, f'Score: {score}')

            # Get user input
            next_key = stdscr.getch()

            # **Pause Functionality**
            if next_key == ord('p'):
                paused = not paused
                if paused:
                    msg = "Paused, press 'p' to continue"
                    stdscr.addstr(sh // 2, (sw - len(msg)) // 2, msg)
                    stdscr.refresh()
                    while paused:
                        key = stdscr.getch()
                        if key == ord('p'):
                            paused = False
                    stdscr.clear()  # Clear pause message
                    # Redraw snake and food
                    for y, x in snake:
                        stdscr.addch(y, x, '█', curses.color_pair(1))
                    stdscr.addch(food[0], food[1], '*', curses.color_pair(2))
                continue

            if not paused:
                # **Enhanced Controls (Arrow keys + WASD)**
                if next_key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT,
                                ord('w'), ord('a'), ord('s'), ord('d')]:
                    # Map WASD to directions
                    if next_key == ord('w'):
                        new_direction = curses.KEY_UP
                    elif next_key == ord('a'):
                        new_direction = curses.KEY_LEFT
                    elif next_key == ord('s'):
                        new_direction = curses.KEY_DOWN
                    elif next_key == ord('d'):
                        new_direction = curses.KEY_RIGHT
                    else:
                        new_direction = next_key

                    # **Prevent Reversing Direction**
                    if not ((direction == curses.KEY_UP and new_direction == curses.KEY_DOWN) or
                            (direction == curses.KEY_DOWN and new_direction == curses.KEY_UP) or
                            (direction == curses.KEY_LEFT and new_direction == curses.KEY_RIGHT) or
                            (direction == curses.KEY_RIGHT and new_direction == curses.KEY_LEFT)):
                        direction = new_direction
                else:
                    # Keep current direction if no valid key
                    new_direction = direction

                # Calculate new head position
                head = snake[0]
                if direction == curses.KEY_DOWN:
                    new_head = (head[0] + 1, head[1])
                elif direction == curses.KEY_UP:
                    new_head = (head[0] - 1, head[1])
                elif direction == curses.KEY_LEFT:
                    new_head = (head[0], head[1] - 1)
                elif direction == curses.KEY_RIGHT:
                    new_head = (head[0], head[1] + 1)

                # Insert new head
                snake.insert(0, new_head)

                # Check for food collision
                if snake[0] == food:
                    score += 1
                    while True:
                        food = (random.randint(1, sh - 2), random.randint(1, sw - 2))
                        if food not in snake:
                            break
                    stdscr.addch(food[0], food[1], '*', curses.color_pair(2))
                else:
                    # Remove tail
                    tail = snake.pop()
                    stdscr.addch(tail[0], tail[1], ' ')

                # Draw snake head
                try:
                    stdscr.addch(snake[0][0], snake[0][1], '█', curses.color_pair(1))
                except curses.error:
                    break

                # Check for self-collision or border collision
                if snake[0] in snake[1:] or snake[0][0] <= 0 or snake[0][0] >= sh - 1 or \
                   snake[0][1] <= 0 or snake[0][1] >= sw - 1:
                    break

        # **Enhanced Game Over Screen**
        stdscr.clear()
        msg = f'Game Over! Final Score: {score}. Press "r" to restart or "q" to quit'
        stdscr.addstr(sh // 2, (sw - len(msg)) // 2, msg)
        stdscr.refresh()
        while True:
            key = stdscr.getch()
            if key == ord('r'):
                break  # Restart game
            elif key == ord('q'):
                return  # Quit game

if __name__ == '__main__':
    curses.wrapper(main)
