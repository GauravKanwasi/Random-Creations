import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
TILE_SIZE = 64
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
GOLD = (255, 215, 0)
BROWN = (139, 69, 19)

# Initialize screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Dungeon Adventure")
clock = pygame.time.Clock()

class Entity:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.health = 100
        self.max_health = 100
        self.speed = 5
        
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Only draw if on screen
        if (0 <= screen_x <= WINDOW_WIDTH and 
            0 <= screen_y <= WINDOW_HEIGHT):
            pygame.draw.rect(screen, self.color, 
                           (screen_x - self.size//2, 
                            screen_y - self.size//2, 
                            self.size, self.size))
            
            # Health bar
            health_width = self.size
            health_height = 5
            pygame.draw.rect(screen, RED, 
                           (screen_x - health_width//2, 
                            screen_y - self.size//2 - 10, 
                            health_width, health_height))
            pygame.draw.rect(screen, GREEN, 
                           (screen_x - health_width//2, 
                            screen_y - self.size//2 - 10, 
                            health_width * (self.health/self.max_health), 
                            health_height))

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 40, BLUE)
        self.attack_power = 25
        self.defense = 5
        self.gold = 0
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100
        
    def move(self, dx, dy, walls):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # Check wall collisions
        can_move = True
        for wall in walls:
            if (abs(new_x - wall.x) < (self.size + wall.size)//2 and 
                abs(new_y - wall.y) < (self.size + wall.size)//2):
                can_move = False
                break
                
        if can_move:
            self.x = new_x
            self.y = new_y
            
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
        self.attack_power += 5
        self.defense += 2
        return True

class Monster(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 30, RED)
        self.speed = 3
        self.health = 50
        self.max_health = 50
        self.attack_power = 10
        self.exp_value = 30
        self.gold_value = random.randint(5, 15)
        
    def update(self, player, walls):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < 400:  # Only chase within range
            if dist > 0:
                dx = dx/dist * self.speed
                dy = dy/dist * self.speed
                
                new_x = self.x + dx
                new_y = self.y + dy
                
                # Check wall collisions
                can_move = True
                for wall in walls:
                    if (abs(new_x - wall.x) < (self.size + wall.size)//2 and 
                        abs(new_y - wall.y) < (self.size + wall.size)//2):
                        can_move = False
                        break
                        
                if can_move:
                    self.x = new_x
                    self.y = new_y

class Wall(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, TILE_SIZE, GRAY)

class Treasure(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 20, GOLD)
        self.value = random.randint(10, 30)

class Game:
    def __init__(self):
        self.player = Player(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
        self.walls = []
        self.monsters = []
        self.treasures = []
        self.camera_x = 0
        self.camera_y = 0
        self.generate_dungeon()
        
    def generate_dungeon(self):
        # Create dungeon walls
        for x in range(-20, 21):
            for y in range(-20, 21):
                if random.random() < 0.3:  # 30% chance for a wall
                    wall_x = x * TILE_SIZE
                    wall_y = y * TILE_SIZE
                    self.walls.append(Wall(wall_x, wall_y))
                    
        # Add monsters
        for _ in range(20):
            while True:
                x = random.randint(-20, 20) * TILE_SIZE
                y = random.randint(-20, 20) * TILE_SIZE
                
                # Check if position is clear
                clear = True
                for wall in self.walls:
                    if (abs(x - wall.x) < TILE_SIZE and 
                        abs(y - wall.y) < TILE_SIZE):
                        clear = False
                        break
                        
                if clear:
                    self.monsters.append(Monster(x, y))
                    break
                    
        # Add treasures
        for _ in range(10):
            while True:
                x = random.randint(-20, 20) * TILE_SIZE
                y = random.randint(-20, 20) * TILE_SIZE
                
                # Check if position is clear
                clear = True
                for wall in self.walls:
                    if (abs(x - wall.x) < TILE_SIZE and 
                        abs(y - wall.y) < TILE_SIZE):
                        clear = False
                        break
                        
                if clear:
                    self.treasures.append(Treasure(x, y))
                    break
    
    def update_camera(self):
        self.camera_x = self.player.x - WINDOW_WIDTH//2
        self.camera_y = self.player.y - WINDOW_HEIGHT//2
        
    def run(self):
        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Attack nearby monsters
                    for monster in self.monsters[:]:
                        dx = monster.x - self.player.x
                        dy = monster.y - self.player.y
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist < 100:
                            monster.health -= self.player.attack_power
                            if monster.health <= 0:
                                self.monsters.remove(monster)
                                self.player.gain_experience(monster.exp_value)
                                self.player.gold += monster.gold_value
                    
            # Movement
            keys = pygame.key.get_pressed()
            dx = keys[pygame.K_d] - keys[pygame.K_a]
            dy = keys[pygame.K_s] - keys[pygame.K_w]
            if dx != 0 or dy != 0:
                self.player.move(dx, dy, self.walls)
                
            # Update monsters
            for monster in self.monsters:
                monster.update(self.player, self.walls)
                
                # Check collision with player
                dx = monster.x - self.player.x
                dy = monster.y - self.player.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < (monster.size + self.player.size)//2:
                    damage = max(1, monster.attack_power - self.player.defense)
                    self.player.health -= damage
                    if self.player.health <= 0:
                        running = False
                        
            # Check treasure collection
            for treasure in self.treasures[:]:
                dx = treasure.x - self.player.x
                dy = treasure.y - self.player.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < (treasure.size + self.player.size)//2:
                    self.player.gold += treasure.value
                    self.treasures.remove(treasure)
                    
            # Update camera
            self.update_camera()
            
            # Draw
            screen.fill(BLACK)
            
            # Draw walls
            for wall in self.walls:
                wall.draw(screen, self.camera_x, self.camera_y)
                
            # Draw treasures
            for treasure in self.treasures:
                treasure.draw(screen, self.camera_x, self.camera_y)
                
            # Draw monsters
            for monster in self.monsters:
                monster.draw(screen, self.camera_x, self.camera_y)
                
            # Draw player
            self.player.draw(screen, self.camera_x, self.camera_y)
            
            # Draw UI
            font = pygame.font.Font(None, 36)
            health_text = font.render(f"Health: {self.player.health}/{self.player.max_health}", True, WHITE)
            gold_text = font.render(f"Gold: {self.player.gold}", True, GOLD)
            level_text = font.render(f"Level: {self.player.level}", True, WHITE)
            exp_text = font.render(f"EXP: {self.player.experience}/{self.player.exp_to_next_level}", True, WHITE)
            
            screen.blit(health_text, (10, 10))
            screen.blit(gold_text, (10, 50))
            screen.blit(level_text, (10, 90))
            screen.blit(exp_text, (10, 130))
            
            pygame.display.flip()
            clock.tick(FPS)
            
        # Game Over
        screen.fill(BLACK)
        font_large = pygame.font.Font(None, 74)
        font_medium = pygame.font.Font(None, 48)
        
        game_over_text = font_large.render("Game Over!", True, RED)
        score_text = font_medium.render(f"Gold Collected: {self.player.gold}", True, GOLD)
        level_text = font_medium.render(f"Final Level: {self.player.level}", True, WHITE)
        
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