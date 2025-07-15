import pygame
import random
import sys
import time
import os
import json
import logging
from enum import Enum
from typing import List, Tuple, Dict, Optional

# Setup logging
logging.basicConfig(filename='game.log', level=logging.INFO)

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
CARD_WIDTH, CARD_HEIGHT = 100, 150
FPS = 60
MAX_PARTICLES = 100
HINT_COOLDOWN = 10
SETTINGS_FILE = 'settings.json'

# Game States
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    SETTINGS = 4
    GAME_OVER = 5

# Colors
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'GRAY': (128, 128, 128),
    'BLUE': (0, 100, 255),
    'RED': (255, 50, 50),
    'GREEN': (50, 255, 50),
    'PURPLE': (147, 0, 211),
    'GOLD': (255, 215, 0),
    'COLORBLIND_RED': (200, 0, 0),
    'COLORBLIND_GREEN': (0, 150, 0),
    'HIGH_CONTRAST_BG': (0, 0, 0),
    'HIGH_CONTRAST_TEXT': (255, 255, 255)
}

# Screen setup
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Memory Card Game")
clock = pygame.time.Clock()

class Settings:
    """Class to manage game settings"""
    def __init__(self):
        self.sound_volume = 0.5
        self.music_volume = 0.3
        self.colorblind_mode = False
        self.show_particles = True
        self.high_contrast = False
        self.flip_speed = 8
        self.difficulty = "medium"
        self.music_files = ["background_music.mp3", "background_music2.mp3"]
        self.current_music = 0
        self.load()

    def load(self):
        """Load settings from file"""
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                self.__dict__.update(data)
        except FileNotFoundError:
            logging.info("No settings file found, using defaults")

    def save(self):
        """Save settings to file"""
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({
                'sound_volume': self.sound_volume,
                'music_volume': self.music_volume,
                'colorblind_mode': self.colorblind_mode,
                'show_particles': self.show_particles,
                'high_contrast': self.high_contrast,
                'flip_speed': self.flip_speed,
                'difficulty': self.difficulty,
                'current_music': self.current_music
            }, f)

    @property
    def card_color(self):
        return COLORS['COLORBLIND_RED'] if self.colorblind_mode else COLORS['BLUE']

    @property
    def match_color(self):
        return COLORS['COLORBLIND_GREEN'] if self.colorblind_mode else COLORS['GREEN']

# Initialize settings
settings = Settings()

# Asset loading with error handling
def load_sound(file: str) -> pygame.mixer.Sound:
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error as e:
        logging.error(f"Failed to load sound {file}: {e}")
        return pygame.mixer.Sound(buffer=bytearray(100))

def load_image(file: str, size: Tuple[int, int]) -> pygame.Surface:
    try:
        image = pygame.image.load(file).convert_alpha()
        return pygame.transform.scale(image, size)
    except pygame.error as e:
        logging.error(f"Failed to load image {file}: {e}")
        return pygame.Surface(size)

# Sound effects
sounds = {
    "flip": load_sound("flip.wav"),
    "match": load_sound("match.wav"),
    "hint": load_sound("hint.wav"),
    "click": load_sound("click.wav"),
    "background": None
}

# Load background music
if settings.music_files and os.path.exists(settings.music_files[settings.current_music]):
    try:
        pygame.mixer.music.load(settings.music_files[settings.current_music])
        pygame.mixer.music.set_volume(settings.music_volume)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        logging.error(f"Failed to load music {settings.music_files[settings.current_music]}: {e}")

class Particle:
    """Particle effect for matches"""
    def __init__(self, x: float, y: float):
        self.reset(x, y)

    def reset(self, x, y):
        self.x, self.y = x, y
        self.vx, self.vy = random.uniform(-1, 1), random.uniform(-2, -1)
        self.lifetime = random.randint(20, 60)
        self.color = random.choice([COLORS['GOLD'], COLORS['WHITE'], COLORS['PURPLE']])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 2)

class Button:
    """Interactive button with hover and click states"""
    def __init__(self, x, y, width, height, text, 
                 color=COLORS['BLUE'], hover_color=COLORS['PURPLE'], 
                 text_color=COLORS['WHITE']):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hover = False
        self.pressed = False
        self.disabled = False

    def draw(self, surface) -> pygame.Rect:
        if self.disabled:
            color = COLORS['GRAY']
        else:
            color = self.hover_color if (self.hover or self.pressed) else self.color
            
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        font = pygame.font.Font(None, 30)
        text_surf = font.render(self.text, True, 
                               COLORS['HIGH_CONTRAST_TEXT'] if settings.high_contrast 
                               else self.text_color)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))
        return self.rect

    def update(self, mouse_pos: Tuple[int, int]):
        self.hover = self.rect.collidepoint(mouse_pos)

