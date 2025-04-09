import curses
import random
import time

def main(stdscr):
    # Set up initial game state
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    # Get screen height and width
    sh, sw = stdscr.getmaxyx()
    
    # Create initial snake position (middle of screen)
    snake_y = sh//2
    snake_x = sw//4
    snake = [(snake_y, snake_x)]
    
    # Create initial food
    food = (sh//2, sw//2)
    stdscr.addch(food[0], food[1], '🍎', curses.color_pair(2))

    # Initial direction
    direction = curses.KEY_RIGHT
    
    # Game loop
    score = 0
    while True:
        # Display score
        stdscr.addstr(0, 0, f'Score: {score}')
        
        # Get next key press
        next_key = stdscr.getch()
        direction = direction if next_key == -1 else next_key

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
        
        # Check if we hit the food
        if snake[0] == food:
            score += 1
            # Create new food
            while True:
                food = (random.randint(1, sh-2), random.randint(1, sw-2))
                if food not in snake:
                    break
            stdscr.addch(food[0], food[1], '🍎', curses.color_pair(2))
        else:
            # Remove tail
            tail = snake.pop()
            stdscr.addch(tail[0], tail[1], ' ')
        
        # Draw snake
        try:
            stdscr.addch(snake[0][0], snake[0][1], '█', curses.color_pair(1))
        except curses.error:
            # Game over if we hit the walls
            break

        # Check if snake hits itself
        if snake[0] in snake[1:]:
            break
        
        # Check if we hit the borders
        if (snake[0][0] >= sh-1 or snake[0][0] <= 0 or
            snake[0][1] >= sw-1 or snake[0][1] <= 0):
            break

    # Game Over
    stdscr.clear()
    msg = f'Game Over! Final Score: {score}'
    stdscr.addstr(sh//2, (sw-len(msg))//2, msg)
    stdscr.refresh()
    time.sleep(2)

if __name__ == '__main__':
    curses.wrapper(main)
