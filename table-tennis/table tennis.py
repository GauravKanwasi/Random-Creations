import pygame
import random
import sys
import math
import json
from enum import Enum
from pygame import gfxdraw

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 110
BALL_SIZE = 18
FPS = 120
TARGET_SCORE = 7
MAX_SPEED = 14
PARTICLE_COUNT = 15

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 100)
RED = (255, 70, 70)
BLUE = (50, 100, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
DARK_BLUE = (5, 5, 30)
LIGHT_BLUE = (100, 150, 255)
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 0, 150)
COURT_COLOR = (5, 10, 40)

# Game states
class GameState(Enum):
    START = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    HIGH_SCORES = 4
    OPTIONS = 5

# Particle types
class ParticleType(Enum):
    TRAIL = 0
    IMPACT = 1
    SCORE = 2

# Paddle class with advanced physics
class Paddle:
    def __init__(self, x, color, name):
        self.x = x
        self.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.color = color
        self.speed = 7
        self.score = 0
        self.hit_timer = 0
        self.original_height = PADDLE_HEIGHT
        self.height = PADDLE_HEIGHT
        self.boost_timer = 0
        self.name = name
        self.momentum = 0
        
    def move(self, up=True):
        if up and self.y > 0:
            self.y -= self.speed
            self.momentum = -0.5
        elif not up and self.y < WINDOW_HEIGHT - self.height:
            self.y += self.speed
            self.momentum = 0.5
            
    def draw(self):
        # Draw glow effect
        if self.hit_timer > 0:
            glow_color = (min(255, self.color[0] + 150), 
                          min(255, self.color[1] + 150), 
                          min(255, self.color[2] + 150))
            for i in range(5, 0, -1):
                alpha = 100 - i*20
                glow_surf = pygame.Surface((PADDLE_WIDTH + i*4, self.height + i*4), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*glow_color, alpha), 
                                (0, 0, PADDLE_WIDTH + i*4, self.height + i*4), 
                                border_radius=10)
                screen.blit(glow_surf, (self.x - i*2 - 2, self.y - i*2))
            self.hit_timer -= 1
        
        # Draw paddle with gradient
        for i in range(int(self.height)):
            color_factor = 1 - abs(i - self.height/2) / (self.height/2)
            shade = (
                max(0, min(255, self.color[0] * color_factor)),
                max(0, min(255, self.color[1] * color_factor)),
                max(0, min(255, self.color[2] * color_factor))
            pygame.draw.line(screen, shade, (self.x, self.y + i), 
                           (self.x + PADDLE_WIDTH, self.y + i))
        
        # Draw outline
        pygame.draw.rect(screen, WHITE, (self.x, self.y, PADDLE_WIDTH, self.height), 
                         2, border_radius=5)
        
        # Draw boost indicator
        if self.boost_timer > 0:
            pygame.draw.rect(screen, NEON_BLUE, 
                           (self.x - 10, self.y + self.height - self.boost_timer, 5, self.boost_timer))
            self.boost_timer -= 1
            if self.boost_timer == 0:
                self.height = self.original_height
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, PADDLE_WIDTH, self.height)
    
    def activate_boost(self):
        self.height = self.original_height * 1.5
        self.boost_timer = self.height

