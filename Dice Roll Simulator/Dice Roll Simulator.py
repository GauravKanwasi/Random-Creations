import pygame
import random
import sys
import math
import time
import json
import os
from pygame import mixer
from collections import Counter

# Initialize Pygame and Mixer
pygame.init()
mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GRAY = (220, 220, 220)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (70, 130, 180)
GOLD = (255, 215, 0)
GREEN = (50, 205, 50)
PURPLE = (138, 43, 226)

# Load sounds
try:
    ROLL_SOUNDS = [
        mixer.Sound('dice_roll1.wav'),
        mixer.Sound('dice_roll2.wav'),
        mixer.Sound('dice_roll3.wav')
    ]
    IMPACT_SOUND = mixer.Sound('impact.wav')
    SUCCESS_SOUND = mixer.Sound('success.wav')
    CLICK_SOUND = mixer.Sound('click.wav')
except:
    ROLL_SOUNDS = [None] * 3
    IMPACT_SOUND = None
    SUCCESS_SOUND = None
    CLICK_SOUND = None

# Die face configurations
DIE_FACES = {
    1: [(0.5, 0.5)],
    2: [(0.25, 0.25), (0.75, 0.75)],
    3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
    4: [(0.25, 0.25), (0.25, 0.75), (0.75, 0.25), (0.75, 0.75)],
    5: [(0.25, 0.25), (0.25, 0.75), (0.5, 0.5), (0.75, 0.25), (0.75, 0.75)],
    6: [(0.25, 0.25), (0.25, 0.5), (0.25, 0.75), (0.75, 0.25), (0.75, 0.5), (0.75, 0.75)]
}

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.lifetime = random.randint(20, 50)
        self.age = 0
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.age += 1
        self.size = max(1, self.size - 0.15)

    def draw(self, screen):
        if self.age < self.lifetime:
            alpha = int(255 * (1 - self.age / self.lifetime))
            surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color[:3], alpha), (self.size, self.size), self.size)
            screen.blit(surface, (int(self.x - self.size), int(self.y - self.size)))

