import pygame
import random
import sys
import time
import os
import json
import logging
from typing import List, Tuple

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

# Colors
WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (128, 128, 128)
BLUE, RED, GREEN = (0, 100, 255), (255, 50, 50), (50, 255, 50)
PURPLE, GOLD = (147, 0, 211), (255, 215, 0)
COLORBLIND_RED, COLORBLIND_GREEN = (200, 0, 0), (0, 150, 0)
HIGH_CONTRAST_BG, HIGH_CONTRAST_TEXT = (0, 0, 0), (255, 255, 255)

# Screen setup
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Memory Card Game")
clock = pygame.time.Clock()

# Load assets with error handling
def load_sound(file: str) -> pygame.mixer.Sound:
    try:
        return pygame.mixer.Sound(file)
    except pygame.error as e:
        logging.error(f"Failed to load sound {file}: {e}")
        return pygame.mixer.Sound(buffer=bytearray(100))

sounds = {
    "flip": load_sound("flip.wav"),
    "match": load_sound("match.wav"),
    "hint": load_sound("hint.wav"),
    "click": load_sound("click.wav")
}
music_files = ["background_music.mp3", "background_music2.mp3"]
current_music = 0
if music_files and os.path.exists(music_files[current_music]):
    try:
        pygame.mixer.music.load(music_files[current_music])
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        logging.error(f"Failed to load music {music_files[current_music]}: {e}")

# Settings
settings = {
    "sound_volume": 0.5,
    "music_volume": 0.3,
    "colorblind_mode": False,
    "show_particles": True,
    "high_contrast": False,
    "flip_speed": 8,
    "difficulty": "medium"
}

# Particle pool
particle_pool = []
active_particles = []

class Particle:
    def __init__(self, x: float, y: float):
        self.reset(x, y)
    
    def reset(self, x, y):
        self.x, self.y = x, y
        self.vx, self.vy = random.uniform(-1, 1), random.uniform(-2, -1)
        self.lifetime = random.randint(20, 60)
        self.color = random.choice([GOLD, WHITE, PURPLE])
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
    
    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 2)

class Button:
    def __init__(self, x, y, width, height, text, color=BLUE, hover_color=PURPLE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text, self.color, self.hover_color = text, color, hover_color
        self.hover, self.selected = False, False

    def draw(self, surface) -> pygame.Rect:
        color = self.hover_color if (self.hover or self.selected) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        font = pygame.font.Font(None, 30)
        text_surf = font.render(self.text, True, HIGH_CONTRAST_TEXT if settings["high_contrast"] else WHITE)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))
        return self.rect

    def update(self, mouse_pos: Tuple[int, int]):
        self.hover = self.rect.collidepoint(mouse_pos)

