import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_MARGIN = 20
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
PURPLE = (147, 0, 211)
GOLD = (255, 215, 0)

# Initialize screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Memory Card Game")
clock = pygame.time.Clock()

class Card:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.revealed = False
        self.matched = False
        self.hover = False
        self.flip_progress = 0  # For flip animation
        
    def draw(self, screen):
        # Base color with hover and match effects
        color = BLUE if not self.hover else PURPLE
        if self.matched:
            color = GREEN
            
        # Card back design
        if not self.revealed and not self.matched:
            pygame.draw.rect(screen, color, (self.x, self.y, CARD_WIDTH, CARD_HEIGHT))
            # Add decorative pattern
            for i in range(0, CARD_WIDTH, 20):
                pygame.draw.line(screen, GOLD, 
                               (self.x + i, self.y), 
                               (self.x + i, self.y + CARD_HEIGHT), 
                               1)
            for i in range(0, CARD_HEIGHT, 20):
                pygame.draw.line(screen, GOLD, 
                               (self.x, self.y + i), 
                               (self.x + CARD_WIDTH, self.y + i), 
                               1)
        else:
            # Card front
            pygame.draw.rect(screen, color, (self.x, self.y, CARD_WIDTH, CARD_HEIGHT))
            font = pygame.font.Font(None, 48)
            text = font.render(str(self.value), True, WHITE)
            text_rect = text.get_rect(center=(self.x + CARD_WIDTH//2, self.y + CARD_HEIGHT//2))
            screen.blit(text, text_rect)
            
        # Card border
        pygame.draw.rect(screen, WHITE, (self.x, self.y, CARD_WIDTH, CARD_HEIGHT), 2)
            
    def contains_point(self, x, y):
        return (self.x <= x <= self.x + CARD_WIDTH and 
                self.y <= y <= self.y + CARD_HEIGHT)

class Game:
    def __init__(self):
        self.cards = []
        self.selected_cards = []
        self.moves = 0
        self.matches = 0
        self.game_over = False
        self.start_time = time.time()
        self.setup_cards()
        
    def setup_cards(self):  # Fixed: Added self parameter
        values = list(range(1, 9)) * 2
        random.shuffle(values)
        
        x_start = (WINDOW_WIDTH - (4 * (CARD_WIDTH + CARD_MARGIN))) // 2
        y_start = (WINDOW_HEIGHT - (4 * (CARD_HEIGHT + CARD_MARGIN))) // 2
        
        index = 0
        for row in range(4):
            for col in range(4):
                x = x_start + col * (CARD_WIDTH + CARD_MARGIN)
                y = y_start + row * (CARD_HEIGHT + CARD_MARGIN)
                self.cards.append(Card(x, y, values[index]))
                index += 1
                
    def handle_click(self, x, y):
        if len(self.selected_cards) >= 2:
            return
            
        for card in self.cards:
            if (card.contains_point(x, y) and 
                not card.matched and 
                not card.revealed and 
                card not in self.selected_cards):
                card.revealed = True
                self.selected_cards.append(card)
                
                if len(self.selected_cards) == 2:
                    self.moves += 1
                    if self.selected_cards[0].value == self.selected_cards[1].value:
                        self.selected_cards[0].matched = True
                        self.selected_cards[1].matched = True
                        self.matches += 1
                        self.selected_cards = []
                        
                        if self.matches == 8:
                            self.game_over = True
                    else:
                        pygame.time.set_timer(pygame.USEREVENT, 1000)
                break
                
    def update_hover(self, x, y):
        for card in self.cards:
            card.hover = card.contains_point(x, y) and not card.matched and not card.revealed
                
    def hide_selected_cards(self):
        for card in self.selected_cards:
            card.revealed = False
        self.selected_cards = []
        
    def draw(self, screen):
        # Draw background with gradient
        for i in range(WINDOW_HEIGHT):
            color = (
                max(0, min(255, i // 3)),
                0,
                max(0, min(255, 100 - i // 4))
            )
            pygame.draw.line(screen, color, (0, i), (WINDOW_WIDTH, i))
        
        # Draw cards
        for card in self.cards:
            card.draw(screen)
            
        # Draw UI with better styling
        # Draw header background
        pygame.draw.rect(screen, (0, 0, 0, 180), (0, 0, WINDOW_WIDTH, 130))
        
        font = pygame.font.Font(None, 36)
        moves_text = font.render(f"Moves: {self.moves}", True, WHITE)
        time_text = font.render(f"Time: {int(time.time() - self.start_time)}s", True, WHITE)
        matches_text = font.render(f"Matches: {self.matches}/8", True, WHITE)
        
        screen.blit(moves_text, (10, 10))
        screen.blit(time_text, (10, 50))
        screen.blit(matches_text, (10, 90))
        
        if self.game_over:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(180)
            screen.blit(overlay, (0, 0))
            
            font_large = pygame.font.Font(None, 74)
            game_over_text = font_large.render("Congratulations!", True, GOLD)
            screen.blit(game_over_text, game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)))
            
            font_medium = pygame.font.Font(None, 48)
            stats_text = font_medium.render(
                f"Completed in {self.moves} moves and {int(time.time() - self.start_time)} seconds", 
                True, WHITE
            )
            screen.blit(stats_text, stats_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50)))
            
            restart_text = font_medium.render("Press SPACE to play again", True, GREEN)
            screen.blit(restart_text, restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 100)))

def main():
    game = Game()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if not game.game_over:
                        game.handle_click(*event.pos)
            elif event.type == pygame.MOUSEMOTION:
                game.update_hover(*event.pos)
            elif event.type == pygame.USEREVENT:
                game.hide_selected_cards()
                pygame.time.set_timer(pygame.USEREVENT, 0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game.game_over:
                    game = Game()
                    
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
