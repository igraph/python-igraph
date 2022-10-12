"""
.. _tutorials-shortest-paths:

==============
Shortest Paths
==============

This example demonstrates how to find the shortest distance between two vertices on a weighted and unweighted graph.

To find the shortest path or distance between two nodes, we can use :meth:`igraph.GraphBase.get_shortest_paths`. If we're only interested in counting the unweighted distance, then we can do the following:


"""
import igraph as ig
import matplotlib.pyplot as plt

import igraph as ig
import matplotlib.pyplot as plt

# Construct the graph
g = ig.Graph(
    6,
    [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5)]
)
g.es["weight"] = [2, 1, 5, 4, 7, 3, 2]

# Get a shortest path along edges
results = g.get_shortest_paths(0, to=5, weights=g.es["weight"], output="epath")  # results = [[1, 3, 5]]

# Plot graph
g.es['width'] = 0.5
g.es[results[0]]['width'] = 2.5

fig, ax = plt.subplots()
ig.plot(
    g,
    target=ax,
    layout='circle',
    vertex_color='steelblue',
    vertex_label=range(g.vcount()),
    edge_width=g.es['width'],
    edge_label=g.es["weight"],
    edge_color='#666',
    edge_align_label=True,
    edge_background='white'
)
