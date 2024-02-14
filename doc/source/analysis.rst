.. include:: include/global.rst

.. currentmodule:: igraph


Graph analysis
==============

|igraph| enables analysis of graphs/networks from simple operations such as adding and removing nodes to complex theoretical constructs such as community detection. Read the :doc:`api/index` for details on each function and class.

The context for the following examples will be to import |igraph| (commonly as `ig`), have the :class:`Graph` class and to have one or more graphs available::

    >>> import igraph as ig
    >>> from igraph import Graph
    >>> g = Graph(edges=[[0, 1], [2, 3]])

To get a summary representation of the graph, use :meth:`Graph.summary`. For instance::

    >>> g.summary(verbosity=1)

will provide a fairly detailed description.

To copy a graph, use :meth:`Graph.copy`. This is a "shallow" copy: any mutable objects in the attributes are not copied (they would refer to the same instance).
If you want to copy a graph including all its attributes, use Python's `deepcopy` module.

Vertices and edges
++++++++++++++++++

Vertices are numbered 0 to `n-1`, where n is the number of vertices in the graph. These are called the "vertex ids".
To count vertices, use :meth:`Graph.vcount`::

    >>> n = g.vcount()

Edges also have ids from 0 to `m-1` and are counted by :meth:`Graph.ecount`::

    >>> m = g.ecount()

To get a sequence of vertices, use their ids and :attr:`Graph.vs`::

    >>> for v in g.vs:
    >>>     print(v)

Similarly for edges, use :attr:`Graph.es`::

    >>> for e in g.es:
    >>>     print(e)

You can index and slice vertices and edges like indexing and slicing a list::

    >>> g.vs[:4]
    >>> g.vs[0, 2, 4]
    >>> g.es[3]

.. note:: The `vs` and `es` attributes are special sequences with their own useful methods. See the :doc:`api/index` for a full list.

If you prefer a vanilla edge list, you can use :meth:`Graph.get_edge_list`.

Incidence
++++++++++++++++++++++++++++++
To get the vertices at the two ends of an edge, use :attr:`Edge.source` and :attr:`Edge.target`::

    >>> e = g.es[0]
    >>> v1, v2 = e.source, e.target

Vice versa, to get the edge if from the source and target vertices, you can use :meth:`Graph.get_eid` or, for multiple pairs of source/targets,
:meth:`Graph.get_eids`. The boolean version, asking whether two vertices are directly connected, is :meth:`Graph.are_adjacent`.

To get the edges incident on a vertex, you can use :meth:`Vertex.incident`, :meth:`Vertex.out_edges` and
:meth:`Vertex.in_edges`. The three are equivalent on undirected graphs but not directed ones of course::

    >>> v = g.vs[0]
    >>> edges = v.incident()

The :meth:`Graph.incident` function fulfills the same purpose with a slightly different syntax based on vertex IDs::

    >>> edges = g.incident(0)

To get the full adjacency/incidence list representation of the graph, use :meth:`Graph.get_adjlist`, :meth:`Graph.g.get_inclist()` or, for a bipartite graph, :meth:`Graph.get_biadjacency`.

Neighborhood
++++++++++++

To compute the neighbors, successors, and predecessors, the methods :meth:`Graph.neighbors`, :meth:`Graph.successors` and
:meth:`Graph.predecessors` are available. The three give the same answer in undirected graphs and have a similar dual syntax::

    >>> neis = g.vs[0].neighbors()
    >>> neis = g.neighbors(0)

To get the list of vertices within a certain distance from one or more initial vertices, you can use :meth:`Graph.neighborhood`::

    >>> g.neighborhood([0, 1], order=2)

and to find the neighborhood size, there is :meth:`Graph.neighborhood_size`.

Degrees
+++++++
To compute the degree, in-degree, or out-degree of a node, use :meth:`Vertex.degree`, :meth:`Vertex.indegree`, and :meth:`Vertex.outdegree`::

    >>> deg = g.vs[0].degree()
    >>> deg = g.degree(0)

To compute the max degree in a list of vertices, use :meth:`Graph.maxdegree`.

:meth:`Graph.knn` computes the average degree of the neighbors.

Adding and removing vertices and edges
++++++++++++++++++++++++++++++++++++++

