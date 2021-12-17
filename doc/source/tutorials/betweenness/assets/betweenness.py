import igraph as ig
import matplotlib.pyplot as plt
import math
import random

# Generate graph
random.seed(1)
g = ig.Graph.Barabasi(n=200, m=2)

# Calculate vertex betweenness and scale it to be between 0.0 and 1.0
vertex_betweenness = g.betweenness()
vertex_betweenness = [math.pow(i, 1/3) for i in vertex_betweenness] # scale values so transition is smoother
min_vertex_betweenness = min(vertex_betweenness)
max_vertex_betweenness = max(vertex_betweenness)
vertex_betweenness = [(i - min_vertex_betweenness) / (max_vertex_betweenness - min_vertex_betweenness) for i in vertex_betweenness]

# Calculate edge betweenness and scale it to be between 0.0 and 1.0
edge_betweenness = g.edge_betweenness()
edge_betweenness = [math.pow(i, 1/2) for i in edge_betweenness] # scale values so transition is smoother
min_edge_betweenness = min(edge_betweenness)
max_edge_betweenness = max(edge_betweenness)
edge_betweenness = [(i - min_edge_betweenness) / (max_edge_betweenness - min_edge_betweenness) for i in edge_betweenness]

# Plot the graph
fig, ax = plt.subplots()
ig.plot(
    g, 
    target=ax, 
    layout="fruchterman_reingold",
    palette=ig.GradientPalette("white", "midnightblue"),
    vertex_color=[int(betweenness * 255) for betweenness in vertex_betweenness], # colors are integers between 0 and 255
    edge_color=[int(betweenness * 255) for betweenness in edge_betweenness],
    vertex_size=[betweenness*0.5+0.1 for betweenness in vertex_betweenness], # vertex_size is between 0.1 and 0.6
    edge_width=[betweenness*0.5+0.5 for betweenness in edge_betweenness], # edge_width is between 0.5 and 1
    vertex_frame_width=0.2,
)
plt.show()

# fig.savefig("../figures/betweenness.png", dpi=200)
