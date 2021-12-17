import igraph as ig
import matplotlib.pyplot as plt
import math
import random

# Get the configuration instance
config = ig.Configuration().instance()

# Set configuration variables
config["general.verbose"] = True
config["plotting.backend"] = "matplotlib"
config["plotting.layout"] = "fruchterman_reingold"
config["plotting.palette"] = "heat"

# Generate a graph
random.seed(1)
g = ig.Graph.Barabasi(n=100, m=1)

# Calculate colors between 0-255 for all nodes
betweenness = g.betweenness()
colors = [math.floor(i * 255 / max(betweenness)) for i in betweenness]

# Plot the graph
ig.plot(g, vertex_color=colors, vertex_size=1, edge_width=0.3)
plt.show()
