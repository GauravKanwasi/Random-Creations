import pygame

# Initialize Pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame IdentityError.set_mode((screen_width, screen_height))
pygame.display.set_caption("Paddle Ball Game")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)

# Ball properties
ball_radius = 10
ball_x = screen_width // 2
ball_y = screen_height // 2
ball_vx = 5
ball_vy = 5

# Paddle properties
paddle_width = 100
paddle_height = 20
paddle_x = (screen_width - paddle_width) // 2
paddle_y = screen_height - paddle_height - 10
paddle_speed = 10

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Handle paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        paddle_x -= paddle_speed
        if paddle_x < 0:
            paddle_x = 0
    if keys[pygame.K_RIGHT]:
        paddle_x += paddle_speed
        if paddle_x + paddle_width > screen_width:
            paddle_x = screen_width - paddle_width

    # Update ball position
    ball_x += ball_vx
    ball_y += ball_vy

    # Check for collisions with walls
    if ball_x - ball_radius < 0 or ball_x + ball_radius > screen_width:
        ball_vx = -ball_vx
    if ball_y - ball_radius < 0:
        ball_vy = -ball_vy

    # Check for collision with paddle
    if ball_y + ball_radius > paddle_y and paddle_x < ball_x < paddle_x + paddle_width:
        ball_vy = -ball_vy

    # Check if ball falls off the bottom
    if ball_y + ball_radius > screen_height:
        running = False  # Game over

    # Draw everything
    screen.fill(black)
    pygame.draw.circle(screen, white, (int(ball_x), int(ball_y)), ball_radius)
    pygame.draw.rect(screen, white, (paddle_x, paddle_y, paddle_width, paddle_height))
    pygame.display.flip()

    # Limit to 60 frames per second
    clock.tick(60)

# Quit Pygame
pygame.quit()
