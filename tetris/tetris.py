import pygame
import random

# Constants
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 600
BLOCK_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
FPS = 60

# Colors for pieces
COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 0, 255),
    'L': (255, 165, 0)
}

# Tetris pieces with identifiers
PIECES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[1, 1, 1], [0, 1, 0]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 1, 1], [1, 0, 0]],
    'L': [[1, 1, 1], [0, 0, 1]]
}


def draw_text(surface, text, size, x, y, color=(255, 255, 255)):
    """Helper function to draw text on the screen."""
    font = pygame.font.SysFont("Arial", size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, (x, y))


def draw_board(screen, board):
    """Draw the game board grid and filled blocks."""
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            if board[y][x]:
                # Draw filled block with a border
                pygame.draw.rect(screen, board[y][x],
                                 (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, (30, 30, 30),
                                 (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)


def draw_piece(screen, piece, offset, color):
    """Draw the current falling piece."""
    px, py = offset
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, color,
                                 ((px + x) * BLOCK_SIZE, (py + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, (30, 30, 30),
                                 ((px + x) * BLOCK_SIZE, (py + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)


def check_collision(board, piece, offset):
    """Check if the piece at the given offset collides with the board boundaries or existing blocks."""
    px, py = offset
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                if (py + y >= BOARD_HEIGHT or
                        px + x < 0 or
                        px + x >= BOARD_WIDTH or
                        board[py + y][px + x]):
                    return True
    return False


def place_piece(board, piece, offset, color):
    """Lock the piece into the board."""
    px, py = offset
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                board[py + y][px + x] = color


def clear_lines(board):
    """Clear completed lines and return the new board along with the number of cleared lines."""
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    cleared = BOARD_HEIGHT - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [0] * BOARD_WIDTH)
    return new_board, cleared


def rotate(piece):
    """Rotate the piece clockwise."""
    return [list(row) for row in zip(*piece[::-1])]


def main():
    pygame.init()
    # Extra width for UI info (score, level, next piece)
    screen = pygame.display.set_mode((WINDOW_WIDTH + 150, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetris (Pygame Version)")
    clock = pygame.time.Clock()

    # Initialize game state
    board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
    score = 0
    level = 1
    lines = 0

    # Choose first pieces
    piece_type = random.choice(list(PIECES))
    next_piece_type = random.choice(list(PIECES))
    piece = PIECES[piece_type]
    color = COLORS[piece_type]
    offset = [BOARD_WIDTH // 2 - len(piece[0]) // 2, 0]
    fall_time = 0
    fall_speed = 0.5  # initial fall speed in seconds

    running = True
    while running:
        screen.fill((20, 20, 20))
        fall_time += clock.get_rawtime() / 1000
        clock.tick(FPS)

        # Automatic piece fall
        if fall_time > fall_speed:
            offset[1] += 1
            if check_collision(board, piece, offset):
                offset[1] -= 1
                place_piece(board, piece, offset, color)
                board, cleared = clear_lines(board)
                lines += cleared
                score += cleared * 100
                # Level up after clearing 10 lines
                if lines >= 10:
                    level += 1
                    lines = 0
                    fall_speed *= 0.9  # Increase speed
                # Prepare next piece
                piece_type = next_piece_type
                piece = PIECES[piece_type]
                color = COLORS[piece_type]
                next_piece_type = random.choice(list(PIECES))
                offset = [BOARD_WIDTH // 2 - len(piece[0]) // 2, 0]
                # Check if the new piece collides immediately (Game Over)
                if check_collision(board, piece, offset):
                    draw_text(screen, "GAME OVER", 40, 50, 250, (255, 0, 0))
                    pygame.display.update()
                    pygame.time.wait(2000)
                    running = False
            fall_time = 0

        # Event handling for user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Move left
                if event.key == pygame.K_LEFT:
                    if not check_collision(board, piece, [offset[0] - 1, offset[1]]):
                        offset[0] -= 1
                # Move right
                elif event.key == pygame.K_RIGHT:
                    if not check_collision(board, piece, [offset[0] + 1, offset[1]]):
                        offset[0] += 1
                # Soft drop: move down faster with collision check
                elif event.key == pygame.K_DOWN:
                    offset[1] += 1
                    if check_collision(board, piece, offset):
                        offset[1] -= 1
                # Rotate piece
                elif event.key == pygame.K_UP:
                    rotated = rotate(piece)
                    if not check_collision(board, rotated, offset):
                        piece = rotated
                # Hard drop with spacebar
                elif event.key == pygame.K_SPACE:
                    while not check_collision(board, piece, [offset[0], offset[1] + 1]):
                        offset[1] += 1
                    # Lock the piece after hard drop
                    place_piece(board, piece, offset, color)
                    board, cleared = clear_lines(board)
                    lines += cleared
                    score += cleared * 100
                    if lines >= 10:
                        level += 1
                        lines = 0
                        fall_speed *= 0.9
                    piece_type = next_piece_type
                    piece = PIECES[piece_type]
                    color = COLORS[piece_type]
                    next_piece_type = random.choice(list(PIECES))
                    offset = [BOARD_WIDTH // 2 - len(piece[0]) // 2, 0]
                    if check_collision(board, piece, offset):
                        draw_text(screen, "GAME OVER", 40, 50, 250, (255, 0, 0))
                        pygame.display.update()
                        pygame.time.wait(2000)
                        running = False

        # Draw current board and falling piece
        draw_board(screen, board)
        draw_piece(screen, piece, offset, color)

        # UI: Score, Level, and Next Piece Preview
        draw_text(screen, f"Score: {score}", 24, WINDOW_WIDTH + 20, 20)
        draw_text(screen, f"Level: {level}", 24, WINDOW_WIDTH + 20, 60)
        draw_text(screen, "Next:", 24, WINDOW_WIDTH + 20, 120)

        # Draw next piece preview
        next_piece = PIECES[next_piece_type]
        next_color = COLORS[next_piece_type]
        for y, row in enumerate(next_piece):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, next_color,
                                     (WINDOW_WIDTH + 20 + x * BLOCK_SIZE, 150 + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, (30, 30, 30),
                                     (WINDOW_WIDTH + 20 + x * BLOCK_SIZE, 150 + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
