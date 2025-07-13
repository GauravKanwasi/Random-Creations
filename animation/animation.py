import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Set up figure and axis
fig, ax = plt.subplots()
x, y = [], []
line, = ax.plot([], [], 'b-', lw=2)
ax.set_xlim(0, 2 * np.pi)
ax.set_ylim(-1.5, 1.5)
ax.set_title("Interactive Sine Wave Animation")
ax.grid(True)

# Initialization function
def init():
    line.set_data([], [])
    return line,

# Update function for animation
def update(frame):
    x.append(frame)
    y.append(np.sin(frame))
    line.set_data(x, y)
    return line,

# Create animation
ani = FuncAnimation(
    fig, update, frames=np.linspace(0, 2 * np.pi, 200),
    init_func=init, blit=True, interval=50
)

# Show interactive plot
plt.show()
