.. include:: include/global.rst

.. _generation:

.. currentmodule:: igraph

Graph generation
================

The first step of most |igraph| applications is to generate a graph. This section will explain a number of ways to do that. Read the :doc:`api/index` for details on each function and class.

The :class:`Graph` class is the main object used to generate graphs::

    >>> from igraph import Graph

To copy a graph, use :meth:`Graph.copy`::

    >>> g_new = g.copy()

From nodes and edges
++++++++++++++++++++

Nodes are always numbered from 0 upwards. To create a generic graph with a specified number of nodes (e.g. 10) and a list of edges between them, you can use the generic constructor:

    >>> g = Graph(n=10, edges=[[0, 1], [2, 3]])

If not specified, the graph is undirected. To make a directed graph::

    >>> g = Graph(n=10, edges=[[0, 1], [2, 3]], directed=True)

To specify edge weights (or any other vertex/edge attributes), use dictionaries::

    >>> g = Graph(
    ...     n=4, edges=[[0, 1], [2, 3]],
    ...     edge_attrs={'weight': [0.1, 0.2]},
    ...     vertex_attrs={'color': ['b', 'g', 'g', 'y']}
    ... )

To create a bipartite graph from a list of types and a list of edges, use :meth:`Graph.Bipartite`.

From Python builtin structures (lists, tuples, dicts)
+++++++++++++++++++++++++++++++++++++++++++++++++++++
|igraph| supports a number of "conversion" methods to import graphs from Python builtin data structures such as dictionaries, lists and tuples:

 - :meth:`Graph.DictList`: from a list of dictionaries
 - :meth:`Graph.TupleList`: from a list of tuples
 - :meth:`Graph.ListDict`: from a dict of lists
 - :meth:`Graph.DictDict`: from a dict of dictionaries

Equivalent methods are available to export a graph, i.e. to convert a graph into
a representation that uses Python builtin data structures:

 - :meth:`Graph.to_dict_list`
 - :meth:`Graph.to_tuple_list`
 - :meth:`Graph.to_list_dict`
 - :meth:`Graph.to_dict_dict`

See the :doc:`api/index` of each function for details and examples.

From matrices
+++++++++++++

To create a graph from an adjacency matrix, use :meth:`Graph.Adjacency` or, for weighted matrices, :meth:`Graph.Weighted_Adjacency`::

    >>> g = Graph.Adjacency([[0, 1, 1], [0, 0, 0], [0, 0, 1]])

This graph is directed and has edges `[0, 1]`, `[0, 2]` and `[2, 2]` (a self-loop).

To create a bipartite graph from a bipartite adjacency matrix, use :meth:`Graph.Biadjacency`::

    >>> g = Graph.Biadjacency([[0, 1, 1], [1, 1, 0]])

From files
++++++++++

To load a graph from a file in any of the supported formats, use :meth:`Graph.Load`. For instance::

    >>> g = Graph.Load('myfile.gml', format='gml')

If you don't specify a format, |igraph| will try to figure it out or, if that fails, it will complain.

From external libraries
+++++++++++++++++++++++

|igraph| can read from and write to `networkx` and `graph-tool` graph formats::

    >>> g = Graph.from_networkx(nwx)

and

::

    >>> g = Graph.from_graph_tool(gt)

From pandas DataFrame(s)
++++++++++++++++++++++++

A common practice is to store edges in a `pandas.DataFrame`, where the two first columns are the source and target vertex ids,
and any additional column indicates edge attributes. You can generate a graph via :meth:`Graph.DataFrame`::

    >>> g = Graph.DataFrame(edges, directed=False)

It is possible to set vertex attributes at the same time via a separate DataFrame. The first column is assumed to contain all
vertex ids (including any vertices without edges) and any additional columns are vertex attributes::

    >>> g = Graph.DataFrame(edges, directed=False, vertices=vertices)

From a formula
++++++++++++++

To create a graph from a string formula, use :meth:`Graph.Formula`, e.g.::

    >>> g = Graph.Formula('D-A:B:F:G, A-C-F-A, B-E-G-B, A-B, F-G, H-F:G, H-I-J')

.. note:: This particular formula also assigns the 'name' attribute to vertices.

Complete graphs
+++++++++++++++

