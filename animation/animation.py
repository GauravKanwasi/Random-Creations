import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class SineAnimator:
    FULL_X = np.linspace(0, 2*np.pi, 400)
    FULL_Y = np.sin(FULL_X)

    def __init__(self):
        plt.style.use("dark_background")
        self.fig, self.ax = plt.subplots(figsize=(7, 3.8))
        self.ax.set(xlim=(0, 2*np.pi), ylim=(-1.5, 1.5))
        self.ax.set_facecolor("#111111")
        self.fig.patch.set_facecolor("#111111")
        self.ax.grid(color="#555555", ls=":", lw=0.5)

        self.bg_line, = self.ax.plot(self.FULL_X, self.FULL_Y,
                                     color="#555555", lw=1.2, alpha=0.4)
        self.live_line, = self.ax.plot([], [], color="#00b4ff", lw=2.5)
        self.dot, = self.ax.plot([], [], "o", color="#ff4d4d", markersize=7)
        self.info = self.ax.text(0.02, 0.97, "", va="top", ha="left",
                                 transform=self.ax.transAxes,
                                 color="white", fontsize=9)

        self.x_vals, self.y_vals = [], []
        self.paused = False
        self.ani = None
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)

    def start(self):
        self.ani = FuncAnimation(self.fig, self._update,
                                 frames=np.linspace(0, 2*np.pi, 250),
                                 init_func=self._init, blit=True, interval=25)
        plt.show()
        return self

    def _init(self):
        self.live_line.set_data([], [])
        self.dot.set_data([], [])
        self.info.set_text("")
        return self.live_line, self.dot, self.info

    def _update(self, frame):
        self.x_vals.append(frame)
        self.y_vals.append(np.sin(frame))
        self.live_line.set_data(self.x_vals, self.y_vals)
        self.dot.set_data([frame], [np.sin(frame)])
        self.info.set_text(f"θ = {frame:.2f}")
        return self.live_line, self.dot, self.info

    def _on_key(self, event):
        k = event.key.lower()
        if k in (" ", "space"):
            if self.paused:
                self.ani.event_source.start()
            else:
                self.ani.event_source.stop()
            self.paused = not self.paused
        elif k == "r":
            self.x_vals.clear()
            self.y_vals.clear()
            self.ani.frame_seq = self.ani.new_frame_seq()
            if self.paused:
                self.ani.event_source.start()
                self.paused = False
        elif k in ("q", "escape"):
            plt.close(self.fig)

if __name__ == "__main__":
    SineAnimator().start()
