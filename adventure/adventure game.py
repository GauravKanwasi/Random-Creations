import pygame
import random
import sys
import math
import os

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

# Initialize screen with vsync for smooth animation
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Epic Adventure")
clock = pygame.time.Clock()

# Load fonts
font_large = pygame.font.Font(None, 64)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)

class AnimatedSprite:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.angle = 0
        self.scale = 1.0
        self.pulse_time = 0
        
    def update(self):
        self.pulse_time += 0.1
        self.scale = 1.0 + math.sin(self.pulse_time) * 0.1
        
    def draw(self, screen, color):
        scaled_size = int(self.size * self.scale)
        surface = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
        pygame.draw.rect(surface, color, (0, 0, scaled_size, scaled_size))
        
        rotated_surface = pygame.transform.rotate(surface, self.angle)
        rect = rotated_surface.get_rect(center=(self.x, self.y))
        screen.blit(rotated_surface, rect)

class Player(AnimatedSprite):
    def __init__(self, name):
        super().__init__(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 40)
        self.name = name
        self.health = 100
        self.max_health = 100
        self.inventory = []
        self.gold = 0
        self.speed = 5
        self.color = GREEN
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100
        self.attack = 10
        self.defense = 5
        
    def gain_experience(self, amount):
        self.experience += amount
        while self.experience >= self.exp_to_next_level:
            self.level_up()
            
    def level_up(self):
        self.level += 1
        self.experience -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        self.max_health += 20
        self.health = self.max_health
        self.attack += 5
        self.defense += 3
        return True

    def draw(self, screen):
        super().draw(screen, self.color)
        
        # Draw health bar
        health_width = 100
        health_height = 10
        health_x = self.x - health_width//2
        health_y = self.y - self.size//2 - 20
        
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
        pygame.draw.rect(screen, GREEN, (health_x, health_y, health_width * (self.health/self.max_health), health_height))
        
        # Draw experience bar
        exp_width = 100
        exp_height = 5
        exp_x = self.x - exp_width//2
        exp_y = self.y - self.size//2 - 30
        
        pygame.draw.rect(screen, BLUE, (exp_x, exp_y, exp_width, exp_height))
        pygame.draw.rect(screen, PURPLE, (exp_x, exp_y, exp_width * (self.experience/self.exp_to_next_level), exp_height))

    def move(self, dx, dy):
        self.x = max(self.size//2, min(WINDOW_WIDTH - self.size//2, self.x + dx * self.speed))
        self.y = max(self.size//2, min(WINDOW_HEIGHT - self.size//2, self.y + dy * self.speed))
        self.angle = math.degrees(math.atan2(dy, dx)) if (dx != 0 or dy != 0) else self.angle

class Enemy(AnimatedSprite):
    def __init__(self, x, y):
        super().__init__(x, y, 30)
        self.health = 50
        self.max_health = 50
        self.speed = 2
        self.color = RED
        self.experience_value = 20
        self.gold_value = random.randint(5, 15)
        
    def update(self, player):
        super().update()
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.x += (dx/dist) * self.speed
            self.y += (dy/dist) * self.speed
            self.angle = math.degrees(math.atan2(dy, dx))
            
    def draw(self, screen):
        super().draw(screen, self.color)
        
        # Draw health bar
        health_width = 40
        health_height = 5
        health_x = self.x - health_width//2
        health_y = self.y - self.size//2 - 10
        
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
        pygame.draw.rect(screen, GREEN, (health_x, health_y, health_width * (self.health/self.max_health), health_height))

class Game:
    def __init__(self):
        self.player = None
        self.enemies = []
        self.particles = []
        self.message = ""
        self.message_timer = 0
        self.spawn_timer = 0
        self.score = 0
        
    def spawn_enemy(self):
        side = random.randint(0, 3)
        if side == 0:  # Top
            x = random.randint(0, WINDOW_WIDTH)
            y = -20
        elif side == 1:  # Right
            x = WINDOW_WIDTH + 20
            y = random.randint(0, WINDOW_HEIGHT)
        elif side == 2:  # Bottom
            x = random.randint(0, WINDOW_WIDTH)
            y = WINDOW_HEIGHT + 20
        else:  # Left
            x = -20
            y = random.randint(0, WINDOW_HEIGHT)
        
        self.enemies.append(Enemy(x, y))

    def add_particle(self, x, y, color, speed=2):
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed_var = random.uniform(0.5, 1.5) * speed
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed_var,
                'dy': math.sin(angle) * speed_var,
                'lifetime': 30,
                'color': color,
                'size': random.randint(2, 4)
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
            pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y']), particle['size']))

    def show_message(self, text, duration=2000):
        self.message = text
        self.message_timer = duration

    def run(self):
        try:
            print("Welcome to Epic Adventure!")
            print("What is your name, brave warrior?")
            name = input("> ").strip()
            if not name:
                name = "Warrior"
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
                    if event.key == pygame.K_SPACE:
                        # Attack nearby enemies
                        for enemy in self.enemies[:]:
                            dx = enemy.x - self.player.x
                            dy = enemy.y - self.player.y
                            dist = math.sqrt(dx*dx + dy*dy)
                            if dist < 100:
                                damage = self.player.attack
                                enemy.health -= damage
                                self.add_particle(enemy.x, enemy.y, RED)
                                if enemy.health <= 0:
                                    self.player.gain_experience(enemy.experience_value)
                                    self.player.gold += enemy.gold_value
                                    self.score += 100
                                    self.enemies.remove(enemy)
                                    self.add_particle(enemy.x, enemy.y, GOLD, 3)
                                    if self.player.level_up():
                                        self.show_message(f"Level Up! Now level {self.player.level}!")

            # Handle movement
            keys = pygame.key.get_pressed()
            dx = keys[pygame.K_d] - keys[pygame.K_a]
            dy = keys[pygame.K_s] - keys[pygame.K_w]
            if dx != 0 or dy != 0:
                self.player.move(dx, dy)

            # Update
            self.player.update()
            self.spawn_timer += 1
            if self.spawn_timer >= 60:  # Spawn enemy every second
                self.spawn_enemy()
                self.spawn_timer = 0

            for enemy in self.enemies:
                enemy.update(self.player)
                
                # Check collision with player
                dx = enemy.x - self.player.x
                dy = enemy.y - self.player.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < (enemy.size + self.player.size) / 2:
                    damage = max(1, 10 - self.player.defense)
                    self.player.health -= damage
                    self.add_particle(self.player.x, self.player.y, RED)
                    if self.player.health <= 0:
                        running = False

            self.update_particles()
            if self.message_timer > 0:
                self.message_timer -= clock.get_time()

            # Draw
            screen.fill(BLACK)
            
            # Draw particles
            self.draw_particles(screen)
            
            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(screen)
            
            # Draw player
            self.player.draw(screen)
            
            # Draw UI
            pygame.draw.rect(screen, BLACK, (0, 0, WINDOW_WIDTH, 60))
            health_text = font_medium.render(f"Health: {self.player.health}/{self.player.max_health}", True, WHITE)
            gold_text = font_medium.render(f"Gold: {self.player.gold}", True, GOLD)
            level_text = font_medium.render(f"Level: {self.player.level}", True, PURPLE)
            score_text = font_medium.render(f"Score: {self.score}", True, WHITE)
            
            screen.blit(health_text, (10, 10))
            screen.blit(gold_text, (300, 10))
            screen.blit(level_text, (500, 10))
            screen.blit(score_text, (700, 10))

            # Draw message
            if self.message_timer > 0:
                message_surface = font_large.render(self.message, True, WHITE)
                message_rect = message_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 50))
                screen.blit(message_surface, message_rect)

            pygame.display.flip()
            clock.tick(FPS)

        # Game Over
        screen.fill(BLACK)
        game_over_text = font_large.render("Game Over!", True, RED)
        score_text = font_medium.render(f"Final Score: {self.score}", True, WHITE)
        level_text = font_medium.render(f"Final Level: {self.player.level}", True, PURPLE)
        
        screen.blit(game_over_text, game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50)))
        screen.blit(score_text, score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20)))
        screen.blit(level_text, level_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 70)))
        
        pygame.display.flip()
        pygame.time.wait(3000)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()