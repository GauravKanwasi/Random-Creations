import pygame
import random
import sys
import time
import os
import json

# Initialize Pygame
pygame.init()
pygame.mixer.init()

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

# Try to load sounds (will fail silently if files don't exist)
sounds = {}
try:
    sounds["flip"] = pygame.mixer.Sound("flip.wav")
    sounds["match"] = pygame.mixer.Sound("match.wav")
    sounds["wrong"] = pygame.mixer.Sound("wrong.wav")
    sounds["win"] = pygame.mixer.Sound("win.wav")
    sounds["click"] = pygame.mixer.Sound("click.wav")
except:
    # Create placeholder sound if files aren't found
    empty_sound = pygame.mixer.Sound(buffer=bytearray(100))
    sounds = {
        "flip": empty_sound,
        "match": empty_sound,
        "wrong": empty_sound,
        "win": empty_sound,
        "click": empty_sound
    }

# Button class for UI
class Button:
    def __init__(self, x, y, width, height, text, color=BLUE, hover_color=PURPLE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.hover = False
        
    def draw(self, surface):
        color = self.hover_color if self.hover else self.color
        
        # Draw button with rounded corners (simulated)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        # Draw text
        font = pygame.font.Font(None, 30)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class Card:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.revealed = False
        self.matched = False
        self.hover = False
        self.flip_progress = 0  # For flip animation (0-100)
        self.flip_direction = 0  # 1 = flipping to front, -1 = flipping to back
        self.scale = 1.0  # For hover effect
        
    def start_flip(self, to_front=True):
        self.flip_direction = 1 if to_front else -1
        if to_front:
            sounds["flip"].play()
        
    def update(self):
        # Update flip animation
        if self.flip_direction != 0:
            self.flip_progress += self.flip_direction * 5
            
            if self.flip_progress >= 100:
                self.flip_progress = 100
                self.flip_direction = 0
                self.revealed = True
            elif self.flip_progress <= 0:
                self.flip_progress = 0
                self.flip_direction = 0
                self.revealed = False
                
        # Update hover animation
        target_scale = 1.05 if self.hover else 1.0
        self.scale += (target_scale - self.scale) * 0.2
            
    def draw(self, screen):
        # Calculate dimensions with scale for hover effect
        scaled_width = int(CARD_WIDTH * self.scale)
        scaled_height = int(CARD_HEIGHT * self.scale)
        # Adjust position to keep card centered while scaling
        scaled_x = self.x - (scaled_width - CARD_WIDTH) // 2
        scaled_y = self.y - (scaled_height - CARD_HEIGHT) // 2
        
        # Flip animation
        if self.flip_progress > 0 and self.flip_progress < 100:
            # During flip animation, calculate width based on progress
            flip_factor = abs((self.flip_progress - 50) / 50)
            width = max(1, int(scaled_width * flip_factor))
            x_offset = (scaled_width - width) // 2
            
            # Determine which side to show based on flip progress
            if self.flip_progress < 50:
                # Show back of card (getting narrower)
                color = BLUE if not self.hover else PURPLE
                if self.matched:
                    color = GREEN
                    
                pygame.draw.rect(screen, color, (scaled_x + x_offset, scaled_y, width, scaled_height))
                # Add decorative pattern
                stripe_width = max(1, width // 5)
                for i in range(0, width, stripe_width):
                    pygame.draw.line(screen, GOLD, 
                                   (scaled_x + x_offset + i, scaled_y), 
                                   (scaled_x + x_offset + i, scaled_y + scaled_height), 
                                   1)
            else:
                # Show front of card (getting wider)
                color = BLUE if not self.hover else PURPLE
                if self.matched:
                    color = GREEN
                    
                pygame.draw.rect(screen, color, (scaled_x + x_offset, scaled_y, width, scaled_height))
                
                # Only show value if the card is wide enough
                if width > scaled_width // 2:
                    font = pygame.font.Font(None, 48)
                    text = font.render(str(self.value), True, WHITE)
                    text_rect = text.get_rect(center=(scaled_x + x_offset + width//2, scaled_y + scaled_height//2))
                    screen.blit(text, text_rect)
        else:
            # Normal drawing (not animating)
            # Base color with hover and match effects
            color = BLUE if not self.hover else PURPLE
            if self.matched:
                color = GREEN
                
            # Card back design
            if not self.revealed and not self.matched:
                pygame.draw.rect(screen, color, (scaled_x, scaled_y, scaled_width, scaled_height))
                # Add decorative pattern
                for i in range(0, scaled_width, 20):
                    pygame.draw.line(screen, GOLD, 
                                   (scaled_x + i, scaled_y), 
                                   (scaled_x + i, scaled_y + scaled_height), 
                                   1)
                for i in range(0, scaled_height, 20):
                    pygame.draw.line(screen, GOLD, 
                                   (scaled_x, scaled_y + i), 
                                   (scaled_x + scaled_width, scaled_y + i), 
                                   1)
            else:
                # Card front
                pygame.draw.rect(screen, color, (scaled_x, scaled_y, scaled_width, scaled_height))
                font = pygame.font.Font(None, 48)
                text = font.render(str(self.value), True, WHITE)
                text_rect = text.get_rect(center=(scaled_x + scaled_width//2, scaled_y + scaled_height//2))
                screen.blit(text, text_rect)
                
            # Card border - thicker when hovering
            border_width = 3 if self.hover else 2
            pygame.draw.rect(screen, WHITE, (scaled_x, scaled_y, scaled_width, scaled_height), border_width)
            
    def contains_point(self, x, y):
        # Use original dimensions for hit detection
        return (self.x <= x <= self.x + CARD_WIDTH and 
                self.y <= y <= self.y + CARD_HEIGHT)

class Game:
    def __init__(self, difficulty="medium"):
        self.difficulty = difficulty
        self.cards = []
        self.selected_cards = []
        self.moves = 0
        self.matches = 0
        self.game_over = False
        self.start_time = time.time()
        self.elapsed_time = 0
        self.paused = False
        self.score = 0
        self.setup_cards()
        self.high_scores = self.load_high_scores()
        
        # Difficulty settings
        self.difficulty_settings = {
            "easy": {"pairs": 6, "rows": 3, "cols": 4},
            "medium": {"pairs": 8, "rows": 4, "cols": 4},
            "hard": {"pairs": 10, "rows": 4, "cols": 5}
        }
        
    def setup_cards(self):
        # Clear existing cards
        self.cards = []
        
        # Get settings based on difficulty
        settings = self.difficulty_settings[self.difficulty]
        pairs = settings["pairs"]
        rows = settings["rows"]
        cols = settings["cols"]
        
        # Create values (pairs of numbers)
        values = list(range(1, pairs + 1)) * 2
        random.shuffle(values)
        
        # Calculate layout
        total_width = cols * (CARD_WIDTH + CARD_MARGIN) - CARD_MARGIN
        total_height = rows * (CARD_HEIGHT + CARD_MARGIN) - CARD_MARGIN
        
        x_start = (WINDOW_WIDTH - total_width) // 2
        y_start = (WINDOW_HEIGHT - total_height) // 2 + 40  # Adjusted for UI elements
        
        index = 0
        for row in range(rows):
            for col in range(cols):
                if index < len(values):
                    x = x_start + col * (CARD_WIDTH + CARD_MARGIN)
                    y = y_start + row * (CARD_HEIGHT + CARD_MARGIN)
                    self.cards.append(Card(x, y, values[index]))
                    index += 1
                
    def handle_click(self, x, y):
        if len(self.selected_cards) >= 2 or self.paused or self.game_over:
            return
            
        for card in self.cards:
            if (card.contains_point(x, y) and 
                not card.matched and 
                not card.revealed and 
                card not in self.selected_cards):
                
                card.start_flip(to_front=True)
                self.selected_cards.append(card)
                
                if len(self.selected_cards) == 2:
                    self.moves += 1
                    if self.selected_cards[0].value == self.selected_cards[1].value:
                        # Match found
                        pygame.time.set_timer(pygame.USEREVENT, 500)  # Short delay for match
                        sounds["match"].play()
                    else:
                        # No match
                        pygame.time.set_timer(pygame.USEREVENT, 1000)  # Longer delay for no match
                        sounds["wrong"].play()
                break
                
    def update_hover(self, x, y):
        for card in self.cards:
            prev_hover = card.hover
            card.hover = card.contains_point(x, y) and not card.matched and not card.revealed and not self.game_over
            if card.hover and not prev_hover:
                sounds["click"].play()
                
    def hide_selected_cards(self):
        if len(self.selected_cards) == 2:
            if self.selected_cards[0].value == self.selected_cards[1].value:
                # Cards match
                self.selected_cards[0].matched = True
                self.selected_cards[1].matched = True
                self.matches += 1
                
                # Check if all matched
                total_pairs = self.difficulty_settings[self.difficulty]["pairs"]
                if self.matches == total_pairs:
                    self.game_over = True
                    self.elapsed_time = time.time() - self.start_time
                    self.calculate_score()
                    sounds["win"].play()
                    self.update_high_scores()
            else:
                # Cards don't match, flip them back
                for card in self.selected_cards:
                    card.start_flip(to_front=False)
                    
        self.selected_cards = []
    
    def update(self):
        for card in self.cards:
            card.update()
    
    def calculate_score(self):
        # Score formula: base points - penalties for moves and time
        base_points = {
            "easy": 1000,
            "medium": 2000,
            "hard": 3000
        }[self.difficulty]
        
        # Penalties
        move_penalty = self.moves * 10
        time_penalty = int(self.elapsed_time) * 5
        
        # Calculate final score
        self.score = max(0, base_points - move_penalty - time_penalty)
    
    def load_high_scores(self):
        try:
            if os.path.exists("high_scores.json"):
                with open("high_scores.json", "r") as f:
                    return json.load(f)
            else:
                return {"easy": [], "medium": [], "hard": []}
        except:
            return {"easy": [], "medium": [], "hard": []}
    
    def save_high_scores(self):
        try:
            with open("high_scores.json", "w") as f:
                json.dump(self.high_scores, f)
        except:
            pass
    
    def update_high_scores(self):
        # Add current score to high scores
        self.high_scores[self.difficulty].append({
            "score": self.score,
            "moves": self.moves,
            "time": self.elapsed_time,
            "date": time.strftime("%Y-%m-%d %H:%M")
        })
        
        # Sort by score (highest first) and keep only top 5
        self.high_scores[self.difficulty] = sorted(
            self.high_scores[self.difficulty], 
            key=lambda x: x["score"], 
            reverse=True
        )[:5]
        
        # Save to file
        self.save_high_scores()
        
    def draw(self, screen):
        # Draw background with gradient
        for i in range(WINDOW_HEIGHT):
            color = (
                max(0, min(255, i // 3)),
                0,
                max(0, min(255, 100 - i // 4))
            )
            pygame.draw.line(screen, color, (0, i), (WINDOW_WIDTH, i))
        
        # Draw header with translucent panel
        header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 80)
        header_surf = pygame.Surface((WINDOW_WIDTH, 80), pygame.SRCALPHA)
        header_surf.fill((0, 0, 0, 180))
        screen.blit(header_surf, header_rect)
        
        # Draw UI with better styling
        font = pygame.font.Font(None, 30)
        
        # Draw difficulty indicator
        diff_text = font.render(f"Difficulty: {self.difficulty.capitalize()}", True, GOLD)
        screen.blit(diff_text, (20, 10))
        
        # Draw stats
        moves_text = font.render(f"Moves: {self.moves}", True, WHITE)
        if not self.game_over:
            time_value = int(time.time() - self.start_time)
        else:
            time_value = int(self.elapsed_time)
        time_text = font.render(f"Time: {time_value}s", True, WHITE)
        
        total_pairs = self.difficulty_settings[self.difficulty]["pairs"]
        matches_text = font.render(f"Matches: {self.matches}/{total_pairs}", True, WHITE)
        
        screen.blit(moves_text, (20, 40))
        screen.blit(time_text, (180, 40))
        screen.blit(matches_text, (320, 40))
        
        # Draw cards
        for card in self.cards:
            card.draw(screen)
            
        # Draw game over screen
        if self.game_over:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            # Create a panel for the victory message
            panel_width = 500
            panel_height = 350
            panel_x = (WINDOW_WIDTH - panel_width) // 2
            panel_y = (WINDOW_HEIGHT - panel_height) // 2
            
            # Draw panel with gradient
            for i in range(panel_height):
                progress = i / panel_height
                color = (
                    int(20 + 40 * progress),
                    int(20 + 30 * progress),
                    int(60 + 80 * progress),
                    220
                )
                pygame.draw.line(
                    screen, 
                    color, 
                    (panel_x, panel_y + i), 
                    (panel_x + panel_width, panel_y + i)
                )
            
            # Draw panel border
            pygame.draw.rect(screen, GOLD, (panel_x, panel_y, panel_width, panel_height), 3)
            
            # Draw victory text
            font_large = pygame.font.Font(None, 60)
            game_over_text = font_large.render("Congratulations!", True, GOLD)
            screen.blit(game_over_text, game_over_text.get_rect(
                center=(WINDOW_WIDTH//2, panel_y + 50)
            ))
            
            # Draw score
            score_text = font_large.render(f"Score: {self.score}", True, WHITE)
            screen.blit(score_text, score_text.get_rect(
                center=(WINDOW_WIDTH//2, panel_y + 100)
            ))
            
            # Draw stats
            font_medium = pygame.font.Font(None, 36)
            stats_text = font_medium.render(
                f"Completed in {self.moves} moves and {int(self.elapsed_time)} seconds", 
                True, WHITE
            )
            screen.blit(stats_text, stats_text.get_rect(
                center=(WINDOW_WIDTH//2, panel_y + 150)
            ))
            
            # Show high score position
            scores = self.high_scores[self.difficulty]
            position = next((i+1 for i, s in enumerate(scores) if s["score"] == self.score), None)
            
            if position:
                rank_text = font_medium.render(
                    f"New High Score: #{position}!", 
                    True, 
                    GOLD if position <= 3 else WHITE
                )
                screen.blit(rank_text, rank_text.get_rect(
                    center=(WINDOW_WIDTH//2, panel_y + 190)
                ))
            
            # Draw buttons
            restart_button = Button(
                panel_x + 50, 
                panel_y + 240, 
                180, 
                50, 
                "Play Again", 
                color=BLUE
            )
            restart_button.update(pygame.mouse.get_pos())
            restart_button.draw(screen)
            
            menu_button = Button(
                panel_x + 270, 
                panel_y + 240, 
                180, 
                50, 
                "Main Menu", 
                color=PURPLE
            )
            menu_button.update(pygame.mouse.get_pos())
            menu_button.draw(screen)
            
            return {
                "restart_button": restart_button,
                "menu_button": menu_button
            }
        return {}

class MainMenu:
    def __init__(self):
        self.buttons = {
            "easy": Button(WINDOW_WIDTH//2 - 100, 200, 200, 50, "Easy Game", BLUE),
            "medium": Button(WINDOW_WIDTH//2 - 100, 270, 200, 50, "Medium Game", PURPLE),
            "hard": Button(WINDOW_WIDTH//2 - 100, 340, 200, 50, "Hard Game", RED),
            "high_scores": Button(WINDOW_WIDTH//2 - 100, 410, 200, 50, "High Scores", GREEN),
            "quit": Button(WINDOW_WIDTH//2 - 100, 480, 200, 50, "Quit Game", GRAY)
        }
        
    def update(self, mouse_pos):
        for button in self.buttons.values():
            button.update(mouse_pos)
            
    def handle_click(self, mouse_pos):
        for name, button in self.buttons.items():
            if button.is_clicked(mouse_pos):
                sounds["click"].play()
                return name
        return None
        
    def draw(self, screen):
        # Draw background with gradient
        for i in range(WINDOW_HEIGHT):
            color = (
                max(0, min(255, i // 3)),
                0,
                max(0, min(255, 100 - i // 4))
            )
            pygame.draw.line(screen, color, (0, i), (WINDOW_WIDTH, i))
        
        # Draw title
        font_title = pygame.font.Font(None, 80)
        title_text = font_title.render("Memory Card Game", True, GOLD)
        screen.blit(title_text, title_text.get_rect(center=(WINDOW_WIDTH//2, 100)))
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(screen)

class HighScores:
    def __init__(self, high_scores):
        self.high_scores = high_scores
        self.current_tab = "medium"
        self.tabs = {
            "easy": Button(WINDOW_WIDTH//4 - 75, 120, 150, 40, "Easy", BLUE),
            "medium": Button(WINDOW_WIDTH//2 - 75, 120, 150, 40, "Medium", PURPLE),
            "hard": Button(WINDOW_WIDTH*3//4 - 75, 120, 150, 40, "Hard", RED)
        }
        self.back_button = Button(WINDOW_WIDTH//2 - 100, 500, 200, 50, "Back to Menu", GRAY)
        
    def update(self, mouse_pos):
        for tab in self.tabs.values():
            tab.update(mouse_pos)
        self.back_button.update(mouse_pos)
            
    def handle_click(self, mouse_pos):
        for name, tab in self.tabs.items():
            if tab.is_clicked(mouse_pos):
                sounds["click"].play()
                self.current_tab = name
                return None
                
        if self.back_button.is_clicked(mouse_pos):
            sounds["click"].play()
            return "menu"
            
        return None
        
    def draw(self, screen):
        # Draw background with gradient
        for i in range(WINDOW_HEIGHT):
            color = (
                max(0, min(255, i // 3)),
                0,
                max(0, min(255, 100 - i // 4))
            )
            pygame.draw.line(screen, color, (0, i), (WINDOW_WIDTH, i))
        
        # Draw title
        font_title = pygame.font.Font(None, 60)
        title_text = font_title.render("High Scores", True, GOLD)
        screen.blit(title_text, title_text.get_rect(center=(WINDOW_WIDTH//2, 70)))
        
        # Draw tabs
        for name, tab in self.tabs.items():
            if name == self.current_tab:
                # Active tab has different color
                old_color = tab.color
                tab.color = GOLD
                tab.draw(screen)
                tab.color = old_color
            else:
                tab.draw(screen)
        
        # Draw scores table
        scores = self.high_scores.get(self.current_tab, [])
        
        # Draw table header
        font = pygame.font.Font(None, 36)
        headers = ["Rank", "Score", "Moves", "Time", "Date"]
        header_positions = [100, 200, 300, 400, 550]
        
        for header, x in zip(headers, header_positions):
            header_text = font.render(header, True, WHITE)
            screen.blit(header_text, (x, 180))
        
        # Draw horizontal line
        pygame.draw.line(screen, WHITE, (80, 210), (720, 210), 2)
        
        # Draw scores
        font_data = pygame.font.Font(None, 30)
        for i, score in enumerate(scores):
            y = 230 + i * 50
            
            # Rank with medal for top 3
            rank_text = f"{i+1}."
            if i == 0:
                rank_color = GOLD
            elif i == 1:
                rank_color = (192, 192, 192)  # Silver
            elif i == 2:
                rank_color = (205, 127, 50)   # Bronze
            else:
                rank_color = WHITE
                
            rank_surf = font_data.render(rank_text, True, rank_color)
            screen.blit(rank_surf, (100, y))
            
            # Score
            score_surf = font_data.render(str(score["score"]), True, WHITE)
            screen.blit(score_surf, (200, y))
            
            # Moves
            moves_surf = font_data.render(str(score["moves"]), True, WHITE)
            screen.blit(moves_surf, (300, y))
            
            # Time
            time_surf = font_data.render(f"{int(score['time'])}s", True, WHITE)
            screen.blit(time_surf, (400, y))
            
            # Date
            date_surf = font_data.render(score["date"], True, WHITE)
            screen.blit(date_surf, (500, y))
        
        # Draw back button
        self.back_button.draw(screen)

def main():
    # Game states
    MENU = "menu"
    PLAYING = "playing"
    HIGH_SCORES = "high_scores"
    
    state = MENU
    menu = MainMenu()
    game = None
    high_scores_screen = None
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if state == MENU:
                        action = menu.handle_click(mouse_pos)
                        if action == "quit":
                            running = False
                        elif action == "high_scores":
                            # Load high scores and switch to high scores screen
                            high_scores = {}
                            if os.path.exists("high_scores.json"):
                                try:
                                    with open("high_scores.json", "r") as f:
                                        high_scores = json.load(f)
                                except:
                                    high_scores = {"easy": [], "medium": [], "hard": []}
                            else:
                                high_scores = {"easy": [], "medium": [], "hard": []}
                                
                            high_scores_screen = HighScores(high_scores)
                            state = HIGH_SCORES
                        elif action in ["easy", "medium", "hard"]:
                            # Start new game with selected difficulty
                            game = Game(action)
                            state = PLAYING
                    elif state == PLAYING:
                        game.handle_click(*event.pos)
                        
                        # Handle buttons if game is over
                        if game.game_over:
                            buttons = game.draw(screen)
                            if "restart_button" in buttons and buttons["restart_button"].is_clicked(mouse_pos):
                                sounds["click"].play()
                                game = Game(game.difficulty)
                            elif "menu_button" in buttons and buttons["menu_button"].is_clicked(mouse_pos):
                                sounds["click"].play()
                                state = MENU
                    elif state == HIGH_SCORES:
                        action = high_scores_screen.handle_click(mouse_pos)
                        if action == "menu":
                            state = MENU
            elif event.type == pygame.MOUSEMOTION:
                if state == MENU:
                    menu.update(mouse_pos)
                elif state == PLAYING:
                    game.update_hover(*event.pos)
                elif state == HIGH_SCORES:
                    high_scores_screen.update(mouse_pos)
            elif event.type == pygame.USEREVENT:
                if state == PLAYING:
                    game.hide_selected_cards()
                    pygame.time.set_timer(pygame.USEREVENT, 0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == PLAYING:
                        state = MENU
                    elif state == HIGH_SCORES:
                        state = MENU
        
        # Update
        if state == PLAYING:
            game.update()
        
        # Draw
        if state == MENU:
            menu.draw(screen)
        elif state == PLAYING:
            game.draw(screen)
        elif state == HIGH_SCORES:
            high_scores_screen.draw(screen)
            
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
