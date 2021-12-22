import igraph as ig
import matplotlib.pyplot as plt
import random

# Generate a graph
random.seed(1)
g = ig.Graph.Barabasi(n=100, m=1)

# Calculate a color value between 0-200 for all nodes
betweenness = g.betweenness()
colors = [int(i * 200 / max(betweenness)) for i in betweenness]

# Plot the graph
ig.plot(g, vertex_color=colors, vertex_size=1, edge_width=0.3)
plt.show()
