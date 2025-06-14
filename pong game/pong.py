import tkinter as tk
import random
import time

class PongGame:
    def __init__(self, window):
        self.window = window
        self.window.title("Pong Game")
        
        # Canvas setup with a colorful background
        self.canvas = tk.Canvas(window, width=600, height=400, bg="#1e1e1e")
        self.canvas.pack()
        
        # Paddle dimensions
        self.paddle_width = 10
        self.paddle_height = 60
        
        # Create paddles with different colors
        self.paddle1 = self.canvas.create_rectangle(
            50, 200 - self.paddle_height//2,
            50 + self.paddle_width, 200 + self.paddle_height//2,
            fill="#00ff00"  # Green paddle for player 1
        )
        self.paddle2 = self.canvas.create_rectangle(
            550 - self.paddle_width, 200 - self.paddle_height//2,
            550, 200 + self.paddle_height//2,
            fill="#0000ff"  # Blue paddle for player 2
        )
        
        # Create ball with a different color
        self.ball = self.canvas.create_oval(295, 195, 305, 205, fill="#ff0000")  # Red ball
        
        # Ball speed and direction
        self.speed = 3.0
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.ball_speed_x = self.speed * self.direction_x
        self.ball_speed_y = self.speed * self.direction_y
        
        # Scores and game state
        self.score1 = 0
        self.score2 = 0
        self.max_score = 10
        self.game_over = False
        self.score_display = self.canvas.create_text(
            300, 50, text=f"{self.score1} - {self.score2}",
            fill="white", font=("Arial", 24, "bold")
        )
        
        # Paddle movement flags
        self.paddle1_up = False
        self.paddle1_down = False
        self.paddle2_up = False
        self.paddle2_down = False
        
        # Frame rate independent movement
        self.last_time = time.time()
        
        # Key bindings for smooth paddle movement
        self.window.bind("<KeyPress-w>", lambda e: self.set_paddle1_up(True))
        self.window.bind("<KeyRelease-w>", lambda e: self.set_paddle1_up(False))
        self.window.bind("<KeyPress-s>", lambda e: self.set_paddle1_down(True))
        self.window.bind("<KeyRelease-s>", lambda e: self.set_paddle1_down(False))
        self.window.bind("<KeyPress-Up>", lambda e: self.set_paddle2_up(True))
        self.window.bind("<KeyRelease-Up>", lambda e: self.set_paddle2_up(False))
        self.window.bind("<KeyPress-Down>", lambda e: self.set_paddle2_down(True))
        self.window.bind("<KeyRelease-Down>", lambda e: self.set_paddle2_down(False))
        
        # Start screen
        self.start_screen()
    
    def set_paddle1_up(self, state):
        self.paddle1_up = state
    
    def set_paddle1_down(self, state):
        self.paddle1_down = state
    
    def set_paddle2_up(self, state):
        self.paddle2_up = state
    
    def set_paddle2_down(self, state):
        self.paddle2_down = state
    
    def move_paddle(self, paddle, dy, delta_time):
        pos = self.canvas.coords(paddle)
        speed = 300  # pixels per second
        if pos[1] + dy * speed * delta_time >= 0 and pos[3] + dy * speed * delta_time <= 400:
            self.canvas.move(paddle, 0, dy * speed * delta_time)
    
    def start_screen(self):
        self.canvas.create_text(300, 150, text="Pong Game", fill="white", font=("Arial", 40, "bold"))
        self.canvas.create_text(300, 250, text="Press Space to Start", fill="white", font=("Arial", 20))
        self.window.bind("<space>", self.start_game)
    
    def start_game(self, event):
        self.canvas.delete("all")
        self.__init__(self.window)  # Reset the game
        self.update()
    
    def update(self):
        if self.game_over:
            return
        
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        # Move paddles based on key states with frame-rate independent speed
        if self.paddle1_up:
            self.move_paddle(self.paddle1, -1, delta_time)
        if self.paddle1_down:
            self.move_paddle(self.paddle1, 1, delta_time)
        if self.paddle2_up:
            self.move_paddle(self.paddle2, -1, delta_time)
        if self.paddle2_down:
            self.move_paddle(self.paddle2, 1, delta_time)
        
        # Move ball
        self.canvas.move(self.ball, self.ball_speed_x * delta_time * 60, self.ball_speed_y * delta_time * 60)
        
        # Get current positions
        ball_pos = self.canvas.coords(self.ball)
        paddle1_pos = self.canvas.coords(self.paddle1)
        paddle2_pos = self.canvas.coords(self.paddle2)
        
        # Collision with top and bottom walls
        if ball_pos[1] <= 0 or ball_pos[3] >= 400:
            self.direction_y = -self.direction_y
            self.ball_speed_y = self.speed * self.direction_y
            # Add sound effect here (e.g., wall hit)
        
        # Collision with paddles
        if (ball_pos[0] <= paddle1_pos[2] and
            ball_pos[1] <= paddle1_pos[3] and
            ball_pos[3] >= paddle1_pos[1]):
            self.direction_x = 1
            self.speed = min(self.speed * 1.1, 10)  # Cap speed at 10
            self.ball_speed_x = self.speed * self.direction_x
            # Add sound effect here (e.g., paddle hit)
        
        if (ball_pos[2] >= paddle2_pos[0] and
            ball_pos[1] <= paddle2_pos[3] and
            ball_pos[3] >= paddle2_pos[1]):
            self.direction_x = -1
            self.speed = min(self.speed * 1.1, 10)  # Cap speed at 10
            self.ball_speed_x = self.speed * self.direction_x
            # Add sound effect here (e.g., paddle hit)
        
        # Scoring
        if ball_pos[0] <= 0:
            self.score2 += 1
            self.reset_ball(1)  # Ball moves towards player 1
            # Add sound effect here (e.g., score)
        elif ball_pos[2] >= 600:
            self.score1 += 1
            self.reset_ball(-1)  # Ball moves towards player 2
            # Add sound effect here (e.g., score)
        
        # Update score display
        self.canvas.itemconfig(self.score_display, text=f"{self.score1} - {self.score2}")
        
        # Check for game over
        if self.score1 >= self.max_score:
            self.game_over = True
            self.canvas.create_text(300, 200, text="Player 1 wins!", fill="green", font=("Arial", 30, "bold"))
        elif self.score2 >= self.max_score:
            self.game_over = True
            self.canvas.create_text(300, 200, text="Player 2 wins!", fill="blue", font=("Arial", 30, "bold"))
        
        # Continue game loop if not over
        if not self.game_over:
            self.window.after(16, self.update)
    
    def reset_ball(self, direction):
        self.canvas.coords(self.ball, 295, 195, 305, 205)
        self.speed = 3.0
        self.direction_x = direction
        self.direction_y = random.choice([-1, 1])
        self.ball_speed_x = self.speed * self.direction_x
        self.ball_speed_y = self.speed * self.direction_y

if __name__ == "__main__":
    root = tk.Tk()
    game = PongGame(root)
    root.mainloop()
