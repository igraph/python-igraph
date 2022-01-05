import igraph as ig
import matplotlib.pyplot as plt
import numpy as np

g = ig.Graph.Lattice([6, 6], circular=False)

# Optional: Rearrange the vertex ids to get a more interesting spanning tree
layout = g.layout("grid")

np.random.seed(0)
permutation = np.random.permutation(36)
g = g.permute_vertices(permutation.tolist())

new_layout = g.layout("grid")
for i in range(36):
    new_layout[permutation[i]] = layout[i]
layout = new_layout

# Generate spanning tree
spanning_tree = g.spanning_tree(weights=None, return_tree=False)

# Plot graph
g.es["color"] = "lightgray"
g.es[spanning_tree]["color"] = "midnightblue"
g.es["width"] = 0.5
g.es[spanning_tree]["width"] = 3.0

fig, ax = plt.subplots()
ig.plot(
    g,
    target=ax,
    layout=layout,
    vertex_color="lightblue",
    edge_width=g.es["width"]
)
plt.show()


