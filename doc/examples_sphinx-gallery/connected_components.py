"""
.. _tutorials-connected-components:

=====================
Connected Components
=====================

This example demonstrates how to visualise the connected components in a graph using :meth:`igraph.GraphBase.connected_components`.

"""
import igraph as ig
import matplotlib.pyplot as plt
import random

# Generate a random geometric graph with random vertex sizes
random.seed(0)
g = ig.Graph.GRG(50, 0.15)

# Cluster graph into weakly connected components
components = g.connected_components(mode='weak')

# Visualise different components
fig, ax = plt.subplots()
ig.plot(
    components,
    target=ax,
    palette=ig.RainbowPalette(),
    vertex_size=0.7,
    vertex_color=list(map(int, ig.rescale(components.membership, (0, 200), clamp=True))),
    edge_width=0.7
)

plt.show()
