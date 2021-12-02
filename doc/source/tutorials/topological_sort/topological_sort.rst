.. include:: include/global.rst

.. tutorials-topological-sort

================
Topological Sort
================

This example show how to sort by topological order with directed acyclic graph(DAG).

To get topological sorted list, we can use :meth:`topological_sorting`. If given graph is not DAG, error will be returned.

.. code-block:: python

    import igraph as ig
    
    # generate directed acyclic graph
    g = ig.Graph(edges=[(0, 1), (0, 2), (1, 3), (2, 4), (4, 3), (3, 5), (4, 5)], 
                directed=True)
    assert g.is_dag
        
    # topological sorting
    results = g.topological_sorting(mode='out')
    print('Topological sorting result (out):', *results)

    results = g.topological_sorting(mode='in')
    print('Topological sorting result (in):', *results)

There are two modes for :meth:`topological_sorting`. Default mode is 'out', which starts from the node with zero in-degree to sort nodes by topological order. The other mode, 'in', starts from the node with maximum in-degree.


.. code-block:: python

    import igraph as ig

    # generate directed acyclic graph
    g = ig.Graph(edges=[(0, 1), (0, 2), (1, 3), (2, 4), (4, 3), (3, 5), (4, 5)], 
                directed=True)

    # print indegree of each node
    for i in range(g.vcount()):
        print('degree of {}: {}'.format(i, g.vs[i].indegree()))

We can use :meth:`indegree()` to compute indegree of a node.

The output of two sorted list following as:

.. code-block::

    Topological sorting is (out): 0 1 2 4 3 5
    Topological sorting is (in): 5 3 1 4 2 0

.. figure:: ./figures/topological_sort.png
   :alt: The visual representation of a directed acyclic graph for topological sorting
   :align: center

   The graph `g`

- Note that :meth:`topological_sorting` returns topological sorted list and we can set a mode of two.
