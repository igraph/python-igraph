"""
.. _tutorials-configuration:

======================
Configuration Instance
======================

This example shows how to use |igraph|'s :class:`configuration instance <igraph.Configuration>` to set default |igraph| settings. This is useful for setting global settings so that they don't need to be explicitly stated at the beginning of every |igraph| project you work on.

First we define the default plotting backend, layout, and color palette, and save them. By default, ``ig.config.save()`` will save files to ``~/.igraphrc`` on Linux and Max OS X systems, or in ``%USERPROFILE%\.igraphrc`` for Windows systems.


"""
import igraph as ig
import matplotlib.pyplot as plt
import random

# Set configuration variables
ig.config["plotting.backend"] = "matplotlib"
ig.config["plotting.layout"] = "fruchterman_reingold"
ig.config["plotting.palette"] = "rainbow"

# Save configuration to ~/.igraphrc
ig.config.save()



# Generate a graph
random.seed(1)
g = ig.Graph.Barabasi(n=100, m=1)

# Calculate a color value between 0-200 for all nodes
betweenness = g.betweenness()
colors = [int(i * 200 / max(betweenness)) for i in betweenness]

# Plot the graph
ig.plot(g, vertex_color=colors, vertex_size=1, edge_width=0.3)
plt.show()
