import igraph as ig
import matplotlib.pyplot as plt
import random

# Generate a random geometric graph with random vertex sizes 
random.seed(0)
g = ig.Graph.GRG(50, 0.15)

# Cluster graph into weakly connected components
clusters = g.clusters(mode='weak')
nclusters = len(clusters)

# Visualise different components
fig, ax = plt.subplots()
ig.plot(
    clusters,
    target=ax,
    palette=ig.RainbowPalette(),
    vertex_size=0.05,
    vertex_color=list(map(int, ig.rescale(clusters.membership, (0, 200), clamp=True))),
    edge_width=0.7
)

plt.show()
