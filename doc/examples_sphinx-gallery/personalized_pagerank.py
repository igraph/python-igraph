"""
.. _tutorials-personalized_pagerank:

===============================
Personalized PageRank on a grid
===============================

This example demonstrates how to calculate and visualize personalized PageRank on a grid. We use the :meth:`igraph.Graph.personalized_pagerank` method, and demonstrate the effects on a grid graph.
"""

# %%
# .. note::
#
#    The PageRank score of a vertex reflects the probability that a random walker will be at that vertex over the long run. At each step the walker has a 1 - damping chance to restart the walk and pick a starting vertex according to the probabilities defined in the reset vector.

import igraph as ig
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np

# %%
# We define a function that plots the graph on a Matplotlib axis, along with
# its personalized PageRank values. The function also generates a
# color bar on the side to see how the values change.
# We use `Matplotlib's Normalize class <https://matplotlib.org/stable/api/_as_gen/matplotlib.colors.Normalize.html>`_
# to set the colors and ensure that our color bar range is correct.


def plot_pagerank(graph: ig.Graph, p_pagerank: list[float]):
    """Plots personalized PageRank values on a grid graph with a colorbar.

    Parameters
    ----------
    graph : ig.Graph
        graph to plot
    p_pagerank : list[float]
        calculated personalized PageRank values
    """
    # Create the axis for matplotlib
    _, ax = plt.subplots(figsize=(8, 8))

    # Create a matplotlib colormap
    # coolwarm goes from blue (lowest value) to red (highest value)
    cmap = cm.coolwarm

    # Normalize the PageRank values for colormap
    normalized_pagerank = ig.rescale(p_pagerank)

    graph.vs["color"] = [cmap(pr) for pr in normalized_pagerank]
    graph.vs["size"] = ig.rescale(p_pagerank, (20, 40))
    graph.es["color"] = "gray"
    graph.es["width"] = 1.5

    # Plot the graph
    ig.plot(graph, target=ax, layout=graph.layout_grid())

    # Add a colorbar
    sm = cm.ScalarMappable(
        norm=plt.Normalize(min(p_pagerank), max(p_pagerank)), cmap=cmap
    )
    plt.colorbar(sm, ax=ax, label="Personalized PageRank")

    plt.title("Graph with Personalized PageRank")
    plt.axis("equal")
    plt.show()


# %%
# First, we generate a graph, e.g. a Lattice Graph, which basically is a ``dim x dim`` grid:
dim = 5
grid_size = (dim, dim)  # dim rows, dim columns
g = ig.Graph.Lattice(dim=grid_size, circular=False)

# %%
# Then we initialize the ``reset_vector`` (it's length should be equal to the number of vertices in the graph):
reset_vector = np.zeros(g.vcount())

# %%
# Then we set the nodes to prioritize, for example nodes with indices ``0`` and ``18``:
reset_vector[0] = 1
reset_vector[18] = 0.65

# %%
# Then we calculate the personalized PageRank:
personalized_page_rank = g.personalized_pagerank(damping=0.85, reset=reset_vector)

# %%
# Finally, we plot the graph with the personalized PageRank values:
plot_pagerank(g, personalized_page_rank)


# %%
# Alternatively, we can play around with the ``damping`` parameter:
personalized_page_rank = g.personalized_pagerank(damping=0.45, reset=reset_vector)

# %%
# Here we can see the same plot with the new damping parameter:
plot_pagerank(g, personalized_page_rank)
