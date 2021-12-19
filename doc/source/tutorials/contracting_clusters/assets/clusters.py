import igraph as ig
import matplotlib.pyplot as plt
import random

# Generate a random geometric graph with random vertex sizes 
random.seed(0)
g1 = ig.Graph.GRG(50, 0.15)
g1.vs['vertex_size'] = [random.uniform(0.03, 0.08) for i in range(g1.vcount())]

# Cluster graph into weakly connected components
clusters = g1.clusters(mode='weak')
nclusters = len(clusters)

# Visualise different components
fig, axs = plt.subplots(1, 2)
ig.plot(
    clusters,
    target=axs[0],
    palette=ig.RainbowPalette(),
    vertex_size=g1.vs['vertex_size'],
    vertex_color=list(map(int, ig.rescale(clusters.membership, (0, 200), clamp=True))),
    edge_width=0.7
)

# Contract vertices, using mean value for coordinates, and using the max vertex_size as the representation
def mean(list):
    return sum(list) / len(list)

g2 = clusters.cluster_graph(combine_vertices={'x':mean, 'y':mean, 'vertex_size':max})

# Visualise the clustered graph
ig.plot(
    g2,
    target=axs[1],
    palette=ig.RainbowPalette(),
    vertex_size=g2.vs['vertex_size'],
    vertex_color=list(map(int, ig.rescale(range(nclusters), (0, 200), clamp=True))),
)

# Add "a" and "b" labels for panels
fig.text(0.05, 0.9, 'a', va='top')
fig.text(0.55, 0.9, 'b', va='top')

plt.show()