# Ball class with spin physics
class Ball:
    def __init__(self):
        self.reset()
        self.trail = []
        self.spin = 0
        self.impact_timer = 0
        self.last_hit_paddle = None
        
    def reset(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        angle = random.uniform(math.pi/6, math.pi/3)
        direction = random.choice([-1, 1])
        self.speed_x = 5 * direction
        self.speed_y = 5 * math.sin(angle)
        self.trail = []
        self.spin = 0
        self.impact_timer = 0
        self.last_hit_paddle = None
        
    def move(self):
        # Apply spin effect
        self.speed_y += self.spin * 0.05
        self.spin *= 0.98  # Spin decay
        
        # Move ball
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Add current position to trail
        self.trail.append((self.x, self.y, self.speed_x, self.speed_y))
        if len(self.trail) > 15:
            self.trail.pop(0)
        
        # Bounce off top and bottom
        if self.y <= BALL_SIZE//2:
            self.y = BALL_SIZE//2
            self.speed_y = abs(self.speed_y) * 0.95
        elif self.y >= WINDOW_HEIGHT - BALL_SIZE//2:
            self.y = WINDOW_HEIGHT - BALL_SIZE//2
            self.speed_y = -abs(self.speed_y) * 0.95
            
        if self.impact_timer > 0:
            self.impact_timer -= 1
        
    def draw(self):
        # Draw trail with dynamic colors
        for i, (x, y, sx, sy) in enumerate(self.trail):
            alpha = 255 * (i / len(self.trail))
            size = max(2, BALL_SIZE - i//2)
            speed_factor = min(1.0, math.sqrt(sx*sx + sy*sy) / MAX_SPEED)
            
            # Color based on speed
            r = int(255 * speed_factor)
            g = int(150 * (1 - speed_factor))
            b = int(255 * (1 - speed_factor))
            
            pygame.draw.circle(screen, (r, g, b, int(alpha)), 
                             (int(x), int(y)), size//2)
        
        # Draw ball with glow
        if self.impact_timer > 0:
            glow_size = BALL_SIZE + self.impact_timer
            glow_surf = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 200, 100, 100), 
                            (glow_size, glow_size), glow_size)
            screen.blit(glow_surf, (int(self.x - glow_size), int(self.y - glow_size)))
        
        # Draw ball
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), BALL_SIZE//2)
        
        # Draw spin indicator
        if abs(self.spin) > 0.1:
            spin_direction = 1 if self.spin > 0 else -1
            start_angle = pygame.time.get_ticks() / 20
            end_angle = start_angle + 120 + abs(self.spin)*30
            pygame.draw.arc(screen, NEON_PINK, 
                         [self.x - BALL_SIZE, self.y - BALL_SIZE, 
                          BALL_SIZE*2, BALL_SIZE*2],
                         math.radians(start_angle), math.radians(end_angle), 2)
        
    def get_rect(self):
        return pygame.Rect(self.x - BALL_SIZE//2, self.y - BALL_SIZE//2, 
                         BALL_SIZE, BALL_SIZE)

# Particle system with multiple effects
class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_particles(self, x, y, ptype=ParticleType.IMPACT, count=PARTICLE_COUNT, color=None):
        for _ in range(count):
            if ptype == ParticleType.IMPACT:
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(1, 5)
                self.particles.append({
                    'x': x,
                    'y': y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'size': random.randint(2, 6),
                    'lifetime': random.randint(15, 30),
                    'color': color or (random.randint(200, 255), random.randint(200, 255), 255),
                    'type': ptype
                })
            elif ptype == ParticleType.TRAIL:
                self.particles.append({
                    'x': x,
                    'y': y,
                    'vx': 0,
                    'vy': 0,
                    'size': random.randint(1, 3),
                    'lifetime': random.randint(10, 20),
                    'color': color or (100, 150, 255),
                    'type': ptype
                })
            elif ptype == ParticleType.SCORE:
                angle = random.uniform(-math.pi/3, math.pi/3) + (math.pi if random.random() > 0.5 else 0)
                speed = random.uniform(3, 8)
                self.particles.append({
                    'x': x,
                    'y': y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'size': random.randint(3, 7),
                    'lifetime': random.randint(25, 40),
                    'color': color or (random.randint(200, 255), 255, random.randint(100, 200)),
                    'type': ptype
                })
    
    def update(self):
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            
            if p['type'] != ParticleType.TRAIL:
                p['vy'] += 0.1  # Gravity
            
            p['lifetime'] -= 1
            
            if p['lifetime'] <= 0:
                self.particles.remove(p)
    
    def draw(self):
        for p in self.particles:
            alpha = min(255, p['lifetime'] * 8)
            size = p['size'] * (p['lifetime'] / 20) if p['type'] == ParticleType.SCORE else p['size']
            pygame.draw.circle(screen, (*p['color'], alpha), 
                             (int(p['x']), int(p['y'])), 
                             int(size))

