import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class SineAnimator:
    FULL_X = np.linspace(0, 2*np.pi, 400)
    FULL_Y = np.sin(FULL_X)

    def __init__(self):
        plt.style.use("dark_background")
        self.fig, self.ax = plt.subplots(figsize=(8, 4.5))
        self.fig.set_facecolor("#0a0a12")
        self.ax.set_facecolor("#0a0a12")
        
        # Setup axes and labels
        self.ax.set(xlim=(0, 2*np.pi), ylim=(-1.5, 1.5))
        self.ax.set_title("Sine Wave Animation", fontsize=14, color="#e0e0ff", pad=15)
        self.ax.set_xlabel("Angle [rad]", fontsize=10, color="#ccccff")
        self.ax.set_ylabel("sin(θ)", fontsize=10, color="#ccccff")
        
        # Grid configuration
        self.ax.grid(color="#333355", ls="--", lw=0.7, alpha=0.7)
        self.ax.axhline(0, color="#8080ff", lw=1.2, alpha=0.4)
        
        # Create plot elements
        self.bg_line, = self.ax.plot(
            self.FULL_X, self.FULL_Y, 
            color="#444477", lw=1.8, alpha=0.4, zorder=1
        )
        self.live_line, = self.ax.plot(
            [], [], color="#00e5ff", lw=2.8, 
            alpha=0.9, solid_capstyle="round", zorder=3
        )
        self.dot, = self.ax.plot(
            [], [], "o", color="#ff6b6b", 
            markersize=10, alpha=0.9, zorder=4
        )
        self.vline = self.ax.plot(
            [], [], color="#ff6b6b", lw=1.2, 
            alpha=0.7, zorder=2
        )[0]
        
        # Information text
        self.info = self.ax.text(
            0.98, 0.98, "", 
            va="top", ha="right",
            transform=self.ax.transAxes,
            color="#e0e0ff", 
            fontsize=11,
            bbox=dict(facecolor="#1a1a2a", alpha=0.7, edgecolor="#333366", boxstyle="round,pad=0.5")
        )
        
        # Animation control
        self.x_vals, self.y_vals = [], []
        self.paused = False
        self.ani = None
        
        # Keybindings and layout
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)
        self.fig.tight_layout()
        plt.subplots_adjust(top=0.9)

    def start(self):
        self.ani = FuncAnimation(
            self.fig, self._update,
            frames=np.linspace(0, 2*np.pi, 300),
            init_func=self._init, 
            blit=True, 
            interval=20
        )
        plt.show()
        return self

    def _init(self):
        """Initialize animation frame"""
        self.live_line.set_data([], [])
        self.dot.set_data([], [])
        self.vline.set_data([], [])
        self.info.set_text("")
        return self.live_line, self.dot, self.vline, self.info

    def _update(self, frame):
        """Update animation frame"""
        # Update data
        self.x_vals.append(frame)
        self.y_vals.append(np.sin(frame))
        
        # Update plot elements
        self.live_line.set_data(self.x_vals, self.y_vals)
        self.dot.set_data([frame], [np.sin(frame)])
        self.vline.set_data([frame, frame], [0, np.sin(frame)])
        
        # Update info box
        angle_deg = np.degrees(frame)
        self.info.set_text(
            f"θ = {frame:.3f} rad\n"
            f"θ = {angle_deg:.1f}°\n"
            f"sin(θ) = {np.sin(frame):.3f}"
        )
        
        return self.live_line, self.dot, self.vline, self.info

    def _on_key(self, event):
        """Handle keyboard events"""
        k = event.key.lower()
        if k in (" ", "space"):
            self.toggle_pause()
        elif k == "r":
            self.reset_animation()
        elif k in ("q", "escape"):
            plt.close(self.fig)
    
    def toggle_pause(self):
        """Toggle animation pause state"""
        if self.paused:
            self.ani.event_source.start()
        else:
            self.ani.event_source.stop()
        self.paused = not self.paused
    
    def reset_animation(self):
        """Reset animation to initial state"""
        self.x_vals.clear()
        self.y_vals.clear()
        self.ani.frame_seq = self.ani.new_frame_seq()
        if self.paused:
            self.ani.event_source.start()
            self.paused = False

if __name__ == "__main__":
    SineAnimator().start()
