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
    """Draw the game board grid and filled blocks with highlights."""
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            if board[y][x]:
                color = board[y][x]
                pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                highlight_color = (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255))
                pygame.draw.rect(screen, highlight_color, (x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 5, 10, 10))
                pygame.draw.rect(screen, (30, 30, 30), (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_piece(screen, piece, offset, color):
    """Draw the current falling piece with highlights."""
    px, py = offset
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, color, ((px + x) * BLOCK_SIZE, (py + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                highlight_color = (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255))
                pygame.draw.rect(screen, highlight_color, ((px + x) * BLOCK_SIZE + 5, (py + y) * BLOCK_SIZE + 5, 10, 10))
                pygame.draw.rect(screen, (30, 30, 30), ((px + x) * BLOCK_SIZE, (py + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def check_collision(board, piece, offset):
    """Check if the piece at the given offset collides with the board boundaries or existing blocks."""
    px, py = offset
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                if (py + y >= BOARD_HEIGHT or px + x < 0 or px + x >= BOARD_WIDTH or board[py + y][px + x]):
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
    """Clear completed lines and return the new board, number of cleared lines, and their indices."""
    cleared_lines = []
    new_board = []
    for y, row in enumerate(board):
        if all(cell != 0 for cell in row):
            cleared_lines.append(y)
        else:
            new_board.append(row)
    for _ in range(len(cleared_lines)):
        new_board.insert(0, [0] * BOARD_WIDTH)
    return new_board, len(cleared_lines), cleared_lines

def rotate(piece):
    """Rotate the piece clockwise."""
    return [list(row) for row in zip(*piece[::-1])]

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH + 150, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetris (Enhanced Version)")
    clock = pygame.time.Clock()

    # Initialize game state
    board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
    score = 0
    level = 1
    lines = 0
    game_state = "playing"
    fall_time = 0
    fall_speed = 0.5  # Initial fall speed in seconds

    # Choose first pieces
    piece_type = random.choice(list(PIECES))
    next_piece_type = random.choice(list(PIECES))
    piece = PIECES[piece_type]
    color = COLORS[piece_type]
    offset = [BOARD_WIDTH // 2 - len(piece[0]) // 2, 0]

    running = True
    while running:
        clock.tick(FPS)

        if game_state == "playing":
            fall_time += clock.get_rawtime() / 1000
            if fall_time > fall_speed:
                offset[1] += 1
                if check_collision(board, piece, offset):
                    offset[1] -= 1
                    place_piece(board, piece, offset, color)
                    new_board, cleared, cleared_lines = clear_lines(board)
                    if cleared > 0:
                        game_state = "flashing"
                        flash_timer = 0.5
                        flashing_board = [row[:] for row in board]
                    else:
                        board = new_board
                        piece_type = next_piece_type
                        piece = PIECES[piece_type]
                        color = COLORS[piece_type]
                        next_piece_type = random.choice(list(PIECES))
                        offset = [BOARD_WIDTH // 2 - len(piece[0]) // 2, 0]
                        if check_collision(board, piece, offset):
                            game_state = "game_over"
                fall_time = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if not check_collision(board, piece, [offset[0] - 1, offset[1]]):
                            offset[0] -= 1
                    elif event.key == pygame.K_RIGHT:
                        if not check_collision(board, piece, [offset[0] + 1, offset[1]]):
                            offset[0] += 1
                    elif event.key == pygame.K_DOWN:
                        offset[1] += 1
                        if check_collision(board, piece, offset):
                            offset[1] -= 1
                    elif event.key == pygame.K_UP:
                        rotated = rotate(piece)
                        if not check_collision(board, rotated, offset):
                            piece = rotated
                    elif event.key == pygame.K_SPACE:
                        while not check_collision(board, piece, [offset[0], offset[1] + 1]):
                            offset[1] += 1
                        place_piece(board, piece, offset, color)
                        new_board, cleared, cleared_lines = clear_lines(board)
                        if cleared > 0:
                            game_state = "flashing"
                            flash_timer = 0.5
                            flashing_board = [row[:] for row in board]
                        else:
                            board = new_board
                            piece_type = next_piece_type
                            piece = PIECES[piece_type]
                            color = COLORS[piece_type]
                            next_piece_type = random.choice(list(PIECES))
                            offset = [BOARD_WIDTH // 2 - len(piece[0]) // 2, 0]
                            if check_collision(board, piece, offset):
                                game_state = "game_over"

            screen.fill((20, 20, 20))
            draw_board(screen, board)
            draw_piece(screen, piece, offset, color)

        elif game_state == "flashing":
            screen.fill((20, 20, 20))
            for y in range(BOARD_HEIGHT):
                for x in range(BOARD_WIDTH):
                    if y in cleared_lines:
                        color = (255, 255, 255) if (int(pygame.time.get_ticks() / 100) % 2) == 0 else flashing_board[y][x]
                    else:
                        color = flashing_board[y][x]
                    if color:
                        pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                        if y not in cleared_lines or (int(pygame.time.get_ticks() / 100) % 2) != 0:
                            highlight_color = (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255))
                            pygame.draw.rect(screen, highlight_color, (x * BLOCK_SIZE + 5, y * BLOCK_SIZE + 5, 10, 10))
                        pygame.draw.rect(screen, (30, 30, 30), (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)
            flash_timer -= clock.get_rawtime() / 1000
            if flash_timer <= 0:
                game_state = "playing"
                board = new_board
                score += cleared * 100
                lines += cleared
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
                    game_state = "game_over"

        elif game_state == "game_over":
            screen.fill((20, 20, 20))
            draw_board(screen, board)
            draw_text(screen, "GAME OVER", 40, 50, 250, (255, 0, 0))
            pygame.display.update()
            pygame.time.wait(2000)
            running = False

        # Draw UI
        draw_text(screen, f"Score: {score}", 24, WINDOW_WIDTH + 20, 20)
        draw_text(screen, f"Level: {level}", 24, WINDOW_WIDTH + 20, 60)
        draw_text(screen, "Next:", 24, WINDOW_WIDTH + 20, 120)
        next_piece = PIECES[next_piece_type]
        next_color = COLORS[next_piece_type]
        for y, row in enumerate(next_piece):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, next_color, (WINDOW_WIDTH + 20 + x * BLOCK_SIZE, 150 + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                    highlight_color = (min(next_color[0] + 50, 255), min(next_color[1] + 50, 255), min(next_color[2] + 50, 255))
                    pygame.draw.rect(screen, highlight_color, (WINDOW_WIDTH + 20 + x * BLOCK_SIZE + 5, 150 + y * BLOCK_SIZE + 5, 10, 10))
                    pygame.draw.rect(screen, (30, 30, 30), (WINDOW_WIDTH + 20 + x * BLOCK_SIZE, 150 + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Draw controls for usability
        draw_text(screen, "Controls:", 24, WINDOW_WIDTH + 20, 250)
        draw_text(screen, "Left: Move left", 20, WINDOW_WIDTH + 20, 280)
        draw_text(screen, "Right: Move right", 20, WINDOW_WIDTH + 20, 310)
        draw_text(screen, "Down: Soft drop", 20, WINDOW_WIDTH + 20, 340)
        draw_text(screen, "Up: Rotate", 20, WINDOW_WIDTH + 20, 370)
        draw_text(screen, "Space: Hard drop", 20, WINDOW_WIDTH + 20, 400)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