To add nodes to a graph, use :meth:`Graph.add_vertex` and :meth:`Graph.add_vertices`::

    >>> g.add_vertex()
    >>> g.add_vertices(5)

This changes the graph `g` in place. You can specify the name of the vertices if you wish.

To remove nodes, use :meth:`Graph.delete_vertices`::

    >>> g.delete_vertices([1, 2])

Again, you can specify the names or the actual :class:`Vertex` objects instead.

To add edges, use :meth:`Graph.add_edge` and :meth:`Graph.add_edges`::

    >>> g.add_edge(0, 2)
    >>> g.add_edges([(0, 2), (1, 3)])

To remove edges, use :meth:`Graph.delete_edges`::

    >>> g.delete_edges([0, 5]) # remove by edge id

You can also remove edges between source and target nodes.

To contract vertices, use :meth:`Graph.contract_vertices`. Edges between contracted vertices will become loops.

Graph operators
+++++++++++++++

It is possible to compute the union, intersection, difference, and other set operations (operators) between graphs.

To compute the union of the graphs (nodes/edges in either are kept)::

    >>> gu = ig.union([g, g2, g3])

Similarly for the intersection (nodes/edges present in all are kept)::

    >>> gu = ig.intersection([g, g2, g3])

These two operations preserve attributes and can be performed with a few variations. The most important one is that vertices can be matched across the graphs by id (number) or by name.

These and other operations are also available as methods of the :class:`Graph` class::

    >>> g.union(g2)
    >>> g.intersection(g2)
    >>> g.disjoint_union(g2)
    >>> g.difference(g2)
    >>> g.complementer()  # complement graph, same nodes but missing edges

and even as numerical operators::

    >>> g |= g2
    >>> g_intersection = g and g2

Topological sorting
+++++++++++++++++++

To sort a graph topologically, use :meth:`Graph.topological_sorting`::

    >>> g = ig.Graph.Tree(10, 2, mode=ig.TREE_OUT)
    >>> g.topological_sorting()

Graph traversal
+++++++++++++++

A common operation is traversing the graph. |igraph| currently exposes breadth-first search (BFS) via :meth:`Graph.bfs` and :meth:`Graph.bfsiter`::

    >>> [vertices, layers, parents] = g.bfs()
    >>> it = g.bfsiter()  # Lazy version

Depth-first search has a similar infrastructure via :meth:`Graph.dfs` and :meth:`Graph.dfsiter`::

    >>> [vertices, parents] = g.dfs()
    >>> it = g.dfsiter()  # Lazy version

To perform a random walk from a certain vertex, use :meth:`Graph.random_walk`::

    >>> vids = g.random_walk(0, 3)

Pathfinding and cuts
++++++++++++++++++++
Several pathfinding algorithms are available:

- :meth:`Graph.shortest_paths` or :meth:`Graph.get_shortest_paths`
- :meth:`Graph.get_all_shortest_paths`
- :meth:`Graph.get_all_simple_paths`
- :meth:`Graph.spanning_tree` finds a minimum spanning tree

As well as functions related to cuts and paths:

- :meth:`Graph.mincut` calculates the minimum cut between the source and target vertices
- :meth:`Graph.st_mincut` - as previous one, but returns a simpler data structure
- :meth:`Graph.mincut_value` - as previous one, but returns only the value
- :meth:`Graph.all_st_cuts`
- :meth:`Graph.all_st_mincuts`
- :meth:`Graph.edge_connectivity` or :meth:`Graph.edge_disjoint_paths` or :meth:`Graph.adhesion`
- :meth:`Graph.vertex_connectivity` or :meth:`Graph.cohesion`

See also the section on flow.

Global properties
+++++++++++++++++

A number of global graph measures are available.

Basic:

- :meth:`Graph.diameter` or :meth:`Graph.get_diameter`
- :meth:`Graph.girth`
- :meth:`Graph.radius`
- :meth:`Graph.average_path_length`

Distributions:

- :meth:`Graph.degree_distribution`
- :meth:`Graph.path_length_hist`

Connectedness:

- :meth:`Graph.all_minimal_st_separators`
- :meth:`Graph.minimum_size_separators`
- :meth:`Graph.cut_vertices` or :meth:`Graph.articulation_points`

Cliques and motifs:

