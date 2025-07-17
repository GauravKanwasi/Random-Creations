import pygame
import random
import sys
import math
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 15
FPS = 60
TARGET_SCORE = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
DARK_BLUE = (0, 0, 50)
LIGHT_BLUE = (100, 100, 255)

# Game states
class GameState(Enum):
    START = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

# Paddle class
class Paddle:
    def __init__(self, x, color):
        self.x = x
        self.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.color = color
        self.speed = 7
        self.score = 0
        self.hit_timer = 0
        
    def move(self, up=True):
        if up and self.y > 0:
            self.y -= self.speed
        elif not up and self.y < WINDOW_HEIGHT - PADDLE_HEIGHT:
            self.y += self.speed
            
    def draw(self):
        color = YELLOW if self.hit_timer > 0 else self.color
        if self.hit_timer > 0:
            self.hit_timer -= 1
            
        pygame.draw.rect(screen, color, (self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT), 
                         border_radius=5, border_width=2)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball class with improved physics
class Ball:
    def __init__(self):
        self.reset()
        self.trail = []
        
    def reset(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        angle = random.uniform(math.pi/6, math.pi/3)
        direction = random.choice([-1, 1])
        self.speed_x = 5 * direction
        self.speed_y = 5 * math.sin(angle)
        self.trail = []
        
    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Add current position to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        # Bounce off top and bottom
        if self.y <= BALL_SIZE//2 or self.y >= WINDOW_HEIGHT - BALL_SIZE//2:
            self.speed_y = -self.speed_y
            
    def draw(self):
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = 255 * (i / len(self.trail))
            size = max(1, BALL_SIZE - i)
            pygame.draw.circle(screen, (200, 200, 255, int(alpha)), 
                             (int(pos[0]), int(pos[1])), size//2)
        
        # Draw ball
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), BALL_SIZE//2)
        pygame.draw.circle(screen, LIGHT_BLUE, (int(self.x), int(self.y)), 
                         BALL_SIZE//2 - 2, 1)
        
    def get_rect(self):
        return pygame.Rect(self.x - BALL_SIZE//2, self.y - BALL_SIZE//2, 
                         BALL_SIZE, BALL_SIZE)

# Particle system with physics-based effects
class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_particles(self, x, y, count=8):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.randint(2, 5),
                'lifetime': random.randint(15, 30),
                'color': (random.randint(200, 255), random.randint(200, 255), 255)
            })
    
    def update(self):
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1  # Gravity
            p['lifetime'] -= 1
            
            if p['lifetime'] <= 0:
                self.particles.remove(p)
    
    def draw(self):
        for p in self.particles:
            alpha = min(255, p['lifetime'] * 8)
            pygame.draw.circle(screen, p['color'], 
                             (int(p['x']), int(p['y'])), 
                             p['size'])

