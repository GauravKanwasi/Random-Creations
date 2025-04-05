import curses
import random
import time
import os

# Define the Tetris board size
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

# Define the Tetris pieces
PIECES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 1, 1], [1, 0, 0]],  # J
    [[1, 1, 1], [0, 0, 1]]   # L
]

# Function to initialize the board
def init_board():
    return [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]

# Function to draw the board
def draw_board(stdscr, board, next_piece, score, level):
    stdscr.clear()
    stdscr.addstr(0, 0, f"Score: {score} | Level: {level}")
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell:
                stdscr.addch(y + 1, x, '#')
            else:
                stdscr.addch(y + 1, x, ' ')
    
    # Draw next piece preview
    stdscr.addstr(0, BOARD_WIDTH + 2, "Next Piece:")
    for y, row in enumerate(next_piece):
        for x, cell in enumerate(row):
            if cell:
                stdscr.addch(y + 2, BOARD_WIDTH + 2 + x, '#')
            else:
                stdscr.addch(y + 2, BOARD_WIDTH + 2 + x, ' ')
    
    stdscr.refresh()

# Function to check for collisions
def check_collision(board, piece, offset):
    px, py = offset
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                if (py + y >= BOARD_HEIGHT or
                    px + x >= BOARD_WIDTH or
                    px + x < 0 or
                    board[py + y][px + x]):
                    return True
    return False

# Function to place a piece on the board
def place_piece(board, piece, offset):
    px, py = offset
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                board[py + y][px + x] = 1

# Function to clear lines
def clear_lines(board):
    new_board = []
    lines_cleared = 0
    for row in board:
        if 0 not in row:
            lines_cleared += 1
        else:
            new_board.append(row)
    while len(new_board) < BOARD_HEIGHT:
        new_board.insert(0, [0] * BOARD_WIDTH)
    return new_board, lines_cleared

# Main game function
def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    board = init_board()
    next_piece = random.choice(PIECES)
    piece = next_piece
    next_piece = random.choice(PIECES)
    offset = [BOARD_WIDTH // 2 - len(piece[0]) // 2, 0]
    score = 0
    level = 1
    lines_cleared = 0

    while True:
        draw_board(stdscr, board, next_piece, score, level)
        key = stdscr.getch()

        if key == ord('q'):
            break

        if key == curses.KEY_LEFT:
            if not check_collision(board, piece, [offset[0] - 1, offset[1]]):
                offset[0] -= 1
        elif key == curses.KEY_RIGHT:
            if not check_collision(board, piece, [offset[0] + 1, offset[1]]):
                offset[0] += 1
        elif key == curses.KEY_UP:
            rotated_piece = list(zip(*piece[::-1]))
            if not check_collision(board, rotated_piece, offset):
                piece = rotated_piece
        elif key == curses.KEY_DOWN:
            if not check_collision(board, piece, [offset[0], offset[1] + 1]):
                offset[1] += 1
            else:
                place_piece(board, piece, offset)
                board, lines_cleared = clear_lines(board)
                score += lines_cleared * 100 * level
                piece = next_piece
                next_piece = random.choice(PIECES)
                offset = [BOARD_WIDTH // 2 - len(piece[0]) // 2, 0]
                if check_collision(board, piece, offset):
                    break

        # Increase level and speed
        if lines_cleared >= 10:
            level += 1
            lines_cleared = 0
            stdscr.timeout(100 - level * 10)

        time.sleep(0.1)

    stdscr.addstr(0, 0, f"Game Over! Score: {score} | Level: {level}")
    stdscr.refresh()
    time.sleep(3)

if __name__ == "__main__":
    curses.wrapper(main)
