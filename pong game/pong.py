import tkinter as tk
import random

class PongGame:
    def __init__(self, window):
        self.window = window
        self.window.title("Pong Game")
        
        # Canvas
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
        
        # Ball speed
        self.ball_speed_x = 3
        self.ball_speed_y = 3
        
        # Scores
        self.score1 = 0
        self.score2 = 0
        self.score_display = self.canvas.create_text(
            300, 50, text=f"{self.score1} - {self.score2}",
            fill="white", font=("Arial", 20)
        )
        
        # Key bindings
        self.window.bind("w", lambda e: self.move_paddle(self.paddle1, -20))
        self.window.bind("s", lambda e: self.move_paddle(self.paddle1, 20))
        self.window.bind("<Up>", lambda e: self.move_paddle(self.paddle2, -20))
        self.window.bind("<Down>", lambda e: self.move_paddle(self.paddle2, 20))
        
        # Start game
        self.update()
        
    def move_paddle(self, paddle, dy):
        pos = self.canvas.coords(paddle)
        if (pos[1] + dy >= 0 and pos[3] + dy <= 400):
            self.canvas.move(paddle, 0, dy)
    
    def update(self):
        # Move ball
        self.canvas.move(self.ball, self.ball_speed_x, self.ball_speed_y)
        
        # Get positions
        ball_pos = self.canvas.coords(self.ball)
        paddle1_pos = self.canvas.coords(self.paddle1)
        paddle2_pos = self.canvas.coords(self.paddle2)
        
        # Check for collision with top and bottom
        if ball_pos[1] <= 0 or ball_pos[3] >= 400:
            self.ball_speed_y = -self.ball_speed_y
        
        # Check for collision with paddles
        if (ball_pos[0] <= paddle1_pos[2] and
            ball_pos[1] <= paddle1_pos[3] and
            ball_pos[3] >= paddle1_pos[1]):
            self.ball_speed_x = abs(self.ball_speed_x)
        
        if (ball_pos[2] >= paddle2_pos[0] and
            ball_pos[1] <= paddle2_pos[3] and
            ball_pos[3] >= paddle2_pos[1]):
            self.ball_speed_x = -abs(self.ball_speed_x)
        
        # Check for scoring
        if ball_pos[0] <= 0:
            self.score2 += 1
            self.reset_ball()
        elif ball_pos[2] >= 600:
            self.score1 += 1
            self.reset_ball()
        
        # Update score display
        self.canvas.itemconfig(
            self.score_display,
            text=f"{self.score1} - {self.score2}"
        )
        
        # Schedule next update
        self.window.after(16, self.update)
    
    def reset_ball(self):
        self.canvas.coords(self.ball, 295, 195, 305, 205)
        self.ball_speed_x = random.choice([-3, 3])
        self.ball_speed_y = random.choice([-3, 3])

if __name__ == "__main__":
    root = tk.Tk()
    game = PongGame(root)
    root.mainloop()
