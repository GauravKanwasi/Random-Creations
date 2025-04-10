import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Initialize screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pygame Adventure")
clock = pygame.time.Clock()

# Load fonts
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.inventory = []
        self.gold = 0
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.speed = 5
        self.size = 40
        self.color = GREEN

    def draw(self, screen):
        # Draw player
        pygame.draw.rect(screen, self.color, (self.x - self.size//2, self.y - self.size//2, self.size, self.size))
        
        # Draw health bar
        health_width = 100
        health_height = 10
        health_x = self.x - health_width//2
        health_y = self.y - self.size//2 - 20
        
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
        pygame.draw.rect(screen, GREEN, (health_x, health_y, health_width * (self.health/self.max_health), health_height))

    def move(self, dx, dy):
        self.x = max(self.size//2, min(WINDOW_WIDTH - self.size//2, self.x + dx * self.speed))
        self.y = max(self.size//2, min(WINDOW_HEIGHT - self.size//2, self.y + dy * self.speed))

class Game:
    def __init__(self):
        self.player = None
        self.current_location = 'village'
        self.message = ""
        self.message_timer = 0
        self.locations = {
            'village': {
                'description': 'A peaceful village with a marketplace and an old well.',
                'color': (100, 200, 100),
                'options': ['marketplace', 'forest', 'cave'],
            },
            'marketplace': {
                'description': 'A bustling marketplace with various merchants.',
                'color': (200, 200, 100),
                'options': ['village', 'shop'],
            },
            'forest': {
                'description': 'A dark forest with mysterious sounds.',
                'color': (0, 100, 0),
                'options': ['village', 'deep_forest'],
            },
            'cave': {
                'description': 'A dark cave entrance looms before you.',
                'color': (50, 50, 50),
                'options': ['village', 'cave_interior'],
            }
        }
        self.items_for_sale = {
            'health_potion': {'price': 20, 'color': RED},
            'sword': {'price': 50, 'color': GRAY},
            'shield': {'price': 30, 'color': GOLD}
        }
        self.particles = []

    def show_message(self, text, duration=2000):
        self.message = text
        self.message_timer = duration

    def add_particle(self, x, y, color):
        self.particles.append({
            'x': x,
            'y': y,
            'dx': random.uniform(-2, 2),
            'dy': random.uniform(-2, 2),
            'lifetime': 30,
            'color': color
        })

    def update_particles(self):
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)

    def draw_particles(self, screen):
        for particle in self.particles:
            alpha = min(255, particle['lifetime'] * 8)
            color = list(particle['color'])
            if len(color) == 3:
                color.append(alpha)
            pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y']), 3))

    def handle_random_event(self):
        if random.random() < 0.1:  # 10% chance of random event
            events = [
                {'type': 'combat', 'damage': random.randint(5, 15), 'gold': random.randint(10, 30)},
                {'type': 'treasure', 'gold': random.randint(20, 50)},
                {'type': 'healing', 'amount': random.randint(10, 30)}
            ]
            event = random.choice(events)
            
            if event['type'] == 'combat':
                self.player.health -= event['damage']
                self.player.gold += event['gold']
                self.show_message(f"Combat! Lost {event['damage']} health, gained {event['gold']} gold")
                for _ in range(10):
                    self.add_particle(self.player.x, self.player.y, RED)
            
            elif event['type'] == 'treasure':
                self.player.gold += event['gold']
                self.show_message(f"Found treasure! Gained {event['gold']} gold")
                for _ in range(10):
                    self.add_particle(self.player.x, self.player.y, GOLD)
            
            elif event['type'] == 'healing':
                self.player.health = min(100, self.player.health + event['amount'])
                self.show_message(f"Healed for {event['amount']} health")
                for _ in range(10):
                    self.add_particle(self.player.x, self.player.y, GREEN)

    def run(self):
        try:
            # Get player name with error handling
            print("Welcome to the Adventure Game!")
            print("What is your name, brave adventurer?")
            name = input("> ").strip()
            if not name:
                name = "Adventurer"  # Default name if empty input
        except (EOFError, KeyboardInterrupt):
            print("\nGame terminated.")
            pygame.quit()
            sys.exit(0)
            
        self.player = Player(name)
        
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h and 'health_potion' in self.player.inventory:
                        self.player.inventory.remove('health_potion')
                        self.player.health = min(100, self.player.health + 50)
                        self.show_message("Used health potion!")
                        for _ in range(10):
                            self.add_particle(self.player.x, self.player.y, GREEN)

            # Handle movement
            keys = pygame.key.get_pressed()
            dx = keys[pygame.K_d] - keys[pygame.K_a]
            dy = keys[pygame.K_s] - keys[pygame.K_w]
            if dx != 0 or dy != 0:
                self.player.move(dx, dy)
                self.handle_random_event()

            # Update
            self.update_particles()
            if self.message_timer > 0:
                self.message_timer -= clock.get_time()

            # Draw
            location = self.locations[self.current_location]
            screen.fill(location['color'])
            
            # Draw particles
            self.draw_particles(screen)
            
            # Draw player
            self.player.draw(screen)
            
            # Draw UI
            pygame.draw.rect(screen, BLACK, (0, 0, WINDOW_WIDTH, 60))
            health_text = font_medium.render(f"Health: {self.player.health}", True, WHITE)
            gold_text = font_medium.render(f"Gold: {self.player.gold}", True, GOLD)
            location_text = font_medium.render(f"Location: {self.current_location.title()}", True, WHITE)
            
            screen.blit(health_text, (10, 10))
            screen.blit(gold_text, (200, 10))
            screen.blit(location_text, (400, 10))

            # Draw message
            if self.message_timer > 0:
                message_surface = font_large.render(self.message, True, WHITE)
                message_rect = message_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 50))
                screen.blit(message_surface, message_rect)

            # Draw inventory
            inventory_y = 70
            for item in self.player.inventory:
                item_text = font_small.render(item.replace('_', ' ').title(), True, WHITE)
                screen.blit(item_text, (10, inventory_y))
                inventory_y += 25

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