# Game class with improved structure
class Game:
    def __init__(self):
        self.player = Paddle(50, GREEN)
        self.opponent = Paddle(WINDOW_WIDTH - 50 - PADDLE_WIDTH, RED)
        self.ball = Ball()
        self.particles = ParticleSystem()
        self.font_large = pygame.font.SysFont('Arial', 80, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 50)
        self.font_small = pygame.font.SysFont('Arial', 30)
        self.state = GameState.START
        self.difficulty = 2  # 1: Easy, 2: Medium, 3: Hard
        self.opponent_reaction = {1: 0.2, 2: 0.3, 3: 0.4}
        self.target_score = TARGET_SCORE
        self.winner = None
        self.flash_timer = 0
        
        # Create background surface
        self.background = self.create_background()
        
    def create_background(self):
        bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        bg.fill(DARK_BLUE)
        
        # Draw court lines
        pygame.draw.line(bg, GRAY, (WINDOW_WIDTH//2, 0), (WINDOW_WIDTH//2, WINDOW_HEIGHT), 2)
        
        # Draw dashed center line
        for y in range(0, WINDOW_HEIGHT, 20):
            pygame.draw.line(bg, GRAY, (WINDOW_WIDTH//2, y), (WINDOW_WIDTH//2, y + 10), 2)
            
        # Draw court outline
        pygame.draw.rect(bg, BLUE, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 4, border_radius=10)
        
        return bg
        
    def draw_start_screen(self):
        # Draw gradient background
        for y in range(WINDOW_HEIGHT):
            color = (0, 0, 50 + int(205 * y / WINDOW_HEIGHT))
            pygame.draw.line(screen, color, (0, y), (WINDOW_WIDTH, y))
        
        # Title
        title = self.font_large.render("PONG PRO", True, WHITE)
        title_shadow = self.font_large.render("PONG PRO", True, GRAY)
        screen.blit(title_shadow, (WINDOW_WIDTH//2 - title.get_width()//2 + 3, 150 + 3))
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 150))
        
        # Difficulty indicator
        diff_colors = [GREEN, YELLOW, RED]
        pygame.draw.rect(screen, diff_colors[self.difficulty-1], 
                       (WINDOW_WIDTH//2 - 100, 300, 200, 50), border_radius=10)
        diff_text = self.font_small.render(
            f"{['EASY', 'MEDIUM', 'HARD'][self.difficulty-1]}", True, BLACK)
        screen.blit(diff_text, (WINDOW_WIDTH//2 - diff_text.get_width()//2, 310))
        
        # Instructions
        start_text = self.font_small.render("PRESS SPACE TO START", True, WHITE)
        screen.blit(start_text, (WINDOW_WIDTH//2 - start_text.get_width()//2, 400))
        
        control_text = self.font_small.render("CONTROLS: W/S KEYS TO MOVE, P TO PAUSE", True, WHITE)
        screen.blit(control_text, (WINDOW_WIDTH//2 - control_text.get_width()//2, 450))
        
        diff_select = self.font_small.render("PRESS 1-3 TO CHANGE DIFFICULTY", True, WHITE)
        screen.blit(diff_select, (WINDOW_WIDTH//2 - diff_select.get_width()//2, 500))
        
    def draw_pause_screen(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("GAME PAUSED", True, YELLOW)
        screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, 200))
        
        resume_text = self.font_medium.render("Press P to Resume", True, WHITE)
        screen.blit(resume_text, (WINDOW_WIDTH//2 - resume_text.get_width()//2, 300))
        
        quit_text = self.font_medium.render("Press Q to Quit", True, WHITE)
        screen.blit(quit_text, (WINDOW_WIDTH//2 - quit_text.get_width()//2, 370))
        
    def draw_game_over_screen(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        winner_color = GREEN if self.winner == "PLAYER" else RED
        winner_text = self.font_large.render(f"{self.winner} WINS!", True, winner_color)
        screen.blit(winner_text, (WINDOW_WIDTH//2 - winner_text.get_width()//2, 150))
        
        score_text = self.font_medium.render(
            f"Final Score: {self.player.score} - {self.opponent.score}", True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, 250))
        
        restart_text = self.font_medium.render("Press R to Restart", True, GREEN)
        screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, 320))
        
        quit_text = self.font_medium.render("Press Q to Quit", True, RED)
        screen.blit(quit_text, (WINDOW_WIDTH//2 - quit_text.get_width()//2, 380))
        
    def enhanced_ai(self):
        reaction = self.opponent_reaction[self.difficulty]
        error = random.uniform(-40, 40) * (4 - self.difficulty)
        target_y = self.ball.y + error
        
        # Move toward predicted ball position
        if self.opponent.y + PADDLE_HEIGHT/2 < target_y - 20:
            self.opponent.move(up=False)
        elif self.opponent.y + PADDLE_HEIGHT/2 > target_y + 20:
            self.opponent.move(up=True)
                
    def check_collision(self):
        ball_rect = self.ball.get_rect()
        
        # Player collision
        if ball_rect.colliderect(self.player.get_rect()):
            # Calculate hit position effect
            relative_y = (self.player.y + PADDLE_HEIGHT/2 - self.ball.y) / (PADDLE_HEIGHT/2)
            self.ball.speed_x = abs(self.ball.speed_x) * 1.05
            self.ball.speed_y = -relative_y * 8
            
            self.player.hit_timer = 10
            self.particles.add_particles(self.ball.x, self.ball.y)
                
        # Opponent collision
        if ball_rect.colliderect(self.opponent.get_rect()):
            relative_y = (self.opponent.y + PADDLE_HEIGHT/2 - self.ball.y) / (PADDLE_HEIGHT/2)
            self.ball.speed_x = -abs(self.ball.speed_x) * 1.05
            self.ball.speed_y = -relative_y * 8
            
            self.opponent.hit_timer = 10
            self.particles.add_particles(self.ball.x, self.ball.y)
                
        # Cap ball speed
        max_speed = 12
        self.ball.speed_x = max(min(self.ball.speed_x, max_speed), -max_speed)
        self.ball.speed_y = max(min(self.ball.speed_y, max_speed), -max_speed)
        
    def reset_game(self):
        self.player.score = 0
        self.opponent.score = 0
        self.ball.reset()
        self.particles = ParticleSystem()
        self.state = GameState.PLAYING
        self.winner = None
        self.flash_timer = 0
        # Set opponent speed based on difficulty
        self.opponent.speed = {1: 5, 2: 7, 3: 9}[self.difficulty]
        
    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pong Pro")
        
        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if self.state == GameState.START:
                        if event.key == pygame.K_SPACE:
                            self.state = GameState.PLAYING
                        elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                            self.difficulty = int(event.unicode)
                            
                    elif self.state == GameState.PLAYING:
                        if event.key == pygame.K_p:
                            self.state = GameState.PAUSED
                            
                    elif self.state == GameState.PAUSED:
                        if event.key == pygame.K_p:
                            self.state = GameState.PLAYING
                        elif event.key == pygame.K_q:
                            running = False
                            
                    elif self.state == GameState.GAME_OVER:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            running = False
            
            # Game state processing
            if self.state == GameState.START:
                self.draw_start_screen()
                
            elif self.state == GameState.PLAYING:
                # Player controls
                keys = pygame.key.get_pressed()
                if keys[pygame.K_w]:
                    self.player.move(up=True)
                if keys[pygame.K_s]:
                    self.player.move(up=False)
                    
                # AI movement
                self.enhanced_ai()
                
                # Ball movement
                self.ball.move()
                self.check_collision()
                
                # Update particles
                self.particles.update()
                
                # Scoring
                if self.ball.x <= 0:
                    self.opponent.score += 1
                    self.flash_timer = 10
                    if self.opponent.score >= self.target_score:
                        self.winner = "OPPONENT"
                        self.state = GameState.GAME_OVER
                    else:
                        self.ball.reset()
                        
                elif self.ball.x >= WINDOW_WIDTH:
                    self.player.score += 1
                    self.flash_timer = 10
                    if self.player.score >= self.target_score:
                        self.winner = "PLAYER"
                        self.state = GameState.GAME_OVER
                    else:
                        self.ball.reset()
                
                # Drawing
                screen.blit(self.background, (0, 0))
                
                # Draw scores
                player_score = self.font_large.render(str(self.player.score), True, GREEN)
                screen.blit(player_score, (WINDOW_WIDTH//4 - player_score.get_width()//2, 20))
                
                opponent_score = self.font_large.render(str(self.opponent.score), True, RED)
                screen.blit(opponent_score, (3*WINDOW_WIDTH//4 - opponent_score.get_width()//2, 20))
                
                # Draw game objects
                self.player.draw()
                self.opponent.draw()
                self.ball.draw()
                self.particles.draw()
                
                # Flash effect on score
                if self.flash_timer > 0:
                    flash = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                    flash.fill((255, 255, 255, min(150, self.flash_timer * 25)))
                    screen.blit(flash, (0, 0))
                    self.flash_timer -= 1
                    
            elif self.state == GameState.PAUSED:
                self.draw_pause_screen()
                
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over_screen()
            
            # Draw FPS counter
            fps_text = self.font_small.render(f"FPS: {int(clock.get_fps())}", True, GRAY)
            screen.blit(fps_text, (10, 10))
            
            pygame.display.flip()
            clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
