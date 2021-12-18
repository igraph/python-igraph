.. include:: ../../include/global.rst

.. _tutorials-betweenness:

=======================
Visualizing Betweenness
=======================

.. _betweenness: https://igraph.org/python/doc/api/igraph._igraph.GraphBase.html#betweenness
.. |betweenness| replace:: :meth:`betweenness`
.. _edge_betweenness: https://igraph.org/python/doc/api/igraph._igraph.GraphBase.html#edge_betweenness
.. |edge_betweenness| replace:: :meth:`edge_betweenness`

This example will demonstrate how to visualize both vertex and edge betweenness with a custom defined color palette. We use the methods |betweenness|_ and |edge_betweenness|_ respectively.

.. code-block:: python

    import igraph as ig
    import matplotlib.pyplot as plt
    import math
    import random

    # Generate graph
    random.seed(1)
    g = ig.Graph.Barabasi(n=200, m=2)

    # Calculate vertex betweenness and scale it to be between 0.0 and 1.0
    vertex_betweenness = ig.rescale(g.betweenness(), clamp=True, 
            scale=lambda x : math.pow(x, 1/3))
    edge_betweenness = ig.rescale(g.edge_betweenness(), clamp=True, 
            scale=lambda x : math.pow(x, 1/2))

    # Plot the graph
    fig, ax = plt.subplots()
    ig.plot(
        g, 
        target=ax, 
        layout="fruchterman_reingold",
        palette=ig.GradientPalette("white", "midnightblue"),
        vertex_color=list(map(int, 
                ig.rescale(vertex_betweenness, (0, 255), clamp=True))), 
        edge_color=list(map(int, 
                ig.rescale(edge_betweenness, (0, 255), clamp=True))),
        vertex_size=ig.rescale(vertex_betweenness, (0.1, 0.6)), 
        edge_width=ig.rescale(edge_betweenness, (0.5, 1.0)), 
        vertex_frame_width=0.2,
    )
    plt.show()


Note that we scale the betweennesses for the vertices and edges by the cube root and square root respectively. The choice of scaling is arbitrary, but is used to give a smoother, more linear transition in the sizes and colors of nodes and edges. The final output graph is here:

.. figure:: ./figures/betweenness.png
   :alt: A graph visualizing the betweenness of each vertex and edge.
   :align: center

   A graph visualizing edge betweenness. White indicates a low betweenness centrality, whereas dark blue indicates a high betweenness centrality.