- :meth:`Graph.clique_number` (aka :meth:`Graph.omega`)
- :meth:`Graph.cliques`
- :meth:`Graph.maximal_cliques`
- :meth:`Graph.largest_cliques`
- :meth:`Graph.motifs_randesu` and :meth:`Graph.motifs_randesu_estimate`
- :meth:`Graph.motifs_randesu_no` counts the number of motifs

Directed acyclic graphs:

- :meth:`Graph.is_dag`
- :meth:`Graph.feedback_arc_set`
- :meth:`Graph.topological_sorting`

Optimality:

- :meth:`Graph.farthest_points`
- :meth:`Graph.modularity`
- :meth:`Graph.maximal_cliques`
- :meth:`Graph.largest_cliques`
- :meth:`Graph.independence_number` (aka :meth:`Graph.alpha`)
- :meth:`Graph.maximal_independent_vertex_sets`
- :meth:`Graph.largest_independent_vertex_sets`
- :meth:`Graph.mincut`
- :meth:`Graph.mincut_value`
- :meth:`Graph.feedback_arc_set`
- :meth:`Graph.maximum_bipartite_matching` (bipartite graphs)

Other complex measures are:

- :meth:`Graph.assortativity`
- :meth:`Graph.assortativity_degree`
- :meth:`Graph.assortativity_nominal`
- :meth:`Graph.density`
- :meth:`Graph.transitivity_undirected`
- :meth:`Graph.transitivity_avglocal_undirected`
- :meth:`Graph.dyad_census`
- :meth:`Graph.triad_census`
- :meth:`Graph.reciprocity` (directed graphs)
- :meth:`Graph.isoclass` (only 3 or 4 vertices)
- :meth:`Graph.biconnected_components` aka :meth:`Graph.blocks`

Boolean properties:

- :meth:`Graph.is_bipartite`
- :meth:`Graph.is_connected`
- :meth:`Graph.is_dag`
- :meth:`Graph.is_directed`
- :meth:`Graph.is_named`
- :meth:`Graph.is_simple`
- :meth:`Graph.is_weighted`
- :meth:`Graph.has_multiple`

Vertex properties
+++++++++++++++++++
A spectrum of vertex-level properties can be computed. Similarity measures include:

- :meth:`Graph.similarity_dice`
- :meth:`Graph.similarity_jaccard`
- :meth:`Graph.similarity_inverse_log_weighted`
- :meth:`Graph.diversity`

Structural:

- :meth:`Graph.authority_score`
- :meth:`Graph.hub_score`
- :meth:`Graph.betweenness`
- :meth:`Graph.bibcoupling`
- :meth:`Graph.closeness`
- :meth:`Graph.constraint`
- :meth:`Graph.cocitation`
- :meth:`Graph.coreness` (aka :meth:`Graph.shell_index`)
- :meth:`Graph.eccentricity`
- :meth:`Graph.eigenvector_centrality`
- :meth:`Graph.harmonic_centrality`
- :meth:`Graph.pagerank`
- :meth:`Graph.personalized_pagerank`
- :meth:`Graph.strength`
- :meth:`Graph.transitivity_local_undirected`

Connectedness:

- :meth:`Graph.subcomponent`
- :meth:`Graph.is_separator`
- :meth:`Graph.is_minimal_separator`

Edge properties
+++++++++++++++
As for vertices, edge properties are implemented. Basic properties include:

- :meth:`Graph.is_loop`
- :meth:`Graph.is_multiple`
- :meth:`Graph.is_mutual`
- :meth:`Graph.count_multiple`

and more complex ones:

- :meth:`Graph.edge_betweenness`

Matrix representations
+++++++++++++++++++++++
Matrix-related functionality includes:

- :meth:`Graph.get_adjacency`
- :meth:`Graph.get_adjacency_sparse` (sparse CSR matrix version)
- :meth:`Graph.laplacian`

Clustering
++++++++++
|igraph| includes several approaches to unsupervised graph clustering and community detection:

