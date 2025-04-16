import pygame
import random
import sys
import math
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GRAY = (220, 220, 220)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (70, 130, 180)

# Die face configurations (dots positions)
DIE_FACES = {
    1: [(0.5, 0.5)],
    2: [(0.25, 0.25), (0.75, 0.75)],
    3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
    4: [(0.25, 0.25), (0.25, 0.75), (0.75, 0.25), (0.75, 0.75)],
    5: [(0.25, 0.25), (0.25, 0.75), (0.5, 0.5), (0.75, 0.25), (0.75, 0.75)],
    6: [(0.25, 0.25), (0.25, 0.5), (0.25, 0.75), (0.75, 0.25), (0.75, 0.5), (0.75, 0.75)]
}

class Die:
    def __init__(self, x, y, size, sides=6):
        self.x = x
        self.y = y
        self.size = size
        self.sides = sides
        self.value = random.randint(1, sides)
        self.rolling = False
        self.roll_frames = 0
        self.total_roll_frames = 20
        self.angle = 0
        self.scale = 1.0
        
    def roll(self):
        self.rolling = True
        self.roll_frames = 0
        
    def update(self):
        if self.rolling:
            self.roll_frames += 1
            # During rolling animation, change value randomly
            if self.roll_frames < self.total_roll_frames:
                self.value = random.randint(1, self.sides)
                self.angle = math.sin(self.roll_frames * 0.5) * 15
                self.scale = 0.9 + 0.2 * math.sin(self.roll_frames * 0.5)
            else:
                self.rolling = False
                self.angle = 0
                self.scale = 1.0
                
    def draw(self, screen):
        # Calculate size with scale factor
        current_size = int(self.size * self.scale)
        
        # Create a surface for the die
        die_surface = pygame.Surface((current_size, current_size), pygame.SRCALPHA)
        
        # Draw the die body
        pygame.draw.rect(die_surface, WHITE, (0, 0, current_size, current_size), 0, 10)
        pygame.draw.rect(die_surface, BLACK, (0, 0, current_size, current_size), 2, 10)
        
        # Draw the dots based on current value
        if 1 <= self.value <= 6:
            dot_radius = max(4, current_size // 10)
            for px, py in DIE_FACES[self.value]:
                dot_x = int(px * current_size)
                dot_y = int(py * current_size)
                pygame.draw.circle(die_surface, BLACK, (dot_x, dot_y), dot_radius)
        else:
            # Draw the number for dice with more than 6 sides
            font = pygame.font.SysFont('Arial', current_size // 2)
            text = font.render(str(self.value), True, BLACK)
            text_rect = text.get_rect(center=(current_size // 2, current_size // 2))
            die_surface.blit(text, text_rect)
            
        # Rotate the die surface
        rotated_surface = pygame.transform.rotate(die_surface, self.angle)
        
        # Get the rect of the rotated surface and position it correctly
        rotated_rect = rotated_surface.get_rect(center=(self.x + self.size // 2, self.y + self.size // 2))
        
        # Draw the die on the screen
        screen.blit(rotated_surface, rotated_rect)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.clicked = False
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect, 0, 10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, 10)
        
        font = pygame.font.SysFont('Arial', 20)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.color
            return False

class InputBox:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = BLACK
        self.text = text
        self.font = pygame.font.SysFont('Arial', 20)
        self.txt_surface = self.font.render(text, True, BLACK)
        self.active = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable
                self.active = not self.active
            else:
                self.active = False
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    # Only allow numeric input
                    if event.unicode.isdigit():
                        self.text += event.unicode
                # Re-render the text
                self.txt_surface = self.font.render(self.text, True, BLACK)
        return False
                
    def update(self):
        # Keep the rect width dynamic based on input text
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width
        
    def draw(self, screen):
        # Draw the input box background
        pygame.draw.rect(screen, WHITE, self.rect, 0, 5)
        # Draw the outline - thicker if active
        pygame.draw.rect(screen, RED if self.active else BLACK, self.rect, 2, 5)
        # Draw the input text
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dice Rolling Simulator")
    clock = pygame.time.Clock()
    
    # Create UI elements
    dice_count_input = InputBox(300, 150, 200, 30, '2')
    sides_input = InputBox(300, 200, 200, 30, '6')
    roll_button = Button(300, 250, 200, 50, "Roll Dice", LIGHT_BLUE, DARK_BLUE)
    reset_button = Button(300, 320, 200, 50, "Reset", GRAY, LIGHT_BLUE)
    
    dice = []
    rolling = False
    results = []
    total = 0
    
    # Font for displaying results
    font = pygame.font.SysFont('Arial', 24)
    title_font = pygame.font.SysFont('Arial', 36)
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Handle input box events
            if dice_count_input.handle_event(event) or sides_input.handle_event(event):
                pass
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Roll button clicked
                if roll_button.update(mouse_pos) and event.button == 1:
                    try:
                        num_dice = max(1, min(10, int(dice_count_input.text)))
                        sides = max(2, int(sides_input.text))
                        
                        # Create dice
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
                        
                    except ValueError:
                        pass
                
                # Reset button clicked
                if reset_button.update(mouse_pos) and event.button == 1:
                    dice_count_input.text = '2'
                    dice_count_input.txt_surface = dice_count_input.font.render(dice_count_input.text, True, BLACK)
                    sides_input.text = '6'
                    sides_input.txt_surface = sides_input.font.render(sides_input.text, True, BLACK)
                    dice = []
                    results = []
                    total = 0
        
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
        
        # Draw
        screen.fill((240, 240, 240))
        
        # Draw title
        title_text = title_font.render("Dice Rolling Simulator", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
        
        # Draw input labels
        label_font = pygame.font.SysFont('Arial', 20)
        dice_label = label_font.render("Number of Dice:", True, BLACK)
        screen.blit(dice_label, (150, 155))
        
        sides_label = label_font.render("Number of Sides:", True, BLACK)
        screen.blit(sides_label, (150, 205))
        
        # Draw UI elements
        dice_count_input.draw(screen)
        sides_input.draw(screen)
        roll_button.draw(screen)
        reset_button.draw(screen)
        
        # Draw dice
        for die in dice:
            die.draw(screen)
        
        # Draw results
        if results:
            results_text = font.render(f"Results: {results}", True, BLACK)
            total_text = font.render(f"Total: {total}", True, BLACK)
            
            screen.blit(results_text, (WIDTH // 2 - results_text.get_width() // 2, 520))
            screen.blit(total_text, (WIDTH // 2 - total_text.get_width() // 2, 550))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()