class Card:
    """Game card with flip animation and states"""
    def __init__(self, x, y, value):
        self.x, self.y = x, y
        self.value = value
        self.revealed = False
        self.matched = False
        self.hover = False
        self.flip_progress = 0
        self.flip_direction = 0
        self.glow = 0
        self.font_size = 48

    def start_flip(self, to_front=True):
        """Start flip animation"""
        self.flip_direction = 1 if to_front else -1
        sounds["flip"].play()

    def update(self):
        """Update card state and animation"""
        if self.flip_direction:
            self.flip_progress += self.flip_direction * settings.flip_speed
            self.flip_progress = max(0, min(100, self.flip_progress))
            if self.flip_progress in [0, 100]:
                self.revealed = self.flip_progress == 100
                self.flip_direction = 0
                
        if self.glow > 0:
            self.glow -= 5

    def draw(self, surface) -> pygame.Rect:
        """Draw card with current state effects"""
        color = settings.match_color if self.matched else (
            COLORS['PURPLE'] if self.hover else settings.card_color
        )
        
        pygame.draw.rect(surface, color, 
                        (self.x, self.y, CARD_WIDTH, CARD_HEIGHT), 
                        border_radius=5)
        
        if self.revealed or self.matched:
            font = pygame.font.Font(None, self.font_size)
            text = font.render(str(self.value), True, COLORS['WHITE'])
            surface.blit(text, text.get_rect(
                center=(self.x + CARD_WIDTH // 2, 
                       self.y + CARD_HEIGHT // 2)))
        
        if self.glow > 0:
            glow_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (255, 255, 0, self.glow), 
                           (0, 0, CARD_WIDTH, CARD_HEIGHT))
            surface.blit(glow_surf, (self.x, self.y))
            
        return pygame.Rect(self.x, self.y, CARD_WIDTH, CARD_HEIGHT)

class Game:
    """Main game logic and state management"""
    def __init__(self, difficulty="medium"):
        self.difficulty = difficulty
        self.cards = self.setup_cards()
        self.selected_cards = []
        self.moves = self.matches = self.score = 0
        self.game_over = self.paused = False
        self.start_time = time.time()
        self.hint_timer = 0
        self.hint_available = True
        self.background = self.create_background()
        self.particle_manager = ParticleManager()
        
        # UI Elements
        self.pause_button = Button(WINDOW_WIDTH - 120, 10, 100, 40, "Pause")
        self.hint_button = Button(WINDOW_WIDTH - 230, 10, 100, 40, "Hint")
        self.tutorial_shown = False

    def create_background(self):
        """Create game background"""
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)).convert()
        surface.fill(COLORS['HIGH_CONTRAST_BG'] if settings.high_contrast 
                    else (50, 0, 100))
        return surface

    def setup_cards(self) -> List[Card]:
        """Create and arrange cards based on difficulty"""
        pairs = {"easy": 6, "medium": 8, "hard": 10}[self.difficulty]
        values = list(range(1, pairs + 1)) * 2
        random.shuffle(values)
        
        cols = {"easy": 3, "medium": 4, "hard": 5}[self.difficulty]
        rows = (len(values) + cols - 1) // cols
        
        padding_x = 50
        padding_y = 100
        spacing_x = (WINDOW_WIDTH - 2*padding_x) // (cols + 1)
        spacing_y = (WINDOW_HEIGHT - 2*padding_y) // (rows + 1)
        
        return [Card(padding_x + (i % cols) * spacing_x, 
                    padding_y + (i // cols) * spacing_y, 
                    values[i]) for i in range(len(values))]

    def handle_click(self, x, y):
        """Handle mouse click events"""
        if self.paused or self.game_over:
            return
            
        # Pause button
        if self.pause_button.rect.collidepoint(x, y):
            self.paused = True
            sounds["click"].play()
            return
            
        # Hint button
        if self.hint_button.rect.collidepoint(x, y) and self.hint_available:
            self.use_hint()
            return
            
        # Card clicks
        for card in self.cards:
            if (card.draw(screen).collidepoint(x, y) and 
                not card.matched and not card.revealed and 
                len(self.selected_cards) < 2):
                card.start_flip()
                self.selected_cards.append(card)
                
                if len(self.selected_cards) == 2:
                    self.moves += 1
                    if self.selected_cards[0].value == self.selected_cards[1].value:
                        pygame.time.set_timer(pygame.USEREVENT + 1, 500)
                        self.selected_cards[0].glow = self.selected_cards[1].glow = 100
                        self.score += 100 - int(time.time() - self.start_time)
                        sounds["match"].play()
                        if settings.show_particles:
                            for _ in range(20):
                                p = Particle(self.selected_cards[0].x + CARD_WIDTH // 2, 
                                           self.selected_cards[0].y + CARD_HEIGHT // 2)
                                self.particle_manager.add_particle(p)
                    else:
                        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
                        self.score = max(0, self.score - 10)
                    break

    def use_hint(self):
        """Activate hint feature"""
        unmatched = [c for c in self.cards if not c.matched]
        if len(unmatched) >= 2:
            value = random.choice([c.value for c in unmatched])
            matches = [c for c in unmatched if c.value == value]
            if len(matches) >= 2:
                for card in matches[:2]:
                    card.glow = 100
                self.hint_available = False
                self.hint_timer = time.time()
                sounds["hint"].play()
                pygame.time.set_timer(pygame.USEREVENT + 2, 2000)

    def update(self):
        """Update game state"""
        for card in self.cards:
            card.update()
            
        self.particle_manager.update()
        
        if not self.hint_available and time.time() - self.hint_timer > HINT_COOLDOWN:
            self.hint_available = True

    def draw(self, surface) -> List[pygame.Rect]:
        """Draw game elements"""
        dirty_rects = [surface.blit(self.background, (0, 0))]
        
        for card in self.cards:
            dirty_rects.append(card.draw(surface))
            
        for particle in self.particle_manager.particles:
            particle.draw(surface)
            
        dirty_rects.append(self.pause_button.draw(surface))
        dirty_rects.append(self.hint_button.draw(surface))
        
        if not self.hint_available:
            cooldown = int(HINT_COOLDOWN - (time.time() - self.hint_timer))
            font = pygame.font.Font(None, 24)
            text = font.render(f"{cooldown}s", True, COLORS['WHITE'])
            dirty_rects.append(surface.blit(text, 
                (self.hint_button.rect.centerx - 10, 
                 self.hint_button.rect.bottom + 5)))
        
        # Score and time
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, COLORS['WHITE'])
        time_text = font.render(f"Time: {int(time.time() - self.start_time)}s", 
                               True, COLORS['WHITE'])
        dirty_rects.append(surface.blit(score_text, (10, 10)))
        dirty_rects.append(surface.blit(time_text, (10, 50)))
        
        return dirty_rects

    def draw_tutorial(self, surface):
        """Display tutorial screen"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        messages = [
            "Welcome to Memory Card Game!",
            "Click two cards to flip them.",
            "Match pairs to score points.",
            "Use 'Hint' for help (cooldown applies).",
            "Press ESC to pause, R to restart, Q to quit to menu."
        ]
        
        font = pygame.font.Font(None, 32)
        for i, line in enumerate(messages):
            text = font.render(line, True, COLORS['WHITE'])
            rect = text.get_rect(center=(WINDOW_WIDTH//2, 200 + i*40))
            surface.blit(text, rect)
            
        pygame.display.flip()
        pygame.time.wait(5000)
        self.tutorial_shown = True

    def show_game_over(self, surface):
        """Display game over screen"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 48)
        text = font.render(f"Game Over! Score: {self.score}", True, COLORS['WHITE'])
        rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        surface.blit(text, rect)
        
        buttons = [
            Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 10, 200, 40, "Restart"),
            Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 60, 200, 40, "Main Menu")
        ]
        
        for button in buttons:
            button.draw(surface)
        
        pygame.display.flip()
        return buttons