# Game class with advanced features
class Game:
    def __init__(self):
        self.player = Paddle(70, GREEN, "PLAYER")
        self.opponent = Paddle(WINDOW_WIDTH - 70 - PADDLE_WIDTH, RED, "CPU")
        self.ball = Ball()
        self.particles = ParticleSystem()
        self.font_large = pygame.font.SysFont('Arial', 90, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 50, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 32)
        self.font_tiny = pygame.font.SysFont('Arial', 24)
        self.state = GameState.START
        self.difficulty = 2  # 1: Easy, 2: Medium, 3: Hard
        self.opponent_reaction = {1: 0.2, 2: 0.3, 3: 0.4}
        self.target_score = TARGET_SCORE
        self.winner = None
        self.flash_timer = 0
        self.screen_shake = 0
        self.camera_offset = [0, 0]
        self.high_scores = self.load_high_scores()
        self.sound_enabled = True
        self.last_score_time = 0
        self.ball_trail_timer = 0
        self.power_up_timer = 0
        self.power_up_pos = [0, 0]
        self.power_up_active = False
        self.power_up_type = 0
        
        # Create background surface
        self.background = self.create_background()
        
        # Load sounds
        try:
            # Placeholder for actual sound files
            self.sounds = {
                'hit': pygame.mixer.Sound(pygame.mixer.Sound(bytes(random.randint(0, 255) for _ in range(44))),
                'score': pygame.mixer.Sound(pygame.mixer.Sound(bytes(random.randint(0, 255) for _ in range(44))),
                'powerup': pygame.mixer.Sound(pygame.mixer.Sound(bytes(random.randint(0, 255) for _ in range(44)))
            }
            for sound in self.sounds.values():
                sound.set_volume(0.5)
        except:
            self.sound_enabled = False
        
    def create_background(self):
        bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        bg.fill(COURT_COLOR)
        
        # Draw court pattern
        for x in range(0, WINDOW_WIDTH, 40):
            for y in range(0, WINDOW_HEIGHT, 40):
                if (x//40 + y//40) % 2 == 0:
                    pygame.draw.rect(bg, (10, 15, 50), (x, y, 40, 40), 1)
        
        # Draw center line
        for y in range(0, WINDOW_HEIGHT, 25):
            pygame.draw.line(bg, (100, 150, 255, 150), (WINDOW_WIDTH//2, y), (WINDOW_WIDTH//2, y + 12), 3)
        
        # Draw court outline with neon effect
        pygame.draw.rect(bg, NEON_BLUE, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 6, border_radius=2)
        pygame.draw.rect(bg, (100, 200, 255), (3, 3, WINDOW_WIDTH-6, WINDOW_HEIGHT-6), 2, border_radius=2)
        
        return bg
        
    def load_high_scores(self):
        try:
            with open('high_scores.json', 'r') as f:
                return json.load(f)
        except:
            return [{"name": "Player", "score": 7, "difficulty": 2},
                    {"name": "CPU", "score": 5, "difficulty": 3},
                    {"name": "Guest", "score": 3, "difficulty": 2}]
    
    def save_high_scores(self):
        with open('high_scores.json', 'w') as f:
            json.dump(self.high_scores, f)
    
    def add_high_score(self, name, score, difficulty):
        self.high_scores.append({"name": name, "score": score, "difficulty": difficulty})
        self.high_scores.sort(key=lambda x: (x["difficulty"], x["score"]), reverse=True)
        self.high_scores = self.high_scores[:5]  # Keep top 5
        self.save_high_scores()
    
    def draw_start_screen(self):
        # Animated background
        t = pygame.time.get_ticks() / 1000
        for y in range(WINDOW_HEIGHT):
            wave = math.sin(y/50 + t) * 10
            color = (10, 15 + int(30 * abs(math.sin(y/100 + t))), 
                    40 + int(50 * abs(math.sin(y/70 + t*0.7))))
            pygame.draw.line(screen, color, (0, y), (WINDOW_WIDTH, y))
        
        # Title with glow
        title = self.font_large.render("PONG PRO", True, NEON_BLUE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 150))
        
        # Title glow effect
        for i in range(10, 0, -1):
            alpha = 30 - i*3
            glow_surf = pygame.Surface((title_rect.width + i*10, title_rect.height + i*10), pygame.SRCALPHA)
            glow_text = self.font_large.render("PONG PRO", True, (*NEON_BLUE, alpha))
            glow_surf.blit(glow_text, (i*5, i*5))
            screen.blit(glow_surf, (title_rect.x - i*5, title_rect.y - i*5))
        
        screen.blit(title, title_rect)
        
        # Difficulty indicator
        diff_colors = [GREEN, YELLOW, RED]
        pygame.draw.rect(screen, (30, 30, 60), 
                       (WINDOW_WIDTH//2 - 120, 280, 240, 70), border_radius=15)
        pygame.draw.rect(screen, diff_colors[self.difficulty-1], 
                       (WINDOW_WIDTH//2 - 115, 285, 230, 60), border_radius=12)
        
        diff_text = self.font_medium.render(
            f"{['EASY', 'MEDIUM', 'HARD'][self.difficulty-1]}", True, WHITE)
        screen.blit(diff_text, (WINDOW_WIDTH//2 - diff_text.get_width()//2, 295))
        
        # Menu options
        options = [
            ("START GAME", GameState.PLAYING),
            ("HIGH SCORES", GameState.HIGH_SCORES),
            ("OPTIONS", GameState.OPTIONS),
            ("QUIT", None)
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (text, state) in enumerate(options):
            y_pos = 400 + i * 70
            hover = (WINDOW_WIDTH//2 - 150 < mouse_pos[0] < WINDOW_WIDTH//2 + 150 and 
                     y_pos - 25 < mouse_pos[1] < y_pos + 25)
            
            color = NEON_BLUE if hover else WHITE
            pygame.draw.rect(screen, (20, 25, 60, 180) if hover else (10, 15, 40, 150), 
                          (WINDOW_WIDTH//2 - 150, y_pos - 30, 300, 60), 
                          border_radius=10)
            pygame.draw.rect(screen, (100, 150, 255, 80) if hover else (50, 100, 200, 80), 
                          (WINDOW_WIDTH//2 - 150, y_pos - 30, 300, 60), 
                          3, border_radius=10)
            
            text_surf = self.font_medium.render(text, True, color)
            screen.blit(text_surf, (WINDOW_WIDTH//2 - text_surf.get_width()//2, y_pos - 20))
        
        # Footer
        footer = self.font_tiny.render("Use W/S to move paddle, P to pause", True, GRAY)
        screen.blit(footer, (WINDOW_WIDTH//2 - footer.get_width()//2, WINDOW_HEIGHT - 50))
        
    def draw_pause_screen(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("GAME PAUSED", True, YELLOW)
        screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, 200))
        
        options = [
            ("RESUME", GameState.PLAYING),
            ("RESTART", "restart"),
            ("MAIN MENU", GameState.START),
            ("QUIT", "quit")
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (text, action) in enumerate(options):
            y_pos = 300 + i * 70
            hover = (WINDOW_WIDTH//2 - 150 < mouse_pos[0] < WINDOW_WIDTH//2 + 150 and 
                     y_pos - 25 < mouse_pos[1] < y_pos + 25)
            
            color = NEON_BLUE if hover else WHITE
            pygame.draw.rect(screen, (20, 25, 60, 180) if hover else (10, 15, 40, 150), 
                          (WINDOW_WIDTH//2 - 150, y_pos - 30, 300, 60), 
                          border_radius=10)
            pygame.draw.rect(screen, (100, 150, 255, 80) if hover else (50, 100, 200, 80), 
                          (WINDOW_WIDTH//2 - 150, y_pos - 30, 300, 60), 
                          3, border_radius=10)
            
            text_surf = self.font_medium.render(text, True, color)
            screen.blit(text_surf, (WINDOW_WIDTH//2 - text_surf.get_width()//2, y_pos - 20))
        
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
        
        # Draw trophy if high score
        is_high_score = any(self.player.score > hs["score"] and self.difficulty >= hs["difficulty"] 
                            for hs in self.high_scores)
        if is_high_score:
            trophy_color = (255, 215, 0)
            pygame.draw.circle(screen, trophy_color, (WINDOW_WIDTH//2, 320), 40)
            pygame.draw.rect(screen, trophy_color, (WINDOW_WIDTH//2 - 20, 320, 40, 60))
            pygame.draw.polygon(screen, trophy_color, [
                (WINDOW_WIDTH//2 - 40, 380),
                (WINDOW_WIDTH//2 + 40, 380),
                (WINDOW_WIDTH//2 + 30, 400),
                (WINDOW_WIDTH//2 - 30, 400)
            ])
            high_score_text = self.font_small.render("NEW HIGH SCORE!", True, trophy_color)
            screen.blit(high_score_text, (WINDOW_WIDTH//2 - high_score_text.get_width()//2, 420))
        
        # Buttons
        options = [
            ("PLAY AGAIN", "restart"),
            ("MAIN MENU", GameState.START),
            ("QUIT", "quit")
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (text, action) in enumerate(options):
            y_pos = 500 + i * 70
            hover = (WINDOW_WIDTH//2 - 150 < mouse_pos[0] < WINDOW_WIDTH//2 + 150 and 
                     y_pos - 25 < mouse_pos[1] < y_pos + 25)
            
            color = NEON_BLUE if hover else WHITE
            pygame.draw.rect(screen, (20, 25, 60, 180) if hover else (10, 15, 40, 150), 
                          (WINDOW_WIDTH//2 - 150, y_pos - 30, 300, 60), 
                          border_radius=10)
            pygame.draw.rect(screen, (100, 150, 255, 80) if hover else (50, 100, 200, 80), 
                          (WINDOW_WIDTH//2 - 150, y_pos - 30, 300, 60), 
                          3, border_radius=10)
            
            text_surf = self.font_medium.render(text, True, color)
            screen.blit(text_surf, (WINDOW_WIDTH//2 - text_surf.get_width()//2, y_pos - 20))
    
    def draw_high_scores(self):
        # Background
        screen.fill(DARK_BLUE)
        
        # Title
        title = self.font_large.render("HIGH SCORES", True, NEON_BLUE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 50))
        
        # Draw high scores table
        headers = ["Rank", "Name", "Score", "Difficulty"]
        header_y = 150
        col_widths = [100, 300, 150, 150]
        
        # Draw headers
        for i, header in enumerate(headers):
            x_pos = 150 + sum(col_widths[:i])
            text = self.font_medium.render(header, True, NEON_PINK)
            screen.blit(text, (x_pos + (col_widths[i] - text.get_width())//2, header_y))
        
        # Draw scores
        for i, score in enumerate(self.high_scores[:10]):  # Show top 10
            y_pos = header_y + 70 + i * 50
            rank = self.font_small.render(f"{i+1}.", True, YELLOW)
            name = self.font_small.render(score["name"], True, WHITE)
            score_val = self.font_small.render(str(score["score"]), True, GREEN)
            diff = self.font_small.render(["Easy", "Medium", "Hard"][score["difficulty"]-1], True, 
                                       [GREEN, YELLOW, RED][score["difficulty"]-1])
            
            screen.blit(rank, (150 + (col_widths[0] - rank.get_width())//2, y_pos))
            screen.blit(name, (250 + (col_widths[1] - name.get_width())//2, y_pos))
            screen.blit(score_val, (550 + (col_widths[2] - score_val.get_width())//2, y_pos))
            screen.blit(diff, (700 + (col_widths[3] - diff.get_width())//2, y_pos))
        
        # Back button
        pygame.draw.rect(screen, (30, 40, 100), (50, 50, 150, 50), border_radius=10)
        back_text = self.font_small.render("BACK", True, NEON_BLUE)
        screen.blit(back_text, (125 - back_text.get_width()//2, 65))
        
    def draw_options(self):
        # Background
        screen.fill(DARK_BLUE)
        
        # Title
        title = self.font_large.render("OPTIONS", True, NEON_BLUE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 50))
        
        # Sound toggle
        sound_text = self.font_medium.render("SOUND:", True, WHITE)
        screen.blit(sound_text, (WINDOW_WIDTH//2 - 250, 150))
        
        sound_state = "ON" if self.sound_enabled else "OFF"
        sound_btn = pygame.draw.rect(screen, (30, 40, 100), 
                                  (WINDOW_WIDTH//2 + 50, 150, 100, 50), border_radius=10)
        sound_text = self.font_medium.render(sound_state, True, NEON_BLUE)
        screen.blit(sound_text, (WINDOW_WIDTH//2 + 100 - sound_text.get_width()//2, 160))
        
        # Back button
        pygame.draw.rect(screen, (30, 40, 100), (50, 50, 150, 50), border_radius=10)
        back_text = self.font_small.render("BACK", True, NEON_BLUE)
        screen.blit(back_text, (125 - back_text.get_width()//2, 65))
        
    def enhanced_ai(self):
        reaction = self.opponent_reaction[self.difficulty]
        error = random.uniform(-40, 40) * (4 - self.difficulty)
        
        # Predict ball position
        predict_x = self.ball.x + self.ball.speed_x * 10
        predict_y = self.ball.y + self.ball.speed_y * 10 + error
        
        # Add difficulty-based delay
        if random.random() < reaction:
            # Move toward predicted ball position
            if self.opponent.y + PADDLE_HEIGHT/2 < predict_y - 20:
                self.opponent.move(up=False)
            elif self.opponent.y + PADDLE_HEIGHT/2 > predict_y + 20:
                self.opponent.move(up=True)
                
    def check_collision(self):
        ball_rect = self.ball.get_rect()
        
        # Player collision
        if ball_rect.colliderect(self.player.get_rect()):
            # Calculate hit position effect
            relative_y = (self.player.y + self.player.height/2 - self.ball.y) / (self.player.height/2)
            
            # Speed increase based on paddle speed
            speed_boost = 1.0 + abs(self.player.momentum) * 0.5
            
            self.ball.speed_x = abs(self.ball.speed_x) * speed_boost
            self.ball.speed_y = -relative_y * 8 * speed_boost
            
            # Apply spin from paddle movement
            self.ball.spin = self.player.momentum * 3
            
            self.player.hit_timer = 10
            self.ball.last_hit_paddle = self.player
            self.ball.impact_timer = 10
            self.particles.add_particles(self.ball.x, self.ball.y, color=self.player.color)
            
            if self.sound_enabled:
                self.sounds['hit'].play()
                
        # Opponent collision
        if ball_rect.colliderect(self.opponent.get_rect()):
            relative_y = (self.opponent.y + self.opponent.height/2 - self.ball.y) / (self.opponent.height/2)
            
            speed_boost = 1.0 + abs(self.opponent.momentum) * 0.5
            self.ball.speed_x = -abs(self.ball.speed_x) * speed_boost
            self.ball.speed_y = -relative_y * 8 * speed_boost
            
            self.ball.spin = self.opponent.momentum * 3
            self.opponent.hit_timer = 10
            self.ball.last_hit_paddle = self.opponent
            self.ball.impact_timer = 10
            self.particles.add_particles(self.ball.x, self.ball.y, color=self.opponent.color)
            
            if self.sound_enabled:
                self.sounds['hit'].play()
                
        # Cap ball speed
        self.ball.speed_x = max(min(self.ball.speed_x, MAX_SPEED), -MAX_SPEED)
        self.ball.speed_y = max(min(self.ball.speed_y, MAX_SPEED), -MAX_SPEED)
        
    def spawn_power_up(self):
        self.power_up_active = True
        self.power_up_timer = 300  # 5 seconds at 60 FPS
        self.power_up_pos = [
            random.randint(WINDOW_WIDTH//4, 3*WINDOW_WIDTH//4),
            random.randint(100, WINDOW_HEIGHT - 100)
        ]
        self.power_up_type = random.randint(0, 1)  # 0 = speed boost, 1 = paddle boost
        
    def draw_power_up(self):
        if not self.power_up_active:
            return
            
        t = pygame.time.get_ticks() / 200
        size = 20 + math.sin(t) * 5
        
        if self.power_up_type == 0:  # Speed boost
            color = NEON_PINK
            pygame.draw.circle(screen, color, (int(self.power_up_pos[0]), int(self.power_up_pos[1])), int(size))
            pygame.draw.circle(screen, (255, 200, 255), (int(self.power_up_pos[0]), int(self.power_up_pos[1])), int(size/2))
        else:  # Paddle boost
            color = NEON_BLUE
            pygame.draw.rect(screen, color, 
                          (self.power_up_pos[0] - size/2, self.power_up_pos[1] - size/2, size, size), 
                          border_radius=5)
            pygame.draw.rect(screen, (200, 230, 255), 
                          (self.power_up_pos[0] - size/4, self.power_up_pos[1] - size/4, size/2, size/2), 
                          border_radius=3)
            
        # Draw glow
        glow_surf = pygame.Surface((int(size*4), int(size*4)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, 50), (size*2, size*2), size*1.8)
        screen.blit(glow_surf, (int(self.power_up_pos[0] - size*2), int(self.power_up_pos[1] - size*2)))
        
    def check_power_up_collision(self):
        if not self.power_up_active:
            return False
            
        paddle = self.player if self.ball.last_hit_paddle == self.opponent else self.opponent
        dist = math.sqrt((self.ball.x - self.power_up_pos[0])**2 + (self.ball.y - self.power_up_pos[1])**2)
        
        if dist < 30:  # Collision radius
            if self.power_up_type == 0:  # Speed boost
                self.ball.speed_x *= 1.5
                self.ball.speed_y *= 1.5
            else:  # Paddle boost
                paddle.activate_boost()
                
            self.power_up_active = False
            self.particles.add_particles(self.power_up_pos[0], self.power_up_pos[1], 
                                      ParticleType.SCORE, count=30, color=(255, 255, 200))
            
            if self.sound_enabled:
                self.sounds['powerup'].play()
                
            return True
                
        return False
        
    def reset_game(self):
        self.player.score = 0
        self.opponent.score = 0
        self.ball.reset()
        self.particles = ParticleSystem()
        self.state = GameState.PLAYING
        self.winner = None
        self.flash_timer = 0
        self.screen_shake = 0
        self.camera_offset = [0, 0]
        self.last_score_time = pygame.time.get_ticks()
        self.power_up_active = False
        # Set opponent speed based on difficulty
        self.opponent.speed = {1: 5, 2: 7, 3: 9}[self.difficulty]
        
    def apply_screen_shake(self, intensity=10):
        self.screen_shake = intensity
        
    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pong Pro - Advanced Table Tennis")
        pygame.mouse.set_visible(False)
        
        running = True
        while running:
            # Handle screen shake
            if self.screen_shake > 0:
                self.camera_offset = [random.randint(-3, 3), random.randint(-3, 3)]
                self.screen_shake -= 1
            else:
                self.camera_offset = [0, 0]
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == GameState.PLAYING:
                            self.state = GameState.PAUSED
                        elif self.state == GameState.PAUSED:
                            self.state = GameState.PLAYING
                        elif self.state in [GameState.HIGH_SCORES, GameState.OPTIONS]:
                            self.state = GameState.START
                    
                    elif self.state == GameState.START:
                        if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                            self.difficulty = int(event.unicode)
                            
                    elif self.state == GameState.PLAYING:
                        if event.key == pygame.K_p:
                            self.state = GameState.PAUSED
                            
                    elif self.state == GameState.PAUSED:
                        if event.key == pygame.K_q:
                            running = False
                            
                    elif self.state == GameState.GAME_OVER:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.state == GameState.START:
                        # Check menu options
                        options_y = [400, 470, 540, 610]
                        for i, y in enumerate(options_y):
                            if (WINDOW_WIDTH//2 - 150 < mouse_pos[0] < WINDOW_WIDTH//2 + 150 and 
                                y - 30 < mouse_pos[1] < y + 30):
                                if i == 0:  # Start Game
                                    self.state = GameState.PLAYING
                                elif i == 1:  # High Scores
                                    self.state = GameState.HIGH_SCORES
                                elif i == 2:  # Options
                                    self.state = GameState.OPTIONS
                                elif i == 3:  # Quit
                                    running = False
                    
                    elif self.state == GameState.PAUSED:
                        options_y = [300, 370, 440, 510]
                        for i, y in enumerate(options_y):
                            if (WINDOW_WIDTH//2 - 150 < mouse_pos[0] < WINDOW_WIDTH//2 + 150 and 
                                y - 30 < mouse_pos[1] < y + 30):
                                if i == 0:  # Resume
                                    self.state = GameState.PLAYING
                                elif i == 1:  # Restart
                                    self.reset_game()
                                elif i == 2:  # Main Menu
                                    self.state = GameState.START
                                elif i == 3:  # Quit
                                    running = False
                    
                    elif self.state == GameState.GAME_OVER:
                        options_y = [500, 570, 640]
                        for i, y in enumerate(options_y):
                            if (WINDOW_WIDTH//2 - 150 < mouse_pos[0] < WINDOW_WIDTH//2 + 150 and 
                                y - 30 < mouse_pos[1] < y + 30):
                                if i == 0:  # Play Again
                                    self.reset_game()
                                elif i == 1:  # Main Menu
                                    self.state = GameState.START
                                elif i == 2:  # Quit
                                    running = False
                    
                    elif self.state == GameState.HIGH_SCORES or self.state == GameState.OPTIONS:
                        if 50 < mouse_pos[0] < 200 and 50 < mouse_pos[1] < 100:
                            self.state = GameState.START
            
            # Draw everything with camera offset
            screen.fill(BLACK)
            
            if self.state == GameState.START:
                self.draw_start_screen()
                
            elif self.state == GameState.PLAYING:
                # Draw background with offset
                screen.blit(self.background, (self.camera_offset[0], self.camera_offset[1]))
                
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
                
                # Add trail particles occasionally
                self.ball_trail_timer += 1
                if self.ball_trail_timer > 2:
                    self.particles.add_particles(self.ball.x, self.ball.y, ptype=ParticleType.TRAIL, count=2)
                    self.ball_trail_timer = 0
                
                # Spawn power-ups
                current_time = pygame.time.get_ticks()
                if not self.power_up_active and current_time - self.last_score_time > 10000:  # 10 seconds
                    if random.random() < 0.01:  # 1% chance per frame
                        self.spawn_power_up()
                
                # Update power-up
                if self.power_up_active:
                    self.power_up_timer -= 1
                    if self.power_up_timer <= 0:
                        self.power_up_active = False
                    else:
                        self.check_power_up_collision()
                
                # Scoring
                if self.ball.x <= 0:
                    self.opponent.score += 1
                    self.flash_timer = 15
                    self.apply_screen_shake(15)
                    self.last_score_time = pygame.time.get_ticks()
                    
                    if self.opponent.score >= self.target_score:
                        self.winner = "OPPONENT"
                        self.state = GameState.GAME_OVER
                        if self.player.score > 0:
                            self.add_high_score("Player", self.player.score, self.difficulty)
                    else:
                        self.ball.reset()
                        self.power_up_active = False
                        
                    if self.sound_enabled:
                        self.sounds['score'].play()
                        
                elif self.ball.x >= WINDOW_WIDTH:
                    self.player.score += 1
                    self.flash_timer = 15
                    self.apply_screen_shake(15)
                    self.last_score_time = pygame.time.get_ticks()
                    
                    if self.player.score >= self.target_score:
                        self.winner = "PLAYER"
                        self.state = GameState.GAME_OVER
                        self.add_high_score("Player", self.player.score, self.difficulty)
                    else:
                        self.ball.reset()
                        self.power_up_active = False
                        
                    if self.sound_enabled:
                        self.sounds['score'].play()
                
                # Draw scores with offset
                player_score = self.font_large.render(str(self.player.score), True, GREEN)
                screen.blit(player_score, 
                          (WINDOW_WIDTH//4 - player_score.get_width()//2 + self.camera_offset[0], 
                           20 + self.camera_offset[1]))
                
                opponent_score = self.font_large.render(str(self.opponent.score), True, RED)
                screen.blit(opponent_score, 
                          (3*WINDOW_WIDTH//4 - opponent_score.get_width()//2 + self.camera_offset[0], 
                           20 + self.camera_offset[1]))
                
                # Draw game objects with offset
                self.player.draw()
                self.opponent.draw()
                self.ball.draw()
                self.particles.draw()
                self.draw_power_up()
                
                # Flash effect on score
                if self.flash_timer > 0:
                    flash = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                    flash.fill((255, 255, 255, min(150, self.flash_timer * 15)))
                    screen.blit(flash, (0, 0))
                    self.flash_timer -= 1
                    
                # Draw difficulty indicator
                diff_text = self.font_small.render(
                    f"Difficulty: {['Easy', 'Medium', 'Hard'][self.difficulty-1]}", True, GRAY)
                screen.blit(diff_text, (WINDOW_WIDTH - diff_text.get_width() - 20 + self.camera_offset[0], 
                                     WINDOW_HEIGHT - 40 + self.camera_offset[1]))
                    
            elif self.state == GameState.PAUSED:
                # Draw game in background
                screen.blit(self.background, (0, 0))
                self.player.draw()
                self.opponent.draw()
                self.ball.draw()
                self.particles.draw()
                self.draw_power_up()
                
                # Draw pause overlay
                self.draw_pause_screen()
                
            elif self.state == GameState.GAME_OVER:
                # Draw game in background
                screen.blit(self.background, (0, 0))
                self.player.draw()
                self.opponent.draw()
                self.ball.draw()
                self.particles.draw()
                
                # Draw game over overlay
                self.draw_game_over_screen()
                
            elif self.state == GameState.HIGH_SCORES:
                self.draw_high_scores()
                
            elif self.state == GameState.OPTIONS:
                self.draw_options()
            
            # Draw FPS counter
            fps_text = self.font_tiny.render(f"FPS: {int(clock.get_fps())}", True, GRAY)
            screen.blit(fps_text, (10, 10))
            
            # Draw custom cursor
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.circle(screen, NEON_BLUE, mouse_pos, 8, 2)
            pygame.draw.circle(screen, (200, 230, 255), mouse_pos, 4)
            
            pygame.display.flip()
            clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
