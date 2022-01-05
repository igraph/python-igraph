import igraph as ig
import matplotlib.pyplot as plt
import numpy as np

# Generate grid graph with random weights
np.random.seed(0)

g = ig.Graph.Lattice([5, 5], circular=False)
g.es["weight"] = np.random.randint(1, 20, g.ecount()).tolist()

# Generate minimum spanning tree
mst_edges = g.spanning_tree(weights=g.es["weight"], return_tree=False)

# Plot graph
g.es["color"] = "lightgray"
g.es[mst_edges]["color"] = "midnightblue"
g.es["width"] = 1.0
g.es[mst_edges]["width"] = 3.0

fig, ax = plt.subplots()
ig.plot(
    g,
    target=ax,
    layout="grid",
    vertex_color="lightblue",
    edge_width=g.es["width"],
    edge_label=g.es["weight"],
    edge_background="white",
)
plt.show()

# Print out minimum edge weight sum
print("Minimum edge weight sum:", sum(g.es[mst_edges]["weight"]))

# Minimum edge weight sum: 136