class Card:
    def __init__(self, x, y, value):
        self.x, self.y, self.value = x, y, value
        self.revealed, self.matched, self.hover = False, False, False
        self.flip_progress, self.flip_direction = 0, 0
        self.glow = 0

    def start_flip(self, to_front=True):
        self.flip_direction = 1 if to_front else -1
        if to_front:
            sounds["flip"].play()

    def update(self):
        if self.flip_direction:
            self.flip_progress += self.flip_direction * settings["flip_speed"]
            self.flip_progress = max(0, min(100, self.flip_progress))
            if self.flip_progress in [0, 100]:
                self.revealed = self.flip_progress == 100
                self.flip_direction = 0
        if self.glow > 0:
            self.glow -= 5

    def draw(self, surface) -> pygame.Rect:
        color = BLUE if not settings["colorblind_mode"] else COLORBLIND_RED
        if self.hover:
            color = PURPLE
        if self.matched:
            color = GREEN if not settings["colorblind_mode"] else COLORBLIND_GREEN
        pygame.draw.rect(surface, color, (self.x, self.y, CARD_WIDTH, CARD_HEIGHT), border_radius=5)
        if self.revealed or self.matched:
            font = pygame.font.Font(None, 48)
            text = font.render(str(self.value), True, WHITE)
            surface.blit(text, text.get_rect(center=(self.x + CARD_WIDTH // 2, self.y + CARD_HEIGHT // 2)))
        if self.glow > 0:
            glow_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (255, 255, 0, self.glow), (0, 0, CARD_WIDTH, CARD_HEIGHT))
            surface.blit(glow_surf, (self.x, self.y))
        return pygame.Rect(self.x, self.y, CARD_WIDTH, CARD_HEIGHT)

class Game:
    def __init__(self, difficulty="medium"):
        self.difficulty = difficulty
        self.cards = self.setup_cards()
        self.selected_cards = []
        self.moves, self.matches, self.score = 0, 0, 0
        self.game_over, self.paused = False, False
        self.start_time = time.time()
        self.hint_timer, self.hint_available = 0, True
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)).convert()
        self.background.fill((50, 0, 100) if not settings["high_contrast"] else HIGH_CONTRAST_BG)
        self.pause_button = Button(WINDOW_WIDTH - 120, 10, 100, 40, "Pause")
        self.hint_button = Button(WINDOW_WIDTH - 230, 10, 100, 40, "Hint")
        self.tutorial_shown = False

    def setup_cards(self) -> List[Card]:
        pairs = {"easy": 6, "medium": 8, "hard": 10}[self.difficulty]
        values = list(range(1, pairs + 1)) * 2
        random.shuffle(values)
        return [Card(100 + i % 4 * 150, 150 + i // 4 * 170, values[i]) for i in range(len(values))]

    def handle_click(self, x, y):
        if self.paused or self.game_over:
            return
        if self.pause_button.rect.collidepoint(x, y):
            self.paused = True
            sounds["click"].play()
        elif self.hint_button.rect.collidepoint(x, y) and self.hint_available:
            self.use_hint()
        elif len(self.selected_cards) < 2:
            for card in self.cards:
                if card.draw(screen).collidepoint(x, y) and not card.matched and not card.revealed:
                    card.start_flip()
                    self.selected_cards.append(card)
                    if len(self.selected_cards) == 2:
                        self.moves += 1
                        if self.selected_cards[0].value == self.selected_cards[1].value:
                            pygame.time.set_timer(pygame.USEREVENT + 1, 500)
                            self.selected_cards[0].glow = self.selected_cards[1].glow = 100
                            self.score += 100 - int(time.time() - self.start_time)
                            sounds["match"].play()
                            if settings["show_particles"]:
                                for _ in range(20):
                                    p = Particle(self.selected_cards[0].x + CARD_WIDTH // 2, self.selected_cards[0].y + CARD_HEIGHT // 2)
                                    active_particles.append(p)
                        else:
                            pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
                            self.score -= 10
                    break

    def use_hint(self):
        unmatched = [c for c in self.cards if not c.matched]
        if len(unmatched) >= 2:
            value = random.choice([c.value for c in unmatched])
            for card in unmatched:
                if card.value == value:
                    card.glow = 100
            self.hint_available = False
            self.hint_timer = time.time()
            sounds["hint"].play()
            pygame.time.set_timer(pygame.USEREVENT + 2, 2000)

    def update(self):
        for card in self.cards:
            card.update()
        if settings["show_particles"]:
            for p in active_particles[:]:
                p.update()
                if p.lifetime <= 0:
                    active_particles.remove(p)
        if not self.hint_available and time.time() - self.hint_timer > HINT_COOLDOWN:
            self.hint_available = True

    def draw(self, surface) -> List[pygame.Rect]:
        dirty_rects = [surface.blit(self.background, (0, 0))]
        for card in self.cards:
            dirty_rects.append(card.draw(surface))
        if settings["show_particles"]:
            for p in active_particles:
                p.draw(surface)
        dirty_rects.append(self.pause_button.draw(surface))
        dirty_rects.append(self.hint_button.draw(surface))
        if not self.hint_available:
            cooldown = int(HINT_COOLDOWN - (time.time() - self.hint_timer))
            font = pygame.font.Font(None, 24)
            text = font.render(f"{cooldown}s", True, WHITE)
            dirty_rects.append(surface.blit(text, (self.hint_button.rect.centerx - 10, self.hint_button.rect.bottom + 5)))
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        time_text = font.render(f"Time: {int(time.time() - self.start_time)}s", True, WHITE)
        dirty_rects.append(surface.blit(score_text, (10, 10)))
        dirty_rects.append(surface.blit(time_text, (10, 50)))
        return dirty_rects

    def draw_tutorial(self, surface):
        font = pygame.font.Font(None, 36)
        text = [
            "Welcome to Memory Card Game!",
            "Click two cards to flip them.",
            "Match pairs to score points.",
            "Use 'Hint' for help (cooldown applies).",
            "Press 'R' to restart, 'Q' to quit to menu."
        ]
        for i, line in enumerate(text):
            text_surf = font.render(line, True, WHITE)
            surface.blit(text_surf, (WINDOW_WIDTH // 4, WINDOW_HEIGHT // 4 + i * 40))
        pygame.display.flip()
        pygame.time.wait(3000)
        self.tutorial_shown = True

# Menu
menu_buttons = [
    Button(WINDOW_WIDTH // 2 - 100, 200, 200, 50, "Play"),
    Button(WINDOW_WIDTH // 2 - 100, 270, 200, 50, "Settings"),
    Button(WINDOW_WIDTH // 2 - 100, 340, 200, 50, "Quit")
]

def draw_menu(surface):
    surface.fill((50, 0, 100))
    dirty_rects = []
    for button in menu_buttons:
        dirty_rects.append(button.draw(surface))
    return dirty_rects

# Main loop
def main():
    global particle_pool
    particle_pool = [Particle(0, 0) for _ in range(MAX_PARTICLES)]
    state = "menu"
    game = None
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state == "menu":
                    if menu_buttons[0].rect.collidepoint(event.pos):
                        game = Game(settings["difficulty"])
                        state = "playing"
                        sounds["click"].play()
                    elif menu_buttons[1].rect.collidepoint(event.pos):
                        state = "settings"  # Placeholder for settings menu
                        sounds["click"].play()
                    elif menu_buttons[2].rect.collidepoint(event.pos):
                        running = False
                elif state == "playing" and game:
                    game.handle_click(*event.pos)
            elif event.type == pygame.USEREVENT + 1:
                if state == "playing" and game and len(game.selected_cards) == 2:
                    if game.selected_cards[0].value == game.selected_cards[1].value:
                        game.matches += 1
                        game.selected_cards[0].matched = game.selected_cards[1].matched = True
                        if game.matches == len(game.cards) // 2:
                            game.game_over = True
                    else:
                        for card in game.selected_cards:
                            card.start_flip(False)
                    game.selected_cards = []
            elif event.type == pygame.USEREVENT + 2:
                for card in game.cards:
                    card.glow = 0
            elif event.type == pygame.KEYDOWN:
                if state == "playing" and event.key == pygame.K_r:
                    game = Game(game.difficulty)
                elif event.key == pygame.K_q:
                    state = "menu"

        if state == "menu":
            for button in menu_buttons:
                button.update(mouse_pos)
            pygame.display.update(draw_menu(screen))
        elif state == "playing" and game:
            if not game.tutorial_shown:
                game.draw_tutorial(screen)
            elif not game.paused:
                game.update()
                pygame.display.update(game.draw(screen))
            if game.paused:
                font = pygame.font.Font(None, 48)
                pause_text = font.render("Paused", True, WHITE)
                screen.blit(pause_text, (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2))
                pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()
