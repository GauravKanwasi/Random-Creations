import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 15
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Initialize screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Table Tennis")
clock = pygame.time.Clock()

class Paddle:
    def __init__(self, x, color):
        self.x = x
        self.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.color = color
        self.speed = 7
        self.score = 0
        
    def move(self, up=True):
        if up and self.y > 0:
            self.y -= self.speed
        elif not up and self.y < WINDOW_HEIGHT - PADDLE_HEIGHT:
            self.y += self.speed
            
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT)

class Ball:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = WINDOW_WIDTH // 2 - BALL_SIZE // 2
        self.y = WINDOW_HEIGHT // 2 - BALL_SIZE // 2
        self.speed_x = random.choice([-4, 4])
        self.speed_y = random.uniform(-4, 4)
        
    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Bounce off top and bottom
        if self.y <= 0 or self.y >= WINDOW_HEIGHT - BALL_SIZE:
            self.speed_y = -self.speed_y
            
    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, BALL_SIZE, BALL_SIZE))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, BALL_SIZE, BALL_SIZE)

def main():
    # Create game objects
    player = Paddle(50, GREEN)
    opponent = Paddle(WINDOW_WIDTH - 50 - PADDLE_WIDTH, RED)
    ball = Ball()
    
    # Font for score display
    font = pygame.font.Font(None, 74)
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # Input handling
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.move(up=True)
        if keys[pygame.K_s]:
            player.move(up=False)
            
        # Simple AI for opponent
        if opponent.y + PADDLE_HEIGHT/2 < ball.y:
            opponent.move(up=False)
        if opponent.y + PADDLE_HEIGHT/2 > ball.y:
            opponent.move(up=True)
            
        # Update ball position
        ball.move()
        
        # Ball collision with paddles
        if ball.get_rect().colliderect(player.get_rect()):
            ball.speed_x = abs(ball.speed_x) * 1.1  # Increase speed slightly
            ball.speed_y += random.uniform(-0.5, 0.5)  # Add some randomness
            
        if ball.get_rect().colliderect(opponent.get_rect()):
            ball.speed_x = -abs(ball.speed_x) * 1.1  # Increase speed slightly
            ball.speed_y += random.uniform(-0.5, 0.5)  # Add some randomness
            
        # Score points
        if ball.x <= 0:
            opponent.score += 1
            ball.reset()
        elif ball.x >= WINDOW_WIDTH - BALL_SIZE:
            player.score += 1
            ball.reset()
            
        # Draw everything
        screen.fill(BLACK)
        
        # Draw center line
        pygame.draw.aaline(screen, WHITE, (WINDOW_WIDTH//2, 0), (WINDOW_WIDTH//2, WINDOW_HEIGHT))
        
        # Draw scores
        player_text = font.render(str(player.score), True, GREEN)
        opponent_text = font.render(str(opponent.score), True, RED)
        screen.blit(player_text, (WINDOW_WIDTH//4, 20))
        screen.blit(opponent_text, (3*WINDOW_WIDTH//4, 20))
        
        # Draw game objects
        player.draw()
        opponent.draw()
        ball.draw()
        
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
