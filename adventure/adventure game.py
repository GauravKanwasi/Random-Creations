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
CYAN = (0, 255, 255)

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
        self.glow_radius = size * 1.5
        self.trail = []
        
    def update(self):
        self.pulse_time += 0.1
        self.scale = 1.0 + math.sin(self.pulse_time) * 0.1
        
        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
    def draw(self, screen, color):
        # Draw trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)) * 0.5)
            trail_color = (*color[:3], alpha)
            trail_size = int(self.size * (i / len(self.trail)) * 0.5)
            trail_surface = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, trail_color, (trail_size, trail_size), trail_size)
            screen.blit(trail_surface, (tx - trail_size, ty - trail_size))

        # Draw glow
        glow_surface = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2), pygame.SRCALPHA)
        for r in range(int(self.glow_radius), 0, -2):
            alpha = int(100 * (r / self.glow_radius))
            glow_color = (*color[:3], alpha)
            pygame.draw.circle(glow_surface, glow_color, (self.glow_radius, self.glow_radius), r)
        screen.blit(glow_surface, (self.x - self.glow_radius, self.y - self.glow_radius))
        
        # Draw main sprite
        scaled_size = int(self.size * self.scale)
        surface = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (scaled_size//2, scaled_size//2), scaled_size//2)
        
        rotated_surface = pygame.transform.rotate(surface, self.angle)
        rect = rotated_surface.get_rect(center=(self.x, self.y))
        screen.blit(rotated_surface, rect)

class PowerUp(AnimatedSprite):
    def __init__(self, x, y):
        super().__init__(x, y, 20)
        self.type = random.choice(['health', 'shield', 'speed', 'power'])
        self.color = {
            'health': (255, 50, 50),
            'shield': (50, 50, 255),
            'speed': (50, 255, 50),
            'power': (255, 255, 0)
        }[self.type]
        self.collected = False
        
    def apply(self, player):
        if self.type == 'health':
            player.health = min(player.max_health, player.health + 50)
        elif self.type == 'shield':
            player.shield = min(player.max_shield, player.shield + 50)
        elif self.type == 'speed':
            player.speed = min(10, player.speed + 1)
        elif self.type == 'power':
            player.attack += 5

class Player(AnimatedSprite):
    def __init__(self, name):
        super().__init__(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 40)
        self.name = name
        self.health = 100
        self.max_health = 100
        self.shield = 100
        self.max_shield = 100
        self.inventory = []
        self.gold = 0
        self.speed = 5
        self.color = CYAN
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100
        self.attack = 10
        self.defense = 5
        self.combo = 0
        self.combo_timer = 0
        
    def gain_experience(self, amount):
        bonus = amount * (self.combo / 10) if self.combo > 0 else amount
        self.experience += bonus
        while self.experience >= self.exp_to_next_level:
            self.level_up()
            
    def level_up(self):
        self.level += 1
        self.experience -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        self.max_health += 20
        self.health = self.max_health
        self.max_shield += 10
        self.shield = self.max_shield
        self.attack += 5
        self.defense += 3
        return True

    def draw(self, screen):
        super().draw(screen, self.color)
        
        # Draw shield bar
        shield_width = 100
        shield_height = 10
        shield_x = self.x - shield_width//2
        shield_y = self.y - self.size//2 - 20
        
        pygame.draw.rect(screen, BLUE, (shield_x, shield_y, shield_width, shield_height))
        pygame.draw.rect(screen, CYAN, (shield_x, shield_y, shield_width * (self.shield/self.max_shield), shield_height))
        
        # Draw health bar
        health_width = 100
        health_height = 10
        health_x = self.x - health_width//2
        health_y = shield_y - 15
        
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
        pygame.draw.rect(screen, GREEN, (health_x, health_y, health_width * (self.health/self.max_health), health_height))
        
        # Draw experience bar
        exp_width = 100
        exp_height = 5
        exp_x = self.x - exp_width//2
        exp_y = health_y - 10
        
        pygame.draw.rect(screen, BLUE, (exp_x, exp_y, exp_width, exp_height))
        pygame.draw.rect(screen, PURPLE, (exp_x, exp_y, exp_width * (self.experience/self.exp_to_next_level), exp_height))
        
        # Draw combo counter if active
        if self.combo > 0:
            combo_text = font_medium.render(f"{self.combo}x", True, GOLD)
            screen.blit(combo_text, (self.x + 50, self.y - 50))

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
        self.attack_pattern = random.choice(['chase', 'circle', 'zigzag'])
        self.pattern_time = 0
        
    def update(self, player):
        super().update()
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        self.pattern_time += 0.05
        
        if self.attack_pattern == 'chase':
            if dist > 0:
                self.x += (dx/dist) * self.speed
                self.y += (dy/dist) * self.speed
        elif self.attack_pattern == 'circle':
            angle = self.pattern_time
            self.x = player.x + math.cos(angle) * 200
            self.y = player.y + math.sin(angle) * 200
        elif self.attack_pattern == 'zigzag':
            if dist > 0:
                self.x += (dx/dist) * self.speed
                self.y += (dy/dist) * self.speed + math.sin(self.pattern_time * 5) * 5
                
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
        self.power_ups = []
        self.message = ""
        self.message_timer = 0
        self.spawn_timer = 0
        self.power_up_timer = 0
        self.score = 0
        self.wave = 1
        self.wave_enemies = 5
        
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

    def spawn_power_up(self):
        x = random.randint(50, WINDOW_WIDTH - 50)
        y = random.randint(50, WINDOW_HEIGHT - 50)
        self.power_ups.append(PowerUp(x, y))

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
            pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y'])), particle['size'])

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
                        hit_enemy = False
                        for enemy in self.enemies[:]:
                            dx = enemy.x - self.player.x
                            dy = enemy.y - self.player.y
                            dist = math.sqrt(dx*dx + dy*dy)
                            if dist < 100:
                                damage = self.player.attack * (1 + self.player.combo * 0.1)
                                enemy.health -= damage
                                self.add_particle(enemy.x, enemy.y, RED)
                                hit_enemy = True
                                if enemy.health <= 0:
                                    self.player.gain_experience(enemy.experience_value)
                                    self.player.gold += enemy.gold_value
                                    self.score += 100 * (1 + self.player.combo * 0.1)
                                    self.enemies.remove(enemy)
                                    self.add_particle(enemy.x, enemy.y, GOLD, 3)
                                    
                        if hit_enemy:
                            self.player.combo += 1
                            self.player.combo_timer = 60
                        else:
                            self.player.combo = 0

            # Handle movement
            keys = pygame.key.get_pressed()
            dx = keys[pygame.K_d] - keys[pygame.K_a]
            dy = keys[pygame.K_s] - keys[pygame.K_w]
            if dx != 0 or dy != 0:
                self.player.move(dx, dy)

            # Update
            self.player.update()
            
            # Update combo timer
            if self.player.combo_timer > 0:
                self.player.combo_timer -= 1
                if self.player.combo_timer <= 0:
                    self.player.combo = 0
            
            # Spawn enemies
            self.spawn_timer += 1
            if self.spawn_timer >= 60 and len(self.enemies) < self.wave_enemies:
                self.spawn_enemy()
                self.spawn_timer = 0
                
            # Spawn power-ups
            self.power_up_timer += 1
            if self.power_up_timer >= 300:  # Every 5 seconds
                self.spawn_power_up()
                self.power_up_timer = 0
                
            # Check wave completion
            if len(self.enemies) == 0 and self.spawn_timer >= 60:
                self.wave += 1
                self.wave_enemies = int(self.wave_enemies * 1.5)
                self.show_message(f"Wave {self.wave} incoming!")
                self.spawn_timer = 0

            # Update enemies
            for enemy in self.enemies:
                enemy.update(self.player)
                
                # Check collision with player
                dx = enemy.x - self.player.x
                dy = enemy.y - self.player.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < (enemy.size + self.player.size) / 2:
                    # First damage shield
                    if self.player.shield > 0:
                        damage = max(1, 10 - self.player.defense)
                        self.player.shield -= damage
                        self.add_particle(self.player.x, self.player.y, BLUE)
                    else:  # Then damage health
                        damage = max(1, 10 - self.player.defense)
                        self.player.health -= damage
                        self.add_particle(self.player.x, self.player.y, RED)
                        if self.player.health <= 0:
                            running = False
                            
            # Update power-ups
            for power_up in self.power_ups[:]:
                dx = power_up.x - self.player.x
                dy = power_up.y - self.player.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < (power_up.size + self.player.size) / 2:
                    power_up.apply(self.player)
                    self.power_ups.remove(power_up)
                    self.add_particle(power_up.x, power_up.y, power_up.color, 3)
                    self.show_message(f"{power_up.type.capitalize()} power-up collected!")

            self.update_particles()
            if self.message_timer > 0:
                self.message_timer -= clock.get_time()

            # Draw
            screen.fill(BLACK)
            
            # Draw particles
            self.draw_particles(screen)
            
            # Draw power-ups
            for power_up in self.power_ups:
                power_up.draw(screen)
            
            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(screen)
            
            # Draw player
            self.player.draw(screen)
            
            # Draw UI
            pygame.draw.rect(screen, BLACK, (0, 0, WINDOW_WIDTH, 60))
            health_text = font_medium.render(f"Health: {int(self.player.health)}/{self.player.max_health}", True, WHITE)
            shield_text = font_medium.render(f"Shield: {int(self.player.shield)}/{self.player.max_shield}", True, CYAN)
            gold_text = font_medium.render(f"Gold: {self.player.gold}", True, GOLD)
            level_text = font_medium.render(f"Level: {self.player.level}", True, PURPLE)
            score_text = font_medium.render(f"Score: {int(self.score)}", True, WHITE)
            wave_text = font_medium.render(f"Wave: {self.wave}", True, RED)
            
            screen.blit(health_text, (10, 10))
            screen.blit(shield_text, (250, 10))
            screen.blit(gold_text, (500, 10))
            screen.blit(level_text, (700, 10))
            screen.blit(score_text, (10, 50))
            screen.blit(wave_text, (250, 50))

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
        score_text = font_medium.render(f"Final Score: {int(self.score)}", True, WHITE)
        wave_text = font_medium.render(f"Waves Survived: {self.wave}", True, RED)
        level_text = font_medium.render(f"Final Level: {self.player.level}", True, PURPLE)
        gold_text = font_medium.render(f"Gold Collected: {self.player.gold}", True, GOLD)
        
        screen.blit(game_over_text, game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100)))
        screen.blit(score_text, score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)))
        screen.blit(wave_text, wave_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50)))
        screen.blit(level_text, level_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 100)))
        screen.blit(gold_text, gold_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 150)))
        
        pygame.display.flip()
        pygame.time.wait(3000)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()