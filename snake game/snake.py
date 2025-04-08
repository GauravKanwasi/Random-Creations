import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")

# Clock to control the frame rate
clock = pygame.time.Clock()

# Snake properties
snake_block_size = 10
snake_speed = 15

# Font for displaying score
font_style = pygame.font.SysFont(None, 50)

def our_snake(snake_block_size, snake_list):
    for x in snake_list:
        pygame.draw.rect(screen, BLACK, [x[0], x[1], snake_block_size, snake_block_size])

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [SCREEN_WIDTH / 6 - mesg.get_width() / 2, SCREEN_HEIGHT / 3])

def gameLoop():
    game_over = False
    game_close = False

    x1 = SCREEN_WIDTH / 2
    y1 = SCREEN_HEIGHT / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    foodx = round(random.randrange(0, SCREEN_WIDTH - snake_block_size) / 10.0) * 10.0
    foody = round(random.randrange(0, SCREEN_HEIGHT - snake_block_size) / 10.0) * 10.0

    while not game_over:

        while game_close == True:
            screen.fill(WHITE)
            message("You Lost! Press Q-Quit or C-Play Again", RED)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block_size
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block_size
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block_size
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block_size
                    x1_change = 0

        if x1 >= SCREEN_WIDTH or x1 < 0 or y1 >= SCREEN_HEIGHT or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change
        screen.fill(WHITE)
        pygame.draw.rect(screen, GREEN, [foodx, foody, snake_block_size, snake_block_size])
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(snake_block_size, snake_List)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, SCREEN_WIDTH - snake_block_size) / 10.0) * 10.0
            foody = round(random.randrange(0, SCREEN_HEIGHT - snake_block_size) / 10.0) * 10.0
            Length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

gameLoop()
