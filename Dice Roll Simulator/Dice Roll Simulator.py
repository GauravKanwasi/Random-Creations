import pygame
import random
import sys
import math
import time
import json
import os
from pygame import mixer

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

# Load sounds
try:
    ROLL_SOUND = mixer.Sound('dice_roll.wav')  # You'll need a dice roll sound file
    CLICK_SOUND = mixer.Sound('click.wav')     # You'll need a click sound file
except:
    ROLL_SOUND = None
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
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.lifetime = random.randint(20, 40)
        self.age = 0
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.age += 1
        self.size = max(1, self.size - 0.1)

    def draw(self, screen):
        if self.age < self.lifetime:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class Die:
    def __init__(self, x, y, size, sides=6):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.size = size
        self.sides = sides
        self.value = random.randint(1, sides)
        self.rolling = False
        self.roll_frames = 0
        self.total_roll_frames = 30
        self.angle = 0
        self.scale = 1.0
        self.vy = -10
        self.bounce_count = 0
        self.max_bounces = 2
        self.particles = []

    def roll(self):
        self.rolling = True
        self.roll_frames = 0
        self.vy = -10
        self.bounce_count = 0
        if ROLL_SOUND:
            ROLL_SOUND.play()

    def update(self):
        if self.rolling:
            self.roll_frames += 1
            
            # Physics-based bounce animation
            self.y += self.vy
            self.vy += 0.5  # Gravity
            if self.y > self.target_y and self.bounce_count < self.max_bounces:
                self.y = self.target_y
                self.vy = -self.vy * 0.6
                self.bounce_count += 1
                # Create particles on bounce
                for _ in range(5):
                    self.particles.append(Particle(self.x + self.size/2, self.y + self.size, GOLD))

            # Rolling animation
            if self.roll_frames < self.total_roll_frames:
                self.value = random.randint(1, self.sides)
                self.angle = math.sin(self.roll_frames * 0.5) * 30
                self.scale = 0.9 + 0.2 * math.sin(self.roll_frames * 0.5)
            else:
                self.rolling = False
                self.angle = 0
                self.scale = 1.0
                self.y = self.target_y
                self.vy = 0

            # Update particles
            self.particles = [p for p in self.particles if p.age < p.lifetime]
            for particle in self.particles:
                particle.update()

    def draw(self, screen):
        current_size = int(self.size * self.scale)
        die_surface = pygame.Surface((current_size, current_size), pygame.SRCALPHA)
        
        # Draw die with slight shadow
        pygame.draw.rect(die_surface, (50, 50, 50, 50), (2, 2, current_size, current_size), 0, 10)
        pygame.draw.rect(die_surface, WHITE, (0, 0, current_size, current_size), 0, 10)
        pygame.draw.rect(die_surface, BLACK, (0, 0, current_size, current_size), 2, 10)
        
        # Draw dots or number
        if 1 <= self.value <= 6:
            dot_radius = max(4, current_size // 10)
            for px, py in DIE_FACES[self.value]:
                dot_x = int(px * current_size)
                dot_y = int(py * current_size)
                pygame.draw.circle(die_surface, BLACK, (dot_x, dot_y), dot_radius)
        else:
            font = pygame.font.SysFont('Arial', current_size // 2)
            text = font.render(str(self.value), True, BLACK)
            text_rect = text.get_rect(center=(current_size // 2, current_size // 2))
            die_surface.blit(text, text_rect)
            
        rotated_surface = pygame.transform.rotate(die_surface, self.angle)
        rotated_rect = rotated_surface.get_rect(center=(self.x + self.size // 2, self.y + self.size // 2))
        screen.blit(rotated_surface, rotated_rect)

        # Draw particles
        for particle in self.particles:
            particle.draw(screen)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.clicked = False
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
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
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
                        self.text += event.unicode
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

def load_settings():
    try:
        with open('dice_settings.json', 'r') as f:
            return json.load(f)
    except:
        return {'dice_count': '2', 'sides': '6'}

def save_settings(dice_count, sides):
    settings = {'dice_count': str(dice_count), 'sides': str(sides)}
    with open('dice_settings.json', 'w') as f:
        json.dump(settings, f)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Enhanced Dice Rolling Simulator")
    clock = pygame.time.Clock()
    
    # Load saved settings
    settings = load_settings()
    
    # Create UI elements
    dice_count_input = InputBox(300, 150, 200, 30, settings['dice_count'])
    sides_input = InputBox(300, 200, 200, 30, settings['sides'])
    roll_button = Button(300, 250, 200, 50, "Roll Dice", LIGHT_BLUE, DARK_BLUE)
    reset_button = Button(300, 320, 200, 50, "Reset", GRAY, LIGHT_BLUE)
    
    dice = []
    rolling = False
    results = []
    total = 0
    roll_history = []
    error_message = ""
    error_timer = 0
    
    font = pygame.font.SysFont('Arial', 24)
    title_font = pygame.font.SysFont('Arial', 36)
    small_font = pygame.font.SysFont('Arial', 18)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            dice_count_input.handle_event(event)
            sides_input.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if roll_button.update(mouse_pos) and event.button == 1:
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
                            die = Die(x, y, dice_size, sides)
                            die.roll()
                            dice.append(die)
                            
                        rolling = True
                        save_settings(num_dice, sides)
                        error_message = ""
                        
                    except ValueError:
                        error_message = "Please enter valid numbers!"
                        error_timer = 120
                        dice_count_input.error = True
                        sides_input.error = True
                        dice_count_input.error_timer = 120
                        sides_input.error_timer = 120
                
                if reset_button.update(mouse_pos) and event.button == 1:
                    dice_count_input.text = '2'
                    dice_count_input.txt_surface = dice_count_input.font.render('2', True, BLACK)
                    sides_input.text = '6'
                    sides_input.txt_surface = sides_input.font.render('6', True, BLACK)
                    dice = []
                    results = []
                    total = 0
                    roll_history = []
                    save_settings(2, 6)
                    if CLICK_SOUND:
                        CLICK_SOUND.play()
        
        # Update
        dice_count_input.update()
        sides_input.update()
        roll_button.update(pygame.mouse.get_pos())
        reset_button.update(pygame.mouse.get_pos())
        
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
                roll_history.append((results, total))
                if len(roll_history) > 5:
                    roll_history.pop(0)
        
        if error_timer > 0:
            error_timer -= 1
        
        # Draw
        screen.fill((240, 240, 240))
        
        # Draw title with subtle animation
        title_scale = 1.0 + 0.02 * math.sin(time.time() * 2)
        title_text = title_font.render("Dice Rolling Simulator", True, BLACK)
        title_surface = pygame.transform.scale(title_text, 
            (int(title_text.get_width() * title_scale), int(title_text.get_height() * title_scale)))
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 30))
        
        # Draw input labels
        label_font = pygame.font.SysFont('Arial', 20)
        screen.blit(label_font.render("Number of Dice:", True, BLACK), (150, 155))
        screen.blit(label_font.render("Number of Sides:", True, BLACK), (150, 205))
        
        # Draw UI elements
        dice_count_input.draw(screen)
        sides_input.draw(screen)
        roll_button.draw(screen)
        reset_button.draw(screen)
        
        # Draw dice
        for die in dice:
            die.draw(screen)
        
        # Draw results and history
        if results:
            results_text = font.render(f"Results: {results}", True, BLACK)
            total_text = font.render(f"Total: {total}", True, BLACK)
            screen.blit(results_text, (WIDTH // 2 - results_text.get_width() // 2, 520))
            screen.blit(total_text, (WIDTH // 2 - total_text.get_width() // 2, 550))
        
        # Draw roll history
        for i, (hist_results, hist_total) in enumerate(roll_history[:-1]):
            history_text = small_font.render(f"Roll {len(roll_history)-i-1}: {hist_results} = {hist_total}", True, (100, 100, 100))
            screen.blit(history_text, (20, 100 + i * 20))
        
        # Draw error message
        if error_timer > 0:
            error_text = font.render(error_message, True, RED)
            screen.blit(error_text, (WIDTH // 2 - error_text.get_width() // 2, 350))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()