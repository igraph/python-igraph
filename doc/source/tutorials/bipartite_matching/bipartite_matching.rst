==========================
Maximum Bipartite Matching
==========================

This example demonstrates how to find and visualise a maximum biparite matching. First construct a bipartite graph

.. code-block:: python

    import igraph as ig
    import matplotlib.pyplot as plt

    g = ig.Graph(
        9,
        [(0, 5), (1, 6), (1, 7), (2, 5), (2, 8), (3, 6), (4, 5), (4, 6)]
    )

    # Assign nodes 0-4 to one side, and the nodes 5-8 to the other side
    for i in range(5):
        g.vs[i]["type"] = True
    for i in range(5, 9):
        g.vs[i]["type"] = False

Then run the maximum matching,

.. code-block:: python

    matching = g.maximum_bipartite_matching()

    # Print pairings for each node on one side
    matching_size = 0
    print("Matching is:")
    for i in range(5):
        print(f"{i} - {matching.match_of(i)}")
        if matching.match_of(i):
            matching_size += 1
    print("Size of Maximum Matching is:", matching_size)


And finally display the bipartite graph with matchings highlighted.

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

The received output is

.. code-block::

    Matching is:
    0 - 5
    1 - 7
    2 - 8
    3 - None
    4 - 6
    Size of Maximum Matching is: 4

.. figure:: ./figures/bipartite.png
   :alt: The visual representation of maximal bipartite matching
   :align: center

   Maximum Bipartite Matching