class Die:
    def __init__(self, x, y, size, sides=6, color=WHITE):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.size = size
        self.sides = sides
        self.color = color
        self.value = random.randint(1, sides)
        self.rolling = False
        self.roll_frames = 0
        self.total_roll_frames = 30
        self.angle = 0
        self.scale = 1.0
        self.vy = -12
        self.bounce_count = 0
        self.max_bounces = 3
        self.particles = []
        self.glow = 0

    def roll(self):
        self.rolling = True
        self.roll_frames = 0
        self.vy = -12
        self.bounce_count = 0
        if ROLL_SOUNDS[0]:
            random.choice(ROLL_SOUNDS).play()

    def update(self):
        if self.rolling:
            self.roll_frames += 1
            
            # Physics-based bounce animation
            self.y += self.vy
            self.vy += 0.6
            if self.y > self.target_y and self.bounce_count < self.max_bounces:
                self.y = self.target_y
                self.vy = -self.vy * 0.7
                self.bounce_count += 1
                if IMPACT_SOUND:
                    IMPACT_SOUND.play()
                for _ in range(8):
                    self.particles.append(Particle(self.x + self.size/2, self.y + self.size, GOLD))

            # Rolling animation
            if self.roll_frames < self.total_roll_frames:
                self.value = random.randint(1, self.sides)
                self.angle = math.sin(self.roll_frames * 0.6) * 45
                self.scale = 0.85 + 0.25 * math.sin(self.roll_frames * 0.6)
            else:
                self.rolling = False
                self.angle = 0
                self.scale = 1.0
                self.y = self.target_y
                self.vy = 0
                if self.value == self.sides and SUCCESS_SOUND:
                    SUCCESS_SOUND.play()
                    self.glow = 60

            self.particles = [p for p in self.particles if p.age < p.lifetime]
            for particle in self.particles:
                particle.update()
            if self.glow > 0:
                self.glow -= 1

    def draw(self, screen):
        current_size = int(self.size * self.scale)
        die_surface = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
        
        if self.glow > 0:
            glow_surface = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
            glow_alpha = int(128 * (self.glow / 60))
            pygame.draw.rect(glow_surface, (*GREEN[:3], glow_alpha), (0, 0, current_size, current_size), 0, 10)
            die_surface.blit(glow_surface, (current_size // 4, current_size // 4))

        pygame.draw.rect(die_surface, (50, 50, 50, 50), (current_size // 4 + 2, current_size // 4 + 2, current_size, current_size), 0, 10)
        pygame.draw.rect(die_surface, self.color, (current_size // 4, current_size // 4, current_size, current_size), 0, 10)
        pygame.draw.rect(die_surface, BLACK, (current_size // 4, current_size // 4, current_size, current_size), 2, 10)
        
        if 1 <= self.value <= 6:
            dot_radius = max(4, current_size // 10)
            for px, py in DIE_FACES.get(self.value, []):
                dot_x = current_size // 4 + int(px * current_size)
                dot_y = current_size // 4 + int(py * current_size)
                pygame.draw.circle(die_surface, BLACK, (dot_x, dot_y), dot_radius)
        else:
            font = pygame.font.SysFont('Arial', current_size // 2)
            text = font.render(str(self.value), True, BLACK)
            text_rect = text.get_rect(center=(current_size // 2 + current_size // 4, current_size // 2 + current_size // 4))
            die_surface.blit(text, text_rect)
            
        rotated_surface = pygame.transform.rotate(die_surface, self.angle)
        rotated_rect = rotated_surface.get_rect(center=(self.x + self.size // 2, self.y + self.size // 2))
        screen.blit(rotated_surface, rotated_rect)

        for particle in self.particles:
            particle.draw(screen)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.scale = 1.0
        self.target_scale = 1.0

    def draw(self, screen):
        scaled_rect = pygame.Rect(
            self.rect.x - (self.rect.width * (self.scale - 1)) / 2,
            self.rect.y - (self.rect.height * (self.scale - 1)) / 2,
            self.rect.width * self.scale,
            self.rect.height * self.scale
        )
        
        pygame.draw.rect(screen, self.current_color, scaled_rect, 0, 10)
        pygame.draw.rect(screen, BLACK, scaled_rect, 2, 10)
        
        font = pygame.font.SysFont('Arial', int(20 * self.scale))
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        screen.blit(text_surface, text_rect)
        
    def update(self, mouse_pos):
        self.scale += (self.target_scale - self.scale) * 0.1
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            self.target_scale = 1.1
            return True
        else:
            self.current_color = self.color
            self.target_scale = 1.0
            return False

class InputBox:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = BLACK
        self.text = text
        self.font = pygame.font.SysFont('Arial', 20)
        self.txt_surface = self.font.render(text, True, BLACK)
        self.active = False
        self.error = False
        self.error_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
            if self.rect.collidepoint(event.pos if hasattr(event, 'pos') else (event.x * WIDTH, event.y * HEIGHT)):
                self.active = not self.active
                if CLICK_SOUND:
                    CLICK_SOUND.play()
            else:
                self.active = False
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if event.unicode.isdigit():
                        self.text = self.text[:10] + event.unicode if len(self.text) < 10 else self.text
                self.txt_surface = self.font.render(self.text, True, BLACK)
        return False
                
    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width
        if self.error:
            self.error_timer -= 1
            if self.error_timer <= 0:
                self.error = False

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect, 0, 5)
        outline_color = RED if self.active or self.error else BLACK
        pygame.draw.rect(screen, outline_color, self.rect, 2, 5)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

class Statistics:
    def __init__(self):
        self.rolls = []
        self.total_rolls = 0

    def add_roll(self, results):
        self.rolls.append(results)
        self.total_rolls += len(results)
        if len(self.rolls) > 100:
            self.rolls.pop(0)

    def get_stats(self):
        if not self.rolls:
            return {"average": 0, "min": 0, "max": 0, "frequency": {}}
        all_values = [val for roll in self.rolls for val in roll]
        frequency = Counter(all_values)
        return {
            "average": sum(all_values) / len(all_values) if all_values else 0,
            "min": min(all_values) if all_values else 0,
            "max": max(all_values) if all_values else 0,
            "frequency": frequency
        }

def load_settings():
    try:
        with open('dice_settings.json', 'r') as f:
            return json.load(f)
    except:
        return {'dice_count': '2', 'sides': '6', 'color': 'white', 'roll_speed': 'normal', 'mode': 'standard'}

def save_settings(dice_count, sides, color, roll_speed, mode):
    settings = {
        'dice_count': str(dice_count),
        'sides': str(sides),
        'color': color,
        'roll_speed': roll_speed,
        'mode': mode
    }
    with open('dice_settings.json', 'w') as f:
        json.dump(settings, f)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Super Dice Rolling Simulator")
    clock = pygame.time.Clock()
    
    settings = load_settings()
    
    COLOR_OPTIONS = {
        'white': WHITE,
        'red': RED,
        'green': GREEN,
        'purple': PURPLE
    }
    
    dice_count_input = InputBox(300, 120, 200, 30, settings['dice_count'])
    sides_input = InputBox(300, 170, 200, 30, settings['sides'])
    roll_button = Button(300, 220, 200, 50, "Roll Dice", LIGHT_BLUE, DARK_BLUE)
    quick_roll_button = Button(300, 280, 200, 50, "Quick Roll", GREEN, DARK_BLUE)
    reset_button = Button(300, 340, 200, 50, "Reset", GRAY, LIGHT_BLUE)
    color_button = Button(300, 400, 200, 50, f"Color: {settings['color'].capitalize()}", PURPLE, DARK_BLUE)
    mode_button = Button(300, 460, 200, 50, f"Mode: {settings['mode'].capitalize()}", GOLD, DARK_BLUE)
    
    dice = []
    rolling = False
    results = []
    total = 0
    roll_history = []
    stats = Statistics()
    error_message = ""
    error_timer = 0
    current_color = settings['color']
    current_mode = settings['mode']
    
    font = pygame.font.SysFont('Arial', 24)
    title_font = pygame.font.SysFont('Arial', 36)
    small_font = pygame.font.SysFont('Arial', 16)
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            dice_count_input.handle_event(event)
            sides_input.handle_event(event)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        num_dice = max(1, min(10, int(dice_count_input.text)))
                        sides = max(2, min(100, int(sides_input.text)))
                        
                        dice = []
                        results = []
                        
                        dice_size = min(100, 600 // num_dice)
                        spacing = min(20, 100 // num_dice)
                        total_width = num_dice * (dice_size + spacing) - spacing
                        start_x = (WIDTH - total_width) // 2
                        
                        for i in range(num_dice):
                            x = start_x + i * (dice_size + spacing)
                            y = 400
                            die = Die(x, y, dice_size, sides, COLOR_OPTIONS[current_color])
                            die.roll()
                            if current_mode == 'quick':
                                die.roll_frames = die.total_roll_frames - 1
                            dice.append(die)
                            
                        rolling = True
                        save_settings(num_dice, sides, current_color, 'normal', current_mode)
                        error_message = ""
                        
                    except ValueError:
                        error_message = "Enter numbers (1-10 dice, 2-100 sides)!"
                        error_timer = 120
                        dice_count_input.error = True
                        sides_input.error = True
                        dice_count_input.error_timer = 120
                        sides_input.error_timer = 120
            
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                pos = event.pos if hasattr(event, 'pos') else (event.x * WIDTH, event.y * HEIGHT)
                
                if roll_button.update(pos) and (event.button == 1 or event.type == pygame.FINGERDOWN):
                    try:
                        num_dice = max(1, min(10, int(dice_count_input.text)))
                        sides = max(2, min(100, int(sides_input.text)))
                        
                        dice = []
                        results = []
                        
                        dice_size = min(100, 600 // num_dice)
                        spacing = min(20, 100 // num_dice)
                        total_width = num_dice * (dice_size + spacing) - spacing
                        start_x = (WIDTH - total_width) // 2
                        
                        for i in range(num_dice):
                            x = start_x + i * (dice_size + spacing)
                            y = 400
                            die = Die(x, y, dice_size, sides, COLOR_OPTIONS[current_color])
                            die.roll()
                            if current_mode == 'quick':
                                die.roll_frames = die.total_roll_frames - 1
                            dice.append(die)
                            
                        rolling = True
                        save_settings(num_dice, sides, current_color, 'normal', current_mode)
                        error_message = ""
                        
                    except ValueError:
                        error_message = "Enter numbers (1-10 dice, 2-100 sides)!"
                        error_timer = 120
                        dice_count_input.error = True
                        sides_input.error = True
                        dice_count_input.error_timer = 120
                        sides_input.error_timer = 120
                
                if quick_roll_button.update(pos) and (event.button == 1 or event.type == pygame.FINGERDOWN):
                    try:
                        num_dice = max(1, min(10, int(dice_count_input.text)))
                        sides = max(2, min(100, int(sides_input.text)))
                        
                        dice = []
                        results = [random.randint(1, sides) for _ in range(num_dice)]
                        total = sum(results)
                        stats.add_roll(results)
                        roll_history.append((results, total))
                        if len(roll_history) > 5:
                            roll_history.pop(0)
                        error_message = ""
                        save_settings(num_dice, sides, current_color, 'normal', current_mode)
                        
                    except ValueError:
                        error_message = "Enter valid numbers!"
                        error_timer = 120
                
                if reset_button.update(pos) and (event.button == 1 or event.type == pygame.FINGERDOWN):
                    dice_count_input.text = '2'
                    dice_count_input.txt_surface = dice_count_input.font.render('2', True, BLACK)
                    sides_input.text = '6'
                    sides_input.txt_surface = sides_input.font.render('6', True, BLACK)
                    dice = []
                    results = []
                    total = 0
                    roll_history = []
                    stats = Statistics()
                    current_color = 'white'
                    current_mode = 'standard'
                    color_button.text = "Color: White"
                    mode_button.text = "Mode: Standard"
                    save_settings(2, 6, current_color, 'normal', current_mode)
                    if CLICK_SOUND:
                        CLICK_SOUND.play()
                
                if color_button.update(pos) and (event.button == 1 or event.type == pygame.FINGERDOWN):
                    colors = list(COLOR_OPTIONS.keys())
                    current_color = colors[(colors.index(current_color) + 1) % len(colors)]
                    color_button.text = f"Color: {current_color.capitalize()}"
                    save_settings(int(dice_count_input.text or 2), int(sides_input.text or 6), current_color, 'normal', current_mode)
                    if CLICK_SOUND:
                        CLICK_SOUND.play()
                
                if mode_button.update(pos) and (event.button == 1 or event.type == pygame.FINGERDOWN):
                    modes = ['standard', 'quick', 'casino']
                    current_mode = modes[(modes.index(current_mode) + 1) % len(modes)]
                    mode_button.text = f"Mode: {current_mode.capitalize()}"
                    save_settings(int(dice_count_input.text or 2), int(sides_input.text or 6), current_color, 'normal', current_mode)
                    if CLICK_SOUND:
                        CLICK_SOUND.play()
        
        dice_count_input.update()
        sides_input.update()
        roll_button.update(mouse_pos)
        quick_roll_button.update(mouse_pos)
        reset_button.update(mouse_pos)
        color_button.update(mouse_pos)
        mode_button.update(mouse_pos)
        
        if rolling:
            all_finished = True
            for die in dice:
                die.update()
                if die.rolling:
                    all_finished = False
            
            if all_finished:
                rolling = False
                results = [die.value for die in dice]
                total = sum(results)
                stats.add_roll(results)
                roll_history.append((results, total))
                if len(roll_history) > 5:
                    roll_history.pop(0)
        
        if error_timer > 0:
            error_timer -= 1
        
        screen.fill((240, 240, 240) if current_mode != 'casino' else (0, 100, 0))
        
        title_scale = 1.0 + 0.03 * math.sin(time.time() * 2)
        title_text = title_font.render("Super Dice Rolling Simulator", True, BLACK)
        title_surface = pygame.transform.scale(title_text, 
            (int(title_text.get_width() * title_scale), int(title_text.get_height() * title_scale)))
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 20))
        
        label_font = pygame.font.SysFont('Arial', 20)
        screen.blit(label_font.render("Number of Dice:", True, BLACK), (150, 125))
        screen.blit(label_font.render("Number of Sides:", True, BLACK), (150, 175))
        
        dice_count_input.draw(screen)
        sides_input.draw(screen)
        roll_button.draw(screen)
        quick_roll_button.draw(screen)
        reset_button.draw(screen)
        color_button.draw(screen)
        mode_button.draw(screen)
        
        for die in dice:
            die.draw(screen)
        
        if results:
            results_text = font.render(f"Results: {results}", True, BLACK)
            total_text = font.render(f"Total: {total}", True, BLACK)
            screen.blit(results_text, (WIDTH // // 2 - results_text.get_width() // 2, 520))
            screen.blit(total_text, (WIDTH // 2 - total_text.get_width() // 2, 550))
        
        for i, (hist_results, hist_total) in enumerate(roll_history[:-1]):
            history_text = small_font.render(f"Roll {len(roll_history)-i-1}: {hist_results} = {hist_total}", True, (100, 100, 100))
            screen.blit(history_text, (20, 80 + i * 20))
        
        stats_data = stats.get_stats()
        stats_text = [
            f"Rolls: {stats.total_rolls}",
            f"Avg: {stats_data['average']:.1f}",
            f"Min: {stats_data['min']}",
            f"Max: {stats_data['max']}"
        ]
        for i, text in enumerate(stats_text):
            stats_surface = small_font.render(text, True, BLACK)
            screen.blit(stats_surface, (WIDTH - 100, 80 + i * 20))
        
        # Draw top five frequencies
        frequency = stats_data['frequency']
        if frequency:
            top_five = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:5]
            top_five_text = "Top 5: " + ", ".join([f"{num}: {count}" for num, count in top_five])
            top_five_surface = small_font.render(top_five_text, True, BLACK)
            screen.blit(top_five_surface, (WIDTH - 100, 80 + 4 * 20))
        
        if error_timer > 0:
            error_text = font.render(error_message, True, RED)
            screen.blit(error_text, (WIDTH // 2 - error_text.get_width() // 2, 350))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
