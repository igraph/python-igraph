"""
.. _tutorials-bridges:

========
Bridges
========

This example shows how to compute and visualize the `bridges <https://en.wikipedia.org/wiki/Bridge_(graph_theory)>`_ in a graph using :meth:`igraph.GraphBase.bridges`. For an example on articulation points instead, see :ref:`tutorials-articulation-points`.

"""
import igraph as ig
import matplotlib.pyplot as plt

# Bridges 1
# Construct graph
g = ig.Graph(14, [(0, 1), (1, 2), (2, 3), (0, 3), (0, 2), (1, 3), (3, 4), 
        (4, 5), (5, 6), (6, 4), (6, 7), (7, 8), (7, 9), (9, 10), (10 ,11), 
        (11 ,7), (7, 10), (8, 9), (8, 10), (5, 12), (12, 13)])

# Find and color bridges
bridges = g.bridges()
g.es["color"] = "gray"
g.es[bridges]["color"] = "red"
g.es["width"] = 0.8
g.es[bridges]["width"] = 1.2

# Plot graph
fig, ax = plt.subplots()
ig.plot(
    g, 
    target=ax, 
    vertex_size=0.3,
    vertex_color="lightblue",
    vertex_label=range(g.vcount())
)
plt.show()


# Bridges 2
# Construct graph
# Construct graph
g = ig.Graph(14, [(0, 1), (1, 2), (2, 3), (0, 3), (0, 2), (1, 3), (3, 4), 
        (4, 5), (5, 6), (6, 4), (6, 7), (7, 8), (7, 9), (9, 10), (10 ,11), 
        (11 ,7), (7, 10), (8, 9), (8, 10), (5, 12), (12, 13)])

# Find and color bridges
bridges = g.bridges()
g.es["color"] = "gray"
g.es[bridges]["color"] = "red"
g.es["width"] = 0.8
g.es[bridges]["width"] = 1.2

g.es["label"] = ""
g.es[bridges]["label"] = "x"

# Plot graph
fig, ax = plt.subplots()
ig.plot(
    g, 
    target=ax, 
    vertex_size=0.3,
    vertex_color="lightblue",
    vertex_label=range(g.vcount()),
    edge_background="#FFF0",    # transparent background color
    edge_align_label=True,      # make sure labels are aligned with the edge
    edge_label=g.es["label"],
    edge_label_color="red"
)
plt.show()

