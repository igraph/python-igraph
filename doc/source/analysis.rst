Graph analysis
==============
|igraph| enables analysis of graphs/networks from simple operations such as adding and removing nodes to complex theoretical constructs such as community detection.

The context for the following examples will be to import the :class:`Graph` class and to have one or more graphs available:

>>> import igraph as ig
>>> from igraph import Graph
>>> g = Graph(edges=[[0, 1], [2, 3]])

Read the `API documentation`_ for details on each function and class.

Basic operations
++++++++++++++++++
To add nodes to a graph, use :meth:`Graph.add_vertex` and :meth:`Graph.add_vertices`:

>>> g.add_vertex()
>>> g.add_vertices(5)

This changes the graph `g` in place. You can specify the name of the vertices if you wish.

To remove nodes, use :meth:`Graph.delete_vertices`:

>>> g.delete_vertices(None)  # remove all vertices
>>> g.delete_vertices([1, 2])

Again, you can specify the names or the actual :class:`Vertex` objects instead.

To add edges, use :meth:`Graph.add_edge` and :meth:`Graph.add_edges`:

>>> g.add_edge(0, 2)
>>> g.add_edges([(0, 2), (1, 3)])

To remove edges, use :meth:`Graph.delete_edges`:

>>> g.delete_edges(None)   # remove all edges
>>> g.delete_edges([0, 5]) # remove by edge ID

You can also remove edges between source and target nodes.

Graph operators
+++++++++++++++++
It is possible to compute the union, intersection, difference, and other set operations (operators) between graphs.

To compute the union of the graphs (nodes/edges in either are kept):

>>> gu = ig.union([g, g2, g3])

Similarly for the intersection (nodes/edges present in all are kept):

>>> gu = ig.intersection([g, g2, g3])

These two operations preserve attributes and can be performed with a few variations. The most important one is that vertices can be matched across the graphs by id (number) or by name.

These and other operations are also available as methods of the :class:`Graph` class:

>>> g.union(g2)
>>> g.intersection(g2)
>>> g.disjoint_union(g2)
>>> g.difference(g2)
>>> g.complementer()  # complement graph, same nodes but missing edges

and even as numerical operators:

>>> g |= g2
>>> g_intersection = g and g2

Graph traversing
+++++++++++++++++++++
A common operation is traversing the graph. |igraph| currently exposes breath-first search (BFS):

>>> [vertices, layers, parents] = g.bfs()

A depth-first search function is in the works.

.. _API documentation: https://igraph.org/python/doc/igraph-module.html
