.. include:: include/global.rst

.. tutorials-random

=================
Erdős-Rényi Graph
=================

This example demonstrates how to generate `Erdős-Rényi Graphs<https://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93R%C3%A9nyi_model>`_. There are two variants of graphs:

- :meth:`Erdos_Renyi(n, m)` will pick a graph uniformly at random out of all graphs with ``n`` nodes and ``m`` edges.
- :meth:`Erdos_Renyi(n, p)` will generate a graph where each edge between any two pair of nodes has an independent probability ``p`` of existing.

We generate two graphs of each, so we can confirm that our graph generator is truly random.

.. code-block:: python

    import igraph as ig
    import matplotlib.pyplot as plt
    import random

    # Set a random seed for reproducibility
    random.seed(0)

    # Generate two Erdos Renyi graphs based on probability
    g1 = ig.Graph.Erdos_Renyi(n=15, p=0.2, directed=False, loops=False)
    g2 = ig.Graph.Erdos_Renyi(n=15, p=0.2, directed=False, loops=False)

    # Generate two Erdos Renyi graphs based on number of edges
    g3 = ig.Graph.Erdos_Renyi(n=20, m=35, directed=False, loops=False)
    g4 = ig.Graph.Erdos_Renyi(n=20, m=35, directed=False, loops=False)

    # Print out summaries of each graph
    ig.summary(g1)
    ig.summary(g2)
    ig.summary(g3)
    ig.summary(g4)

    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    ig.plot(
        g1,
        target=axs[0],
        layout="circle",
        vertex_color="lightblue"
    )
    axs[0].set_aspect(1)
    ig.plot(
        g2,
        target=axs[1],
        layout="circle",
        vertex_color="lightblue"
    )
    axs[1].set_aspect(1)
    plt.show()

    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    ig.plot(
        g3,
        target=axs[0],
        layout="circle",
        vertex_color="lightblue",
        vertex_size=0.15
    )
    axs[0].set_aspect(1)
    ig.plot(
        g4,
        target=axs[1],
        layout="circle",
        vertex_color="lightblue",
        vertex_size=0.15
    )
    axs[1].set_aspect(1)
    plt.show()

The received output is:

.. code-block::

    IGRAPH U--- 15 18 --
    IGRAPH U--- 15 21 --
    IGRAPH U--- 20 35 --
    IGRAPH U--- 20 35 --

.. figure:: ./figures/erdos_renyi_p.png

   :alt: The visual representation of a randomly generated Erdos Renyi graph
   :align: center

   Erdos Renyi random graphs with probability ``p`` = 0.2

.. figure:: ./figures/erdos_renyi_m.png

   :alt: The second visual representation of a randomly generated Erdos Renyi graph
   :align: center

   Erdos Renyi random graphs with ``m`` = 35 edges


.. note::
    
    Even when using the same random seed, results can still differ depending on the machine the code is being run from.
