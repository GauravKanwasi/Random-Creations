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
TARGET_SCORE = 5  # Score needed to win the game

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)

# Initialize screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Table Tennis Pro")

# Paddle class for player and opponent
class Paddle:
    def __init__(self, x, color):
        self.x = x
        self.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.color = color
        self.speed = 7  # Default speed, adjusted for opponent in Game
        self.score = 0
        self.hit_timer = 0  # Timer for flash effect
        
    def move(self, up=True):
        if up and self.y > 0:
            self.y -= self.speed
        elif not up and self.y < WINDOW_HEIGHT - PADDLE_HEIGHT:
            self.y += self.speed
            
    def draw(self):
        # Flash yellow when hit, then revert to original color
        if self.hit_timer > 0:
            color = YELLOW
            self.hit_timer -= 1
        else:
            color = self.color
        pygame.draw.rect(screen, color, (self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT), border_radius=5)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball class with enhanced trail effect
class Ball:
    def __init__(self):
        self.reset()
        self.trail = []  # For ball trail effect
        
    def reset(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.speed_x = random.choice([-4, 4])
        self.speed_y = random.uniform(-4, 4)
        self.trail = []
        
    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        # Bounce off top and bottom
        if self.y <= 0 or self.y >= WINDOW_HEIGHT - BALL_SIZE:
            self.speed_y = -self.speed_y
            # Uncomment to play wall sound (requires sound file)
            # game.wall_sound.play()
            
    def draw(self):
        # Draw trail with fading shades of gray
        for i, pos in enumerate(self.trail):
            shade = 255 - int(200 * i / len(self.trail))
            color = (shade, shade, shade)
            size = BALL_SIZE // 2 - i // 3
            if size > 0:
                pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), size)
        # Draw ball
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), BALL_SIZE // 2)
        
    def get_rect(self):
        return pygame.Rect(self.x - BALL_SIZE // 2, self.y - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Particle class with fading effect
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.size = random.randint(2, 5)
        self.lifetime = random.randint(10, 20)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        
    def draw(self):
        if self.lifetime > 0:
            shade = int(255 * self.lifetime / 20)  # Fade based on lifetime
            color = (shade, shade, shade)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

# Game class managing the overall game
class Game:
    def __init__(self):
        self.player = Paddle(50, GREEN)
        self.opponent = Paddle(WINDOW_WIDTH - 50 - PADDLE_WIDTH, RED)
        self.ball = Ball()
        self.particles = []
        self.title_font = pygame.font.Font(None, 100)
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.state = "start"
        self.difficulty = 1  # 1: Easy, 2: Medium, 3: Hard
        self.opponent_reaction = {1: 0.1, 2: 0.2, 3: 0.3}
        self.paused = False
        self.flash_timer = 0
        self.fade_alpha = 0
        self.winner = None
        self.target_score = TARGET_SCORE
        
        # Gradient background for start screen
        self.gradient = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        for y in range(WINDOW_HEIGHT):
            color = (0 + int(100 * y / WINDOW_HEIGHT), 0 + int(100 * y / WINDOW_HEIGHT), 50 + int(205 * y / WINDOW_HEIGHT))
            pygame.draw.line(self.gradient, color, (0, y), (WINDOW_WIDTH, y))
        
        # Load sound effects (uncomment with sound files available)
        # self.hit_sound = pygame.mixer.Sound('hit.wav')
        # self.wall_sound = pygame.mixer.Sound('wall.wav')
        # self.score_sound = pygame.mixer.Sound('score.wav')
        
    def draw_start_screen(self):
        screen.blit(self.gradient, (0, 0))
        
        # Title with shadow
        title_shadow = self.title_font.render("Table Tennis Pro", True, GRAY)
        screen.blit(title_shadow, (WINDOW_WIDTH//2 - title_shadow.get_width()//2 + 2, WINDOW_HEIGHT//3 + 2))
        title = self.title_font.render("Table Tennis Pro", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT//3))
        
        # Instructions
        start_text = self.small_font.render("Press SPACE to start", True, WHITE)
        screen.blit(start_text, (WINDOW_WIDTH//2 - start_text.get_width()//2, WINDOW_HEIGHT//2))
        diff_text = self.small_font.render(f"Difficulty: {['Easy', 'Medium', 'Hard'][self.difficulty-1]} (1-3 to change)", True, WHITE)
        screen.blit(diff_text, (WINDOW_WIDTH//2 - diff_text.get_width()//2, 2*WINDOW_HEIGHT//3))
        
    def draw_pause_screen(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        pause_text = self.title_font.render("Paused", True, WHITE)
        screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, WINDOW_HEIGHT//2))
        resume_text = self.small_font.render("Press P to resume or Q to quit", True, WHITE)
        screen.blit(resume_text, (WINDOW_WIDTH//2 - resume_text.get_width()//2, 2*WINDOW_HEIGHT//3))
        
    def draw_game_over_screen(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        color = (self.fade_alpha, self.fade_alpha, self.fade_alpha)
        winner_text = self.title_font.render(f"{self.winner} Wins!", True, color)
        screen.blit(winner_text, (WINDOW_WIDTH//2 - winner_text.get_width()//2, WINDOW_HEIGHT//3))
        score_text = self.font.render(f"Final Score: {self.player.score} - {self.opponent.score}", True, color)
        screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, WINDOW_HEIGHT//2))
        options_text = self.small_font.render("Press R to restart or Q to quit", True, color)
        screen.blit(options_text, (WINDOW_WIDTH//2 - options_text.get_width()//2, 2*WINDOW_HEIGHT//3))
        
    def enhanced_ai(self):
        reaction = self.opponent_reaction[self.difficulty]
        # Add prediction error based on difficulty
        error = random.uniform(-50, 50) * (1 - (self.difficulty - 1) / 2)
        predicted_y = self.ball.y + self.ball.speed_y * 10 + error
        if random.random() < reaction:
            if self.opponent.y + PADDLE_HEIGHT/2 < predicted_y:
                self.opponent.move(up=False)
            elif self.opponent.y + PADDLE_HEIGHT/2 > predicted_y:
                self.opponent.move(up=True)
                
    def check_collision(self):
        if self.ball.get_rect().colliderect(self.player.get_rect()):
            self.ball.speed_x = abs(self.ball.speed_x) * 1.1
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.ball.speed_y -= 0.5
            elif keys[pygame.K_s]:
                self.ball.speed_y += 0.5
            self.player.hit_timer = 10  # Trigger flash
            for _ in range(5):
                self.particles.append(Particle(self.ball.x, self.ball.y))
            # Uncomment to play hit sound (requires sound file)
            # self.hit_sound.play()
                
        if self.ball.get_rect().colliderect(self.opponent.get_rect()):
            self.ball.speed_x = -abs(self.ball.speed_x) * 1.1
            self.ball.speed_y += random.uniform(-0.5, 0.5)
            self.opponent.hit_timer = 10  # Trigger flash
            for _ in range(5):
                self.particles.append(Particle(self.ball.x, self.ball.y))
            # Uncomment to play hit sound (requires sound file)
            # self.hit_sound.play()
                
        # Cap ball speed
        self.ball.speed_x = max(min(self.ball.speed_x, 10), -10)
        self.ball.speed_y = max(min(self.ball.speed_y, 10), -10)
        
    def reset_game(self):
        self.player.score = 0
        self.opponent.score = 0
        self.ball.reset()
        self.particles = []
        self.state = "playing"
        self.fade_alpha = 0
        self.winner = None
        
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == "start":
                        if event.key == pygame.K_SPACE:
                            self.state = "playing"
                            # Set opponent speed based on difficulty
                            self.opponent.speed = {1: 5, 2: 7, 3: 9}[self.difficulty]
                        elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                            self.difficulty = int(event.unicode)
                    elif self.state == "playing":
                        if event.key == pygame.K_p:
                            self.paused = not self.paused
                    elif self.state == "game_over":
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            running = False
                    if self.paused and event.key == pygame.K_q:
                        running = False
                            
            if self.state == "start":
                self.draw_start_screen()
                
            elif self.state == "playing":
                if self.paused:
                    self.draw_pause_screen()
                else:
                    # Input handling
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_w]:
                        self.player.move(up=True)
                    if keys[pygame.K_s]:
                        self.player.move(up=False)
                        
                    # Update game
                    self.enhanced_ai()
                    self.ball.move()
                    self.check_collision()
                    
                    # Update particles
                    for particle in self.particles[:]:
                        particle.update()
                        if particle.lifetime <= 0:
                            self.particles.remove(particle)
                    
                    # Score points
                    if self.ball.x <= 0:
                        self.opponent.score += 1
                        self.flash_timer = 6
                        # Uncomment to play score sound (requires sound file)
                        # self.score_sound.play()
                        if self.opponent.score >= self.target_score:
                            self.winner = "Opponent"
                            self.state = "game_over"
                        else:
                            self.ball.reset()
                    elif self.ball.x >= WINDOW_WIDTH - BALL_SIZE:
                        self.player.score += 1
                        self.flash_timer = 6
                        # Uncomment to play score sound (requires sound file)
                        # self.score_sound.play()
                        if self.player.score >= self.target_score:
                            self.winner = "Player"
                            self.state = "game_over"
                        else:
                            self.ball.reset()
                            
                    # Draw everything
                    screen.fill(BLACK)
                    
                    # Draw court details
                    pygame.draw.aaline(screen, WHITE, (WINDOW_WIDTH//2, 0), (WINDOW_WIDTH//2, WINDOW_HEIGHT))
                    pygame.draw.rect(screen, BLUE, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 5)
                    
                    # Draw net
                    for y in range(0, WINDOW_HEIGHT, 20):
                        pygame.draw.line(screen, WHITE, (WINDOW_WIDTH//2 - 2, y), (WINDOW_WIDTH//2 - 2, y + 10), 4)
                    
                    # Draw scores with labels
                    player_label = self.small_font.render("Player", True, GREEN)
                    screen.blit(player_label, (WINDOW_WIDTH//4 - player_label.get_width()//2, 20))
                    player_score = self.font.render(str(self.player.score), True, GREEN)
                    screen.blit(player_score, (WINDOW_WIDTH//4 - player_score.get_width()//2, 60))
                    opponent_label = self.small_font.render("Opponent", True, RED)
                    screen.blit(opponent_label, (3*WINDOW_WIDTH//4 - opponent_label.get_width()//2, 20))
                    opponent_score = self.font.render(str(self.opponent.score), True, RED)
                    screen.blit(opponent_score, (3*WINDOW_WIDTH//4 - opponent_score.get_width()//2, 60))
                    
                    # Draw game objects
                    self.player.draw()
                    self.opponent.draw()
                    self.ball.draw()
                    for particle in self.particles:
                        particle.draw()
                    
                    # Screen flash on score
                    if self.flash_timer > 0:
                        flash_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                        flash_overlay.fill(WHITE)
                        flash_overlay.set_alpha(100)
                        screen.blit(flash_overlay, (0, 0))
                        self.flash_timer -= 1
                        
            elif self.state == "game_over":
                if self.fade_alpha < 255:
                    self.fade_alpha += 5
                    if self.fade_alpha > 255:
                        self.fade_alpha = 255
                self.draw_game_over_screen()
            
            pygame.display.flip()
            clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
