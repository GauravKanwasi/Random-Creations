import pygame
import random
import sys
import math
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

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

# Initialize screen and audio
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Epic Adventure")
clock = pygame.time.Clock()
hit_sound = pygame.mixer.Sound('hit.wav')  # Requires hit.wav
powerup_sound = pygame.mixer.Sound('powerup.wav')  # Requires powerup.wav
pygame.mixer.music.load('background.mp3')  # Requires background.mp3
pygame.mixer.music.play(-1)

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
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
    def draw(self, screen, color):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)) * 0.5)
            trail_color = (*color[:3], alpha)
            trail_size = int(self.size * (i / len(self.trail)) * 0.5)
            trail_surface = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, trail_color, (trail_size, trail_size), trail_size)
            screen.blit(trail_surface, (tx - trail_size, ty - trail_size))

        glow_surface = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2), pygame.SRCALPHA)
        for r in range(int(self.glow_radius), 0, -2):
            alpha = int(100 * (r / self.glow_radius))
            glow_color = (*color[:3], alpha)
            pygame.draw.circle(glow_surface, glow_color, (self.glow_radius, self.glow_radius), r)
        screen.blit(glow_surface, (self.x - self.glow_radius, self.y - self.glow_radius))
        
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

    def draw(self, screen):
        super().draw(screen, self.color)
        shield_width = 100
        shield_height = 10
        shield_x = self.x - shield_width//2
        shield_y = self.y - self.size//2 - 20
        pygame.draw.rect(screen, BLUE, (shield_x, shield_y, shield_width, shield_height))
        pygame.draw.rect(screen, CYAN, (shield_x, shield_y, shield_width * (self.shield/self.max_shield), shield_height))
        health_width = 100
        health_height = 10
        health_x = self.x - health_width//2
        health_y = shield_y - 15
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
        pygame.draw.rect(screen, GREEN, (health_x, health_y, health_width * (self.health/self.max_health), health_height))
        exp_width = 100
        exp_height = 5
        exp_x = self.x - exp_width//2
        exp_y = health_y - 10
        pygame.draw.rect(screen, BLUE, (exp_x, exp_y, exp_width, exp_height))
        pygame.draw.rect(screen, PURPLE, (exp_x, exp_y, exp_width * (self.experience/self.exp_to_next_level), exp_height))
        if self.combo > 0:
            combo_text = font_medium.render(f"{self.combo}x", True, GOLD)
            screen.blit(combo_text, (self.x + 50, self.y - 50))

    def move(self, dx, dy):
        self.x = max(self.size//2, min(WINDOW_WIDTH - self.size//2, self.x + dx * self.speed))
        self.y = max(self.size//2, min(WINDOW_HEIGHT - self.size//2, self.y + dy * self.speed))
        self.angle = math.degrees(math.atan2(dy, dx)) if (dx != 0 or dy != 0) else self.angle

class Enemy(AnimatedSprite):
    def __init__(self, x, y, wave):
        super().__init__(x, y, 30)
        self.health = 50 + 10 * wave
        self.max_health = self.health
        self.speed = 2 + 0.1 * wave
        self.color = RED
        self.experience_value = 20 + 5 * wave
        self.gold_value = random.randint(5 + wave, 15 + wave * 2)
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
        health_width = 40
        health_height = 5
        health_x = self.x - health_width//2
        health_y = self.y - self.size//2 - 10
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
        pygame.draw.rect(screen, GREEN, (health_x, health_y, health_width * (self.health/self.max_health), health_height))

class BossEnemy(Enemy):
    def __init__(self, x, y, wave):
        super().__init__(x, y, wave)
        self.health = 200 + 50 * wave
        self.max_health = self.health
        self.speed = 1.5 + 0.05 * wave
        self.color = PURPLE
        self.experience_value = 100 + 20 * wave
        self.gold_value = 50 + 10 * wave
        self.size = 50

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
        self.state = "playing"
        self.selected_item = 0
        self.is_boss_wave = False
        self.player_hit_timer = 0
        self.shop_items = [
            {"name": "Health Potion", "cost": 75, "effect": lambda p: setattr(p, 'health', min(p.max_health, p.health + 50))},
            {"name": "Shield Recharge", "cost": 75, "effect": lambda p: setattr(p, 'shield', min(p.max_shield, p.shield + 50))},
            {"name": "Attack Boost", "cost": 150, "effect": lambda p: setattr(p, 'attack', p.attack + 5)},
            {"name": "Defense Boost", "cost": 150, "effect": lambda p: setattr(p, 'defense', p.defense + 3)},
            {"name": "Speed Boost", "cost": 150, "effect": lambda p: setattr(p, 'speed', min(10, p.speed + 1))},
            {"name": "Proceed to next wave", "cost": 0, "effect": lambda p: None}
        ]
        
    def spawn_enemy(self):
        side = random.randint(0, 3)
        if side == 0:
            x = random.randint(0, WINDOW_WIDTH)
            y = -20
        elif side == 1:
            x = WINDOW_WIDTH + 20
            y = random.randint(0, WINDOW_HEIGHT)
        elif side == 2:
            x = random.randint(0, WINDOW_WIDTH)
            y = WINDOW_HEIGHT + 20
        else:
            x = -20
            y = random.randint(0, WINDOW_HEIGHT)
        if self.is_boss_wave:
            self.enemies.append(BossEnemy(x, y, self.wave))
        else:
            self.enemies.append(Enemy(x, y, self.wave))

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
        name = ""
        input_active = True
        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event.unicode.isalnum():
                        name += event.unicode
            screen.fill(BLACK)
            prompt = font_large.render("Enter your name:", True, WHITE)
            name_text = font_medium.render(name, True, CYAN)
            screen.blit(prompt, (WINDOW_WIDTH//2 - prompt.get_width()//2, WINDOW_HEIGHT//2 - 50))
            screen.blit(name_text, (WINDOW_WIDTH//2 - name_text.get_width()//2, WINDOW_HEIGHT//2 + 50))
            pygame.display.flip()
            clock.tick(FPS)
        self.player = Player(name or "Warrior")
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == "playing":
                        if event.key == pygame.K_SPACE:
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
                                hit_sound.play()
                                self.player.combo += 1
                                self.player.combo_timer = 60
                            else:
                                self.player.combo = 0
                    elif self.state == "shop":
                        if event.key == pygame.K_UP:
                            self.selected_item = (self.selected_item - 1) % len(self.shop_items)
                        elif event.key == pygame.K_DOWN:
                            self.selected_item = (self.selected_item + 1) % len(self.shop_items)
                        elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                            item = self.shop_items[self.selected_item]
                            if item["name"] == "Proceed to next wave":
                                self.state = "playing"
                                self.wave += 1
                                if self.wave % 5 == 0:
                                    self.is_boss_wave = True
                                    self.wave_enemies = 1
                                else:
                                    self.is_boss_wave = False
                                    self.wave_enemies = int(self.wave_enemies * 1.5) if self.wave > 1 else 5
                                self.spawn_timer = 0
                            elif self.player.gold >= item["cost"]:
                                item["effect"](self.player)
                                self.player.gold -= item["cost"]
                                self.show_message(f"Purchased {item['name']}!")
                            else:
                                self.show_message("Not enough gold!")

            self.update_particles()
            if self.message_timer > 0:
                self.message_timer -= clock.get_time()

            if self.state == "playing":
                keys = pygame.key.get_pressed()
                dx = keys[pygame.K_d] - keys[pygame.K_a]
                dy = keys[pygame.K_s] - keys[pygame.K_w]
                if dx != 0 or dy != 0:
                    self.player.move(dx, dy)
                self.player.update()
                if self.player.combo_timer > 0:
                    self.player.combo_timer -= 1
                    if self.player.combo_timer <= 0:
                        self.player.combo = 0
                self.spawn_timer += 1
                if self.spawn_timer >= 60 and len(self.enemies) < self.wave_enemies:
                    self.spawn_enemy()
                    self.spawn_timer = 0
                self.power_up_timer += 1
                if self.power_up_timer >= 300:
                    self.spawn_power_up()
                    self.power_up_timer = 0
                for enemy in self.enemies:
                    enemy.update(self.player)
                    dx = enemy.x - self.player.x
                    dy = enemy.y - self.player.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < (enemy.size + self.player.size) / 2:
                        if self.player.shield > 0:
                            damage = max(1, 10 - self.player.defense)
                            self.player.shield -= damage
                            self.add_particle(self.player.x, self.player.y, BLUE)
                        else:
                            damage = max(1, 10 - self.player.defense)
                            self.player.health -= damage
                            self.add_particle(self.player.x, self.player.y, RED)
                            self.player_hit_timer = 10
                            if self.player.health <= 0:
                                running = False
                for power_up in self.power_ups[:]:
                    dx = power_up.x - self.player.x
                    dy = power_up.y - self.player.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < (power_up.size + self.player.size) / 2:
                        power_up.apply(self.player)
                        self.power_ups.remove(power_up)
                        powerup_sound.play()
                        self.add_particle(power_up.x, power_up.y, power_up.color, 3)
                        self.show_message(f"{power_up.type.capitalize()} power-up collected!")
                if len(self.enemies) == 0:
                    self.state = "shop"
                    self.selected_item = 0
                    self.show_message("Wave cleared! Visit the shop.")

            screen.fill(BLACK)
            self.draw_particles(screen)
            for power_up in self.power_ups:
                power_up.draw(screen)
            for enemy in self.enemies:
                enemy.draw(screen)
            self.player.draw(screen)
            for enemy in self.enemies:
                if enemy.x < 0 or enemy.x > WINDOW_WIDTH or enemy.y < 0 or enemy.y > WINDOW_HEIGHT:
                    dx = enemy.x - self.player.x
                    dy = enemy.y - self.player.y
                    angle = math.atan2(dy, dx)
                    arrow_x = self.player.x + math.cos(angle) * 100
                    arrow_y = self.player.y + math.sin(angle) * 100
                    arrow_x = max(20, min(WINDOW_WIDTH - 20, arrow_x))
                    arrow_y = max(20, min(WINDOW_HEIGHT - 20, arrow_y))
                    pygame.draw.line(screen, RED, (arrow_x, arrow_y), 
                                    (arrow_x + math.cos(angle) * 20, arrow_y + math.sin(angle) * 20), 5)
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

            if self.state == "shop":
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                screen.blit(overlay, (0, 0))
                shop_text = font_large.render("Shop", True, WHITE)
                screen.blit(shop_text, (WINDOW_WIDTH//2 - shop_text.get_width()//2, 100))
                gold_text = font_medium.render(f"Gold: {self.player.gold}", True, GOLD)
                screen.blit(gold_text, (WINDOW_WIDTH//2 - gold_text.get_width()//2, 150))
                for i, item in enumerate(self.shop_items):
                    color = CYAN if i == self.selected_item else WHITE
                    item_text = font_medium.render(f"{item['name']} - {item['cost']}g", True, color)
                    screen.blit(item_text, (WINDOW_WIDTH//2 - item_text.get_width()//2, 200 + i * 50))

            if self.message_timer > 0:
                message_surface = font_large.render(self.message, True, WHITE)
                message_rect = message_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 50))
                screen.blit(message_surface, message_rect)

            if self.player_hit_timer > 0:
                flash_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                flash_surface.fill((255, 0, 0, 128))
                screen.blit(flash_surface, (0, 0))
                self.player_hit_timer -= 1

            pygame.display.flip()
            clock.tick(FPS)

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