- :meth:`Graph.components` (aka :meth:`Graph.connected_components`): the connected components
- :meth:`Graph.cohesive_blocks`
- :meth:`Graph.community_edge_betweenness`
- :meth:`Graph.community_fastgreedy`
- :meth:`Graph.community_infomap`
- :meth:`Graph.community_label_propagation`
- :meth:`Graph.community_leading_eigenvector`
- :meth:`Graph.community_leiden`
- :meth:`Graph.community_multilevel` (a version of Louvain)
- :meth:`Graph.community_optimal_modularity` (exact solution, < 100 vertices)
- :meth:`Graph.community_spinglass`
- :meth:`Graph.community_walktrap`

Simplification, permutations and rewiring
+++++++++++++++++++++++++++++++++++++++++
To check is a graph is simple, you can use :meth:`Graph.is_simple`::

    >>> g.is_simple()

To simplify a graph (remove multiedges and loops), use :meth:`Graph.simplify`::

    >>> g_simple = g.simplify()

To return a directed/undirected copy of the graph, use :meth:`Graph.as_directed` and :meth:`Graph.as_undirected`, respectively.

To permute the order of vertices, you can use :meth:`Graph.permute_vertices`::

    >>> g = ig.Tree(6, 2)
    >>> g_perm = g.permute_vertices([1, 0, 2, 3, 4, 5])

The canonical permutation can be obtained via :meth:`Graph.canonical_permutation`, which can then be directly passed to the function above.

To rewire the graph at random, there are:

- :meth:`Graph.rewire` - preserves the degree distribution
- :meth:`Graph.rewire_edges` - fixed rewiring probability for each endpoint

Line graph
++++++++++

To compute the line graph of a graph `g`, which represents the connectedness of the *edges* of g, you can use :meth:`Graph.linegraph`::

    >>> g = Graph(n=4, edges=[[0, 1], [0, 2]])
    >>> gl = g.linegraph()

In this case, the line graph has two vertices, representing the two edges of the original graph, and one edge, representing the point where those two original edges touch.

Composition and subgraphs
+++++++++++++++++++++++++

The function :meth:`Graph.decompose` decomposes the graph into subgraphs. Vice versa, the function :meth:`Graph.compose` returns the composition of two graphs.

To compute the subgraph spannes by some vertices/edges, use :meth:`Graph.subgraph` (aka :meth:`Graph.induced_subgraph`) and :meth:`Graph.subgraph_edges`::

    >>> g_sub = g.subgraph([0, 1])
    >>> g_sub = g.subgraph_edges([0])

To compute the minimum spanning tree, use :meth:`Graph.spanning_tree`.

To compute graph k-cores, the method :meth:`Graph.k_core` is available.

The dominator tree from a given node can be obtained with :meth:`Graph.dominator`.

Bipartite graphs can be decomposed using :meth:`Graph.bipartite_projection`. The size of the projections can be computed using :meth:`Graph.bipartite_projection_size`.

Morphisms
+++++++++

|igraph| enables comparisons between graphs:

- :meth:`Graph.isomorphic`
- :meth:`Graph.isomorphic_vf2`
- :meth:`Graph.subisomorphic_vf2`
- :meth:`Graph.subisomorphic_lad`
- :meth:`Graph.get_isomorphisms_vf2`
- :meth:`Graph.get_subisomorphisms_vf2`
- :meth:`Graph.get_subisomorphisms_lad`
- :meth:`Graph.get_automorphisms_vf2`
- :meth:`Graph.count_isomorphisms_vf2`
- :meth:`Graph.count_subisomorphisms_vf2`
- :meth:`Graph.count_automorphisms_vf2`

Flow
++++

Flow is a characteristic of directed graphs. The following functions are available:

- :meth:`Graph.maxflow` between two nodes
- :meth:`Graph.maxflow_value` - similar to the previous one, but only the value is returned
- :meth:`Graph.gomory_hu_tree`

Flow and cuts are closely related, therefore you might find the following functions useful as well:

- :meth:`Graph.mincut` calculates the minimum cut between the source and target vertices
- :meth:`Graph.st_mincut` - as previous one, but returns a simpler data structure
- :meth:`Graph.mincut_value` - as previous one, but returns only the value
- :meth:`Graph.all_st_cuts`
- :meth:`Graph.all_st_mincuts`
- :meth:`Graph.edge_connectivity` or :meth:`Graph.edge_disjoint_paths` or :meth:`Graph.adhesion`
- :meth:`Graph.vertex_connectivity` or :meth:`Graph.cohesion`