To create a complete graph, use :meth:`Graph.Full`::

    >>> g = Graph.Full(n=3)

where `n` is the number of nodes. You can specify directedness and whether self-loops are included::

    >>> g = Graph.Full(n=3, directed=True, loops=True)

A similar method, :meth:`Graph.Full_Bipartite`, generates a complete bipartite graph. Finally, the metho :meth:`Graph.Full_Citation` created the full citation graph, in which a vertex with index `i` has a directed edge to all vertices with index strictly smaller than `i`.

Tree and star
+++++++++++++

:meth:`Graph.Tree` can be used to generate regular trees, in which almost each vertex has the same number of children::

    >>> g = Graph.Tree(n=7, n_children=2)

creates a tree with seven vertices - of which four are leaves. The root (0) has two children (1 and 2), each of which has two children (the four leaves). Regular trees can be directed or undirected (default).

The method :meth:`Graph.Star` creates a star graph, which is a subtype of a tree.

Lattice
+++++++

:meth:`Graph.Lattice` creates a regular square lattice of the chosen size. For instance::

    >>> g = Graph.Lattice(dim=[3, 3], circular=False)

creates a 3×3 grid in two dimensions (9 vertices total). `circular` is used to connect each edge of the lattice back onto the other side, a process also known as "periodic boundary condition" that is sometimes helpful to smoothen out edge effects.

The one dimensional case (path graph or cycle graph) is important enough to deserve its own constructor :meth:`Graph.Ring`, which can be circular or not::

    >>> g = Graph.Ring(n=4, circular=False)

Graph Atlas
+++++++++++

The book ‘An Atlas of Graphs’ by Roland C. Read and Robin J. Wilson contains all unlabeled undirected graphs with up to seven vertices, numbered from 0 up to 1252. You can create any graph from this list by index with :meth:`Graph.Atlas`, e.g.::

    >>> g = Graph.Atlas(44)

The graphs are listed:

 - in increasing order of number of nodes;
 - for a fixed number of nodes, in increasing order of the number of edges;
 - for fixed numbers of nodes and edges, in increasing order of the degree sequence, for example 111223 < 112222;
 - for fixed degree sequence, in increasing number of automorphisms.

Famous graphs
+++++++++++++

A curated list of famous graphs, which are often used in the literature for benchmarking and other purposes, is available on the `igraph C core manual <https://igraph.org/c/doc/igraph-Generators.html#igraph_famous>`_. You can generate any graph in that list by name, e.g.::

    >>> g = Graph.Famous('Zachary')

will teach you some about martial arts.


Random graphs
+++++++++++++

Stochastic graphs can be created according to several different models or games:

 - Barabási-Albert model: :meth:`Graph.Barabasi`
 - Erdős-Rényi: :meth:`Graph.Erdos_Renyi`
 - Watts-Strogatz :meth:`Graph.Watts_Strogatz`
 - stochastic block model :meth:`Graph.SBM`
 - random tree :meth:`Graph.Tree_Game`
 - forest fire game :meth:`Graph.Forest_Fire`
 - random geometric graph :meth:`Graph.GRG`
 - growing :meth:`Graph.Growing_Random`
 - establishment game :meth:`Graph.Establishment`
 - preference, the non-growing variant of establishment :meth:`Graph.Preference`
 - asymmetric preference :meth:`Graph.Asymmetric_Prefernce`
 - recent degree :meth:`Graph.Recent_Degree`
 - k-regular (each node has degree k) :meth:`Graph.K_Regular`
 - non-growing graph with edge probabilities proportional to node fitnesses :meth:`Graph.Static_Fitness`
 - non-growing graph with prescribed power-law degree distribution(s) :meth:`Graph.Static_Power_Law`
 - random graph with a given degree sequence :meth:`Graph.Degree_Sequence`
 - bipartite :meth:`Graph.Random_Bipartite`

Other graphs
++++++++++++

Finally, there are some ways of generating graphs that are not covered by the previous sections:

 - Kautz graphs :meth:`Graph.Kautz`
 - De Bruijn graphs :meth:`Graph.De_Bruijn`
 - graphs from LCF notation :meth:`Graph.LCF`
 - small graphs of any "isomorphism class" :meth:`Graph.Isoclass`
 - graphs with a specified degree sequence :meth:`Graph.Realize_Degree_Sequence`
