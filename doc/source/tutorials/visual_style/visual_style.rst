.. include:: ../../include/global.rst

.. _tutorials-visual-style:

=================================================
Making Multiple Graphs with the Same Visual Style
=================================================

This example shows how to use dictionary unpacking in order to easily use the same visual style across multiple graphs. This is a quick and easy way to quickly share a single visual style across multiple graphs, without having to copy and paste each of the individual attributes over and over again for each graph you plot.

.. code-block:: python

    import igraph as ig
    import matplotlib.pyplot as plt
    import math
    import random

    # Configure visual style for use in both graphs
    visual_style = {
        "edge_width": 0.3,
        "vertex_size": 1,
        "palette": "heat",
        "layout": "fruchterman_reingold"
    }

    # Generate graphs
    random.seed(1)
    g1 = ig.Graph.Barabasi(n=100, m=1)
    g2 = ig.Graph.Barabasi(n=100, m=1)

    # Calculate colors between 0-255 for all nodes
    betweenness1 = g1.betweenness()
    betweenness2 = g2.betweenness()
    colors1 = [int(i * 255 / max(betweenness1)) for i in betweenness1]
    colors2 = [int(i * 255 / max(betweenness2)) for i in betweenness2]

    # Plot the graphs, using the same predefined visual style for both
    fig, axs = plt.subplots(1, 2)
    ig.plot(g1, target=axs[0], vertex_color=colors1, **visual_style)
    ig.plot(g2, target=axs[1], vertex_color=colors2, **visual_style)
    plt.show()

The plots looks like this:

.. figure:: ./figures/visual_style.png
   :alt: Two graphs plotted using the same palette and layout algorithm
   :align: center

   Two graphs using the same palette and layout algorithm.

.. note::
    If you would like to set global defaults, for example, always using the Matplotlib plotting backend, or using a particular color palette by default, you can use |igraph|'s `configuration instance <https://igraph.org/python/doc/api/igraph.configuration.Configuration.html>`_. A quick example on how to use it can be found here: :ref:`tutorials-configuration`