class ParticleManager:
    """Manages particle effects"""
    def __init__(self):
        self.particles = []
        
    def add_particle(self, particle):
        if len(self.particles) < MAX_PARTICLES:
            self.particles.append(particle)
            
    def update(self):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()

# Menu setup
menu_buttons = [
    Button(WINDOW_WIDTH//2 - 100, 200, 200, 50, "Play"),
    Button(WINDOW_WIDTH//2 - 100, 270, 200, 50, "Settings"),
    Button(WINDOW_WIDTH//2 - 100, 340, 200, 50, "Quit")
]

def draw_menu(surface):
    """Draw main menu"""
    surface.fill(COLORS['HIGH_CONTRAST_BG'] if settings.high_contrast 
                else (50, 0, 100))
    for button in menu_buttons:
        button.draw(surface)
    return [surface.get_rect()]

def draw_settings(surface):
    """Draw settings menu"""
    surface.fill(COLORS['HIGH_CONTRAST_BG'] if settings.high_contrast 
                else (50, 0, 100))
    
    options = [
        ("Colorblind Mode", settings.colorblind_mode),
        ("High Contrast", settings.high_contrast),
        ("Show Particles", settings.show_particles),
        ("Difficulty: " + settings.difficulty.capitalize(), True),
        ("Back", True)
    ]
    
    buttons = []
    for i, (text, _) in enumerate(options):
        buttons.append(Button(WINDOW_WIDTH//2 - 100, 150 + i*60, 200, 40, text))
        
    for button in buttons:
        button.draw(surface)
        
    return buttons

def main():
    """Main game loop"""
    state = GameState.MENU
    game = None
    settings_menu_buttons = draw_settings(screen)
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state == GameState.MENU:
                    for button in menu_buttons:
                        if button.rect.collidepoint(event.pos):
                            if button.text == "Play":
                                game = Game(settings.difficulty)
                                state = GameState.PLAYING
                                sounds["click"].play()
                            elif button.text == "Settings":
                                state = GameState.SETTINGS
                                sounds["click"].play()
                            elif button.text == "Quit":
                                running = False
                                
                elif state == GameState.SETTINGS:
                    for i, button in enumerate(settings_menu_buttons):
                        if button.rect.collidepoint(event.pos):
                            sounds["click"].play()
                            if button.text.startswith("Colorblind"):
                                settings.colorblind_mode = not settings.colorblind_mode
                            elif button.text.startswith("High Contrast"):
                                settings.high_contrast = not settings.high_contrast
                            elif button.text.startswith("Show Particles"):
                                settings.show_particles = not settings.show_particles
                            elif button.text.startswith("Difficulty"):
                                difficulties = ["easy", "medium", "hard"]
                                current_idx = difficulties.index(settings.difficulty)
                                settings.difficulty = difficulties[(current_idx + 1) % 3]
                                button.text = f"Difficulty: {settings.difficulty.capitalize()}"
                            elif button.text == "Back":
                                state = GameState.MENU
                                settings.save()
                                
                elif state == GameState.PLAYING and game:
                    game.handle_click(*event.pos)
                    
                elif state == GameState.GAME_OVER:
                    buttons = game.show_game_over(screen)
                    for button in buttons:
                        if button.rect.collidepoint(event.pos):
                            sounds["click"].play()
                            if button.text == "Restart":
                                game = Game(game.difficulty)
                                state = GameState.PLAYING
                            elif button.text == "Main Menu":
                                state = GameState.MENU
                                
            elif event.type == pygame.KEYDOWN:
                if state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        game.paused = not game.paused
                    elif event.key == pygame.K_r:
                        game = Game(game.difficulty)
                    elif event.key == pygame.K_q:
                        state = GameState.MENU
                        
            elif event.type == pygame.USEREVENT + 1:
                if state == GameState.PLAYING and game and len(game.selected_cards) == 2:
                    if game.selected_cards[0].value == game.selected_cards[1].value:
                        game.matches += 1
                        game.selected_cards[0].matched = game.selected_cards[1].matched = True
                        if game.matches == len(game.cards) // 2:
                            game.game_over = True
                            state = GameState.GAME_OVER
                    else:
                        for card in game.selected_cards:
                            card.start_flip(False)
                    game.selected_cards = []
                    
            elif event.type == pygame.USEREVENT + 2:
                for card in game.cards:
                    card.glow = 0

        # Update display based on game state
        if state == GameState.MENU:
            for button in menu_buttons:
                button.update(mouse_pos)
            pygame.display.update(draw_menu(screen))
            
        elif state == GameState.SETTINGS:
            for button in settings_menu_buttons:
                button.update(mouse_pos)
            settings_menu_buttons = draw_settings(screen)
            
        elif state == GameState.PLAYING:
            if not game.tutorial_shown:
                game.draw_tutorial(screen)
            elif not game.paused:
                game.update()
                pygame.display.update(game.draw(screen))
            else:
                # Draw paused text
                font = pygame.font.Font(None, 48)
                pause_text = font.render("Paused", True, COLORS['WHITE'])
                screen.blit(pause_text, (WINDOW_WIDTH//2 - 50, WINDOW_HEIGHT//2))
                pygame.display.flip()
                
        elif state == GameState.GAME_OVER:
            buttons = game.show_game_over(screen)
            for button in buttons:
                button.update(mouse_pos)
                
        clock.tick(FPS)
        
    # Save settings on exit
    settings.save()
    pygame.quit()

if __name__ == "__main__":
    main()
