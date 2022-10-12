"""
.. _tutorials-complement:

================
Complement
================

This example shows how to generate the `complement graph <https://en.wikipedia.org/wiki/Complement_graph>`_ of a graph (sometimes known as the anti-graph) using :meth:`igraph.GraphBase.complementer`.

First we generate a random graph

"""
import igraph as ig
import matplotlib.pyplot as plt
import random

# Create a random graph
random.seed(0)
g1 = ig.Graph.Erdos_Renyi(n=10, p=0.5)

# Generate complement
g2 = g1.complementer(loops=False)

# Union graph
g_full = g1 | g2

# Complement of union
g_empty = g_full.complementer(loops=False)

# Plot graphs
fig, axs = plt.subplots(2, 2)
ig.plot(
    g1,
    target=axs[0, 0],
    layout="circle",
    vertex_color="black",
)
axs[0, 0].set_title('Original graph')
ig.plot(
    g2,
    target=axs[0, 1],
    layout="circle",
    vertex_color="black",
)
axs[0, 1].set_title('Complement graph')

ig.plot(
    g_full,
    target=axs[1, 0],
    layout="circle",
    vertex_color="black",
)
axs[1, 0].set_title('Union graph')
ig.plot(
    g_empty,
    target=axs[1, 1],
    layout="circle",
    vertex_color="black",
)
axs[1, 1].set_title('Complement of union graph')

plt.show()
