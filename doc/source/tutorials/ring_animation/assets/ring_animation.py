import igraph as ig
import matplotlib.pyplot as plt

# Animate a directed ring graph
g = ig.Graph.Ring(10, directed=True)

# Make 2D ring layout
layout = g.layout_circle()

# Create canvas
fig, ax = plt.subplots()


# Prepare interactive backend for autoupdate
plt.ion()
plt.show()

# Animate, one vertex at a time
for frame in range(11):
    ax.clear()
    # Fix limits (unless you want a zoom-out effect)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    gd = g.subgraph(range(frame))
    ig.plot(gd, target=ax, layout=layout[:frame])
    fig.canvas.draw_idle()
    fig.canvas.start_event_loop(0.5)
