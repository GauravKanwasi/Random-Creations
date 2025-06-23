import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Neon Paddle Ball")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_BLUE = (0, 195, 255)
NEON_PINK = (255, 0, 128)
NEON_GREEN = (57, 255, 20)
NEON_PURPLE = (180, 0, 255)
BACKGROUND = (10, 10, 30)

# Particle class for visual effects
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.life = random.randint(20, 40)
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        return self.life > 0
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

# Ball properties
class Ball:
    def __init__(self):
        self.radius = 12
        self.reset()
        self.trail = []
        self.max_trail = 10
        self.color = NEON_BLUE
    
    def reset(self):
        self.x = screen_width // 2
        self.y = screen_height // 3
        angle = random.uniform(math.pi/4, 3*math.pi/4)
        speed = random.uniform(6, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
    
    def update(self):
        # Add current position to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
        
        # Update position
        self.x += self.vx
        self.y += self.vy
    
    def draw(self, surface):
        # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            size = self.radius * (i / len(self.trail))
            color = (min(255, self.color[0] + 50), 
                     min(255, self.color[1] + 50), 
                     min(255, self.color[2] + 50))
            pygame.draw.circle(surface, color, (int(trail_x), int(trail_y)), int(size))
        
        # Draw ball
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius - 4, 2)
        
        # Draw inner glow
        for i in range(3):
            pygame.draw.circle(surface, (*self.color[:2], min(255, self.color[2] + 50*i)), 
                              (int(self.x), int(self.y)), self.radius - i*2, 1)

# Paddle properties
class Paddle:
    def __init__(self):
        self.width = 120
        self.height = 20
        self.x = (screen_width - self.width) // 2
        self.y = screen_height - self.height - 20
        self.speed = 8
        self.color = NEON_PINK
        self.glow = 0
    
    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x + self.width < screen_width:
            self.x += self.speed
        
        # Decrease glow effect over time
        self.glow = max(0, self.glow - 0.5)
    
    def draw(self, surface):
        # Draw glow effect when hit
        if self.glow > 0:
            glow_surf = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*self.color, int(100 * self.glow)), 
                            (10, 10, self.width, self.height), border_radius=10)
            surface.blit(glow_surf, (self.x - 10, self.y - 10))
        
        # Draw paddle with rounded corners
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), border_radius=10)
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.width, self.height), 2, border_radius=10)
        
        # Draw inner details
        pygame.draw.line(surface, NEON_PURPLE, (self.x + 10, self.y + self.height//2), 
                         (self.x + self.width - 10, self.y + self.height//2), 2)

# Game class to manage state
class Game:
    def __init__(self):
        self.ball = Ball()
        self.paddle = Paddle()
        self.particles = []
        self.score = 0
        self.lives = 3
        self.game_state = "playing"  # "playing", "game_over"
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 72, bold=True)
        self.title_glow = 0
        self.title_dir = 1
    
    def create_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
    
    def update(self):
        keys = pygame.key.get_pressed()
        self.paddle.update(keys)
        
        if self.game_state == "playing":
            self.ball.update()
            
            # Check for collisions with walls
            if self.ball.x - self.ball.radius < 0:
                self.ball.x = self.ball.radius
                self.ball.vx = abs(self.ball.vx)
                self.create_particles(self.ball.x, self.ball.y, NEON_GREEN, 5)
            elif self.ball.x + self.ball.radius > screen_width:
                self.ball.x = screen_width - self.ball.radius
                self.ball.vx = -abs(self.ball.vx)
                self.create_particles(self.ball.x, self.ball.y, NEON_GREEN, 5)
                
            if self.ball.y - self.ball.radius < 0:
                self.ball.y = self.ball.radius
                self.ball.vy = abs(self.ball.vy)
                self.create_particles(self.ball.x, self.ball.y, NEON_GREEN, 5)
            
            # Check for collision with paddle
            if (self.ball.y + self.ball.radius > self.paddle.y and 
                self.ball.x > self.paddle.x and self.ball.x < self.paddle.x + self.paddle.width):
                self.ball.y = self.paddle.y - self.ball.radius
                self.ball.vy = -abs(self.ball.vy)
                
                # Add angle based on where the ball hits the paddle
                relative_x = (self.ball.x - (self.paddle.x + self.paddle.width/2)) / (self.paddle.width/2)
                self.ball.vx = relative_x * 8
                
                # Create particles and visual effects
                self.create_particles(self.ball.x, self.ball.y, NEON_PINK, 15)
                self.paddle.glow = 5
                self.score += 1
            
            # Check if ball falls off the bottom
            if self.ball.y - self.ball.radius > screen_height:
                self.lives -= 1
                self.create_particles(self.ball.x, screen_height, NEON_PURPLE, 20)
                if self.lives > 0:
                    self.ball.reset()
                else:
                    self.game_state = "game_over"
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Update title glow effect
        self.title_glow += 0.05 * self.title_dir
        if self.title_glow > 5 or self.title_glow < 0:
            self.title_dir *= -1
    
    def draw(self, surface):
        # Draw background
        surface.fill(BACKGROUND)
        
        # Draw grid pattern for background
        for y in range(0, screen_height, 30):
            alpha = 30 + 20 * math.sin(pygame.time.get_ticks() / 2000 + y/100)
            pygame.draw.line(surface, (*NEON_PURPLE[:2], int(alpha)), 
                            (0, y), (screen_width, y), 1)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(surface)
        
        # Draw game elements
        self.ball.draw(surface)
        self.paddle.draw(surface)
        
        # Draw score and lives
        score_text = self.font.render(f"Score: {self.score}", True, NEON_GREEN)
        lives_text = self.font.render(f"Lives: {self.lives}", True, NEON_BLUE)
        surface.blit(score_text, (20, 20))
        surface.blit(lives_text, (screen_width - lives_text.get_width() - 20, 20))
        
        # Draw game over screen
        if self.game_state == "game_over":
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("GAME OVER", True, NEON_PINK)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press SPACE to restart", True, NEON_GREEN)
            
            surface.blit(game_over_text, (screen_width//2 - game_over_text.get_width()//2, 
                                         screen_height//2 - 60))
            surface.blit(score_text, (screen_width//2 - score_text.get_width()//2, 
                                    screen_height//2))
            surface.blit(restart_text, (screen_width//2 - restart_text.get_width()//2, 
                                      screen_height//2 + 60))
        
        # Draw title with glow effect
        title_text = self.title_font.render("NEON PADDLE", True, NEON_BLUE)
        for offset in range(1, int(self.title_glow) + 1):
            glow_color = (min(255, NEON_BLUE[0] + offset*10), 
                          min(255, NEON_BLUE[1] + offset*10), 
                          min(255, NEON_BLUE[2] + offset*10))
            glow_surf = self.title_font.render("NEON PADDLE", True, glow_color)
            surface.blit(glow_surf, (screen_width//2 - glow_surf.get_width()//2 - offset, 
                                  20 - offset))
            surface.blit(glow_surf, (screen_width//2 - glow_surf.get_width()//2 + offset, 
                                  20 + offset))
        
        surface.blit(title_text, (screen_width//2 - title_text.get_width()//2, 20))
    
    def reset_game(self):
        self.ball.reset()
        self.paddle = Paddle()
        self.particles = []
        self.score = 0
        self.lives = 3
        self.game_state = "playing"

# Create game instance
game = Game()

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE and game.game_state == "game_over":
                game.reset_game()
    
    # Update game state
    game.update()
    
    # Draw everything
    game.draw(screen)
    
    # Update display
    pygame.display.flip()
    
    # Limit to 60 frames per second
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
