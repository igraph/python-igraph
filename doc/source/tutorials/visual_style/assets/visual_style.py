import igraph as ig
import matplotlib.pyplot as plt
import math
import random

# Configure visual style
visual_style = {
    "edge_width": 0.3,
    "vertex_size": 1,
    "palette": "heat",
    "layout": "fruchterman_reingold"
}

# Generate graphs
random.seed(1)
g1 = ig.Graph.Barabasi(n=100, m=1)
g2 = ig.Graph.Barabasi(n=100, m=1)

# Calculate colors between 0-255 for all nodes
betweenness1 = g1.betweenness()
betweenness2 = g2.betweenness()
colors1 = [int(i * 255 / max(betweenness1)) for i in betweenness1]
colors2 = [int(i * 255 / max(betweenness2)) for i in betweenness2]

# Plot the graphs
fig, axs = plt.subplots(1, 2)
ig.plot(g1, target=axs[0], vertex_color=colors1, **visual_style)
ig.plot(g2, target=axs[1], vertex_color=colors2, **visual_style)
plt.show()

