Graph analysis
==============
|igraph| enables analysis of graphs/networks from simple operations such as adding and removing nodes to complex theoretical constructs such as community detection. Read the `API documentation`_ for details on each function and class.

The context for the following examples will be to import the :class:`Graph` class and to have one or more graphs available:

>>> import igraph as ig
>>> from igraph import Graph
>>> g = Graph(edges=[[0, 1], [2, 3]])

To get a summary representation of the graph, use :meth:`Graph.summary`. For instance

>>> g.summary(verbosity=1)

will provide a fairly detailed description.

Vertices and edges
+++++++++++++++++++++++++++
Vertices are numbered 0 to `n-1`, where n is the number of vertices in the graph. These are called the "vertex ids".
To count vertices, use :meth:`Graph.vcount`:

>>> n = g.vcount()

Edges also have ids from 0 to `m-1` and are counted by :meth:`Graph.ecount`:

>>> m = g.ecount()

To get a sequence of vertices, use their ids and :meth:`Graph.vs`:

>>> for v in g.vs:
>>>     print(v)

Similarly for edges:

>>> for e in g.es:
>>>     print(e)

Incidence and neighborhood
++++++++++++++++++++++++++++++
To get the vertices at the two ends of an edge, use :attr:`Edge.source` and :attr:`Edge.target`:

>>> e = g.es[0]
>>> v1, v2 = e.source, e.target

Vice versa, to get the edges incident on a vertex, you can use :meth:`Vertex.incident`, :meth:`Vertex.out_edges` and
:meth:`Vertex.in_edges`. The three are equivalent on undirected graphs but not directed ones, of course:

>>> v = g.vs[0]
>>> edges = v.incident()

The :meth:`Graph.incident` function fulfills the same purpose with a slightly different syntax based on vertex ids:

>>> edges = g.incident(0)

To compute the neighbors, successors, and predecessors, the methods :meth:`Graph.neighbors`, :meth:`Graph.successors` and
:meth:`Graph.predecessors` are available. The three give the same answer in undirected graphs and have a similar dual syntax:

>>> neis = g.vs[0].neighbors()
>>> neis = g.neighbors(0)

To get the list of vertives within a certain distance of one or more initial nodes, you can use :meth:`Graph.neighborhood`:

>>> g.neighborhood([0, 1], order=2)

and to find the neighborhood size, there is :meth:`Graph.neighborhood_size`.

Degrees
+++++++
To compute the degree, in-degree, or out-degree of a node, use :meth:`Vertex.degree`, :meth:`Vertex.indegree`, and :meth:`Vertex.outdegree`:

>>> deg = g.vs[0].degree()
>>> deg = g.degree(0)

To compute the max degree in a list of vertices, use :meth:`Graph.maxdegree`.

:meth:`Graph.knn` computes the average degree of the neighbors.

Flow
++++
Flow is a characteristic of directed graphs. The following functions are available:

- :meth:`Graph.maxflow` between two nodes
- :meth:`Graph.maxflow_value` - similar to the previous one, but only the value is returned

Adding and removing vertices and edges
++++++++++++++++++++++++++++++++++++++

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

Topological sorting
+++++++++++++++++++
To sort a graph topologically, use :meth:`Graph.topological_sorting`:

>>> g = ig.Graph.Tree(10, 2, mode=ig.TREE_OUT)
>>> g.topological_sorting()

Graph traversing
+++++++++++++++++++++
A common operation is traversing the graph. |igraph| currently exposes breath-first search (BFS) via :meth:`Graph.bfs` and :meth:`Graph.bfsiter`:

>>> [vertices, layers, parents] = g.bfs()
>>> it = g.bfsiter()  # Lazy version

A depth-first search function is in the works.

To perform a random walk from a certain vertex, use :meth:`Graph.random_walk`:

>>> vids = g.random_walk(0, 3)

Pathfinding
+++++++++++
Several pathfinding algorithms are available:

- :meth:`Graph.shortest_paths`
- :meth:`Graph.spanning_tree` finds a minimum spanning tree
- :meth:`Graph.mincut` calculates the minimum cut between the source and target vertices
- :meth:`Graph.st_mincut` - as previous one, but returns a simpler data structure
- :meth:`Graph.mincut_value` - as previous one, but returns only the value

Global properties
+++++++++++++++++++++
A number of global graph measures are available:

- :meth:`Graph.diameter`
- :meth:`Graph.radius`
- :meth:`Graph.path_length_hist`

Connectedness:

- :meth:`Graph.minimum_size_separators`

Some properties related to optimality:

- :meth:`Graph.modularity`
- :meth:`Graph.maximal_cliques`
- :meth:`Graph.largest_cliques`
- :meth:`Graph.maximal_independent_vertex_sets`
- :meth:`Graph.largest_independent_vertex_sets`
- :meth:`Graph.mincut`
- :meth:`Graph.mincut_value`
- :meth:`Graph.maximum_bipartite_matching` (bipartite graphs)

Cliques and motifs:

- :meth:`Graph.clique_number` (aka :meth:`Graph.omega`)
- :meth:`Graph.motifs_randesu` and :meth:`Graph.motifs_randesu_estimate`
- :meth:`Graph.g.motifs_randesu_no` counts the number of motifs

Other complex measures are:

- :meth:`Graph.vertex_connectivity`
- :meth:`Graph.transitivity_undirected`
- :meth:`Graph.transitivity_avglocal_undirected`
- :meth:`Graph.transitivity_local_undirected`
- :meth:`Graph.triad_census`
- :meth:`Graph.coreness` (aka :meth:`Graph.shell_index`)
- :meth:`Graph.reciprocity` (directed graphs)


Vertex properties
+++++++++++++++++++
A spectrum of vertex-level properties can be computed. Similarity measures include:

- :meth:`Graph.similarity_dice`
- :meth:`Graph.similarity_jaccard`
- :meth:`Graph.similarity_inverse_log_weighted`

Centrality-related:

- :meth:`Graph.strength`
- :meth:`Graph.pagerank`
- :meth:`Graph.personalized_pagerank`

Connectedness:

- :meth:`Graph.subcomponent`

Matrix representations
+++++++++++++++++++++++
Matrix-related functionality includes:

- :meth:`Graph.get_adjacency`
- :meth:`Graph.get_adjacency_sparse` (sparase CSR matrix version)
- :meth:`Graph.laplacian`



Simplification, subgraphs, etc.
+++++++++++++++++++++++++++++++
To simplify a graph (remove multiedges and loops), use :meth:`Graph.simplify`:

>>> g_simple = g.simplify()

To compute the line graph, there is :meth:`Graph.linegraph`:

>>> gl = g.linegraph()

To compute the subgraph spannes by some vertices/edges, use :meth:`Graph.subgraph` and :meth:`Graph.subgraph_edges`:

>>> g_sub = g.subgraph([0, 1])
>>> g_sub = g.subgraph_edges([0])

To permute the order of vertices, you can use :meth:`Graph.permute_vertices`:

>>> g = ig.Tree(6, 2)
>>> g_perm = g.permute_vertices([1, 0, 2, 3, 4, 5])

To rewire the graph at random while keeping some structural properties, there are:

- :meth:`Graph.rewire`
- :meth:`Graph.rewire_edges`

To compute graph k-cores, the method :meth:`Graph.k_core` is available.

Graph comparisons
++++++++++++++++++
|igraph| enables comparisons between graphs:

- :meth:`Graph.subisomorphic_lad`
- :meth:`Graph.g.subisomorphic_vf2`



.. _API documentation: https://igraph.org/python/doc/igraph-module.html
