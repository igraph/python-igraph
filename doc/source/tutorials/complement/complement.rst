.. include:: ../../include/global.rst

.. _tutorials-complement:

================
Complement
================

.. _complementer: https://igraph.org/python/doc/api/igraph._igraph.GraphBase.html#complementer
.. |complementer| replace:: :meth:`complementer`

This example shows how to generate the `complement graph <https://en.wikipedia.org/wiki/Complement_graph>`_ of a graph (sometimes known as the anti-graph) using |complementer|_. First we generate a random graph

.. code-block:: python

    import igraph as ig
    import matplotlib.pyplot as plt
    import random

    # Create a random graph
    random.seed(0)
    g1 = ig.Graph.Erdos_Renyi(n=10, p=0.5)

We can then generate the complement, and plot out the graph.

.. code-block:: python

    # Generate complement
    g2 = g1.complementer(loops=False)

    # Plot graph
    fig, axs = plt.subplots(1, 2)
    ig.plot(
        g1,
        target=axs[0],
        layout="circle",
        vertex_color="lightblue",
    )
    axs[0].set_title('Original graph')
    ig.plot(
        g2,
        target=axs[1],
        layout="circle",
        vertex_color="lightblue",
    )
    axs[1].set_title('Complement graph')
    plt.show()

The two graphs compared side by side look like this:

.. figure:: ./figures/complement.png
   :alt: Two complement graphs side by side
   :align: center

   The original graph (left) and its complement (right).
