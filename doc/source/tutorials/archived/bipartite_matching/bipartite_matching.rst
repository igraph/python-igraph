==========================
Maximum Bipartite Matching
==========================

This example demonstrates how to visualise bipartite matching using max flow.

.. code-block:: python

    # Generate the graph
    g = ig.Graph(
        9,
        [(0, 4), (0, 5), (1, 4), (1, 6), (1, 7), (2, 5), (2, 7), (2, 8), (3, 6), (3, 7)],
        directed=True
    )

    # Assign nodes 0-3 to one side, and the nodes 4-8 to the other side
    for i in range(4):
        g.vs[i]["type"] = True
    for i in range(4, 9):
        g.vs[i]["type"] = False

    g.add_vertices(2)
    g.add_edges([(9, 0), (9, 1), (9, 2), (9, 3)]) # connect source to one side
    g.add_edges([(4, 10), (5, 10), (6, 10), (7, 10), (8, 10)]) # ... and sinks to the other

    flow = g.maxflow(9, 10) # not setting capacities means that all edges have capacity 1
    print("Size of the Maximum Matching is:", flow.value)

And to display the flow graph nicely, with the matchings added

.. code-block:: python

    # Manually set the position of source and sink to display nicely
    layout = g.layout_bipartite()
    layout[9] = (2, -1)
    layout[10] = (2, 2)

    fig, ax = plt.subplots()
    ig.plot(
        g,
        target=ax,
        layout=layout,
        vertex_size=0.4,
        vertex_label=range(g.vcount()),
        vertex_color=["lightblue" if i < 9 else "orange" for i in range(11)],
        edge_width=[1.0 + flow.flow[i] for i in range(g.ecount())]
    )
    plt.show()

The received output is:

.. code-block::

    Maximal Matching is: 4.0

.. figure:: ./figures/maxflow2.png
   :alt: The visual representation of maximal bipartite matching
   :align: center

   Maximal Bipartite Matching