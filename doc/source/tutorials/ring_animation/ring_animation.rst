.. include:: ../../include/global.rst

.. _tutorials-ring-animation:

====================
Ring Graph Animation
====================

This example demonstrates how to use `Matplotlib's animation features <https://matplotlib.org/stable/api/animation_api.html>`_ in order to animate a ring graph sequentially being revealed.

.. code-block:: python

    import igraph as ig
    import matplotlib.pyplot as plt

    # Animate a directed ring graph
    g = ig.Graph.Ring(10, directed=True)

    # Make 2D ring layout
    layout = g.layout_circle()

    # Create canvas
    fig, ax = plt.subplots()
    ax.set_aspect(1)

    # Prepare interactive backend for autoupdate
    plt.ion()
    plt.show()

    # Animate, one vertex at a time
    for frame in range(11):
        # Remove plot elements from the previous frame
        ax.clear()

        # Fix limits (unless you want a zoom-out effect)
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)

        # Plot subgraph
        gd = g.subgraph(range(frame))
        ig.plot(gd, target=ax, layout=layout[:frame], vertex_color="yellow")

        # matplotlib animation infrastructure
        fig.canvas.draw_idle()
        fig.canvas.start_event_loop(0.5)

The received output is:

.. figure:: ./figures/ring_animation.gif
   :alt: The visualisation of a animated ring graph
   :align: center

   Sequentially Animated Ring Graph


.. _induced_subgraph: https://igraph.org/python/api/latest/igraph._igraph.GraphBase.html#induced_subgraph
.. |induced_subgraph| replace:: :meth:`induced_subgraph`

.. note::
    
    We use *igraph*'s :meth:`Graph.subgraph()` (see |induced_subgraph|_) in order to obtain a section of the ring graph at a time for each frame.
