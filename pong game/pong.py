import tkinter as tk
import random

class PongGame:
    def __init__(self, window):
        self.window = window
        self.window.title("Pong Game")
        
        # Canvas setup
        self.canvas = tk.Canvas(window, width=600, height=400, bg="black")
        self.canvas.pack()
        
        # Paddle dimensions
        self.paddle_width = 10
        self.paddle_height = 60
        
        # Create paddles
        self.paddle1 = self.canvas.create_rectangle(
            50, 200 - self.paddle_height//2,
            50 + self.paddle_width, 200 + self.paddle_height//2,
            fill="white"
        )
        self.paddle2 = self.canvas.create_rectangle(
            550 - self.paddle_width, 200 - self.paddle_height//2,
            550, 200 + self.paddle_height//2,
            fill="white"
        )
        
        # Create ball
        self.ball = self.canvas.create_oval(295, 195, 305, 205, fill="white")
        
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
            fill="white", font=("Arial", 20)
        )
        
        # Paddle movement flags
        self.paddle1_up = False
        self.paddle1_down = False
        self.paddle2_up = False
        self.paddle2_down = False
        
        # Key bindings for smooth paddle movement
        self.window.bind("<KeyPress-w>", lambda e: self.set_paddle1_up(True))
        self.window.bind("<KeyRelease-w>", lambda e: self.set_paddle1_up(False))
        self.window.bind("<KeyPress-s>", lambda e: self.set_paddle1_down(True))
        self.window.bind("<KeyRelease-s>", lambda e: self.set_paddle1_down(False))
        self.window.bind("<KeyPress-Up>", lambda e: self.set_paddle2_up(True))
        self.window.bind("<KeyRelease-Up>", lambda e: self.set_paddle2_up(False))
        self.window.bind("<KeyPress-Down>", lambda e: self.set_paddle2_down(True))
        self.window.bind("<KeyRelease-Down>", lambda e: self.set_paddle2_down(False))
        
        # Start the game loop
        self.update()
    
    def set_paddle1_up(self, state):
        self.paddle1_up = state
    
    def set_paddle1_down(self, state):
        self.paddle1_down = state
    
    def set_paddle2_up(self, state):
        self.paddle2_up = state
    
    def set_paddle2_down(self, state):
        self.paddle2_down = state
    
    def move_paddle(self, paddle, dy):
        pos = self.canvas.coords(paddle)
        if pos[1] + dy >= 0 and pos[3] + dy <= 400:
            self.canvas.move(paddle, 0, dy)
    
    def update(self):
        if self.game_over:
            return
        
        # Move paddles based on key states
        if self.paddle1_up:
            self.move_paddle(self.paddle1, -5)
        if self.paddle1_down:
            self.move_paddle(self.paddle1, 5)
        if self.paddle2_up:
            self.move_paddle(self.paddle2, -5)
        if self.paddle2_down:
            self.move_paddle(self.paddle2, 5)
        
        # Move ball
        self.canvas.move(self.ball, self.ball_speed_x, self.ball_speed_y)
        
        # Get current positions
        ball_pos = self.canvas.coords(self.ball)
        paddle1_pos = self.canvas.coords(self.paddle1)
        paddle2_pos = self.canvas.coords(self.paddle2)
        
        # Collision with top and bottom walls
        if ball_pos[1] <= 0 or ball_pos[3] >= 400:
            self.direction_y = -self.direction_y
            self.ball_speed_y = self.speed * self.direction_y
        
        # Collision with paddles
        if (ball_pos[0] <= paddle1_pos[2] and
            ball_pos[1] <= paddle1_pos[3] and
            ball_pos[3] >= paddle1_pos[1]):
            self.direction_x = 1
            self.speed *= 1.1  # Increase speed by 10%
            self.ball_speed_x = self.speed * self.direction_x
        
        if (ball_pos[2] >= paddle2_pos[0] and
            ball_pos[1] <= paddle2_pos[3] and
            ball_pos[3] >= paddle2_pos[1]):
            self.direction_x = -1
            self.speed *= 1.1  # Increase speed by 10%
            self.ball_speed_x = self.speed * self.direction_x
        
        # Scoring
        if ball_pos[0] <= 0:
            self.score2 += 1
            self.reset_ball(1)  # Ball moves towards player 1
        elif ball_pos[2] >= 600:
            self.score1 += 1
            self.reset_ball(-1)  # Ball moves towards player 2
        
        # Update score display
        self.canvas.itemconfig(self.score_display, text=f"{self.score1} - {self.score2}")
        
        # Check for game over
        if self.score1 >= self.max_score:
            self.game_over = True
            self.canvas.create_text(300, 200, text="Player 1 wins!", fill="red", font=("Arial", 30))
        elif self.score2 >= self.max_score:
            self.game_over = True
            self.canvas.create_text(300, 200, text="Player 2 wins!", fill="red", font=("Arial", 30))
        
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
