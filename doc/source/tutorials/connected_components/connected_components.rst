.. include:: ../../include/global.rst

.. _tutorials-connected-components:

=====================
Connected Components
=====================

.. _clusters: https://igraph.org/python/doc/api/igraph.Graph.html#clusters
.. |clusters| replace:: :meth:`clusters`

This example demonstrates how to visualise the connected components in a graph using |clusters|_.

.. code-block:: python

    import igraph as ig
    import matplotlib.pyplot as plt
    import random

    # Generate a random geometric graph with random vertex sizes 
    random.seed(0)
    g = ig.Graph.GRG(50, 0.15)

    # Cluster graph into weakly connected components
    clusters = g.clusters(mode='weak')
    nclusters = len(clusters)

    # Visualise different components
    fig, ax = plt.subplots()
    ig.plot(
        clusters,
        target=ax,
        palette=ig.RainbowPalette(),
        vertex_size=0.05,
        vertex_color=list(map(int, ig.rescale(clusters.membership, (0, 200), clamp=True))),
        edge_width=0.7
    )

    plt.show()

The plotting results are:

.. figure:: ./figures/connected_components.png
   :alt: A graph showing the various connected components in different colours.
   :align: center

   A graph separated into its weakly connected components.

.. note::

    We use the integers from 0 to 200 instead of 0 to 255 in our vertex colors, since 255 in the `rainbow palette <https://igraph.org/python/doc/api/igraph.drawing.colors.RainbowPalette.html>`_ corresponds to looping back to red.
