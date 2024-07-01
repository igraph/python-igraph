.. include:: include/global.rst

.. _tutorial:

.. currentmodule:: igraph

========
Tutorial
========

This page is a detailed tutorial of |igraph|'s Python capabilities. To get an quick impression of what |igraph| can do, check out the :doc:`tutorials/quickstart`. If you have not installed |igraph| yet, follow the section titled :doc:`install`.

.. note::
   For the impatient reader, see the :doc:`tutorials/index` page for short, self-contained examples.

Starting |igraph|
=================

The most common way to use |igraph| is as a named import within a Python environment (e.g. a bare Python shell, an `IPython`_ shell, a `Jupyter`_ notebook or JupyterLab instance, `Google Colab <https://colab.research.google.com/>`_, or an `IDE <https://www.spyder-ide.org/>`_)::

  $ python
  Python 3.9.6 (default, Jun 29 2021, 05:25:02)
  [Clang 12.0.5 (clang-1205.0.22.9)] on darwin
  Type "help", "copyright", "credits" or "license" for more information.
  >>> import igraph as ig

To call functions, you need to prefix them with ``ig`` (or whatever name you chose)::

  >>> import igraph as ig
  >>> print(ig.__version__)
  0.9.8

.. note::
   It is possible to use *star imports* for |igraph|::

    >>> from igraph import *

   but it is `generally discouraged <https://stackoverflow.com/questions/2386714/why-is-import-bad>`_.

There is a second way to start |igraph|, which is to call the script :command:`igraph` from your terminal::

  $ igraph
  No configuration file, using defaults
  igraph 0.9.6 running inside Python 3.9.6 (default, Jun 29 2021, 05:25:02)
  Type "copyright", "credits" or "license" for more information.
  >>>

.. note::
  Windows users will find the script inside the :file:`scripts` subdirectory of Python
  and might have to add it manually to their path.

This script starts an appropriate shell (`IPython`_ or `IDLE <https://docs.python.org/3/library/idle.html>`_ if found, otherwise a pure Python shell) and uses star imports (see above). This is sometimes convenient to play with |igraph|'s functions.

.. note::
   You can specify which shell should be used by this script via |igraph|'s
   :doc:`configuration` file.

This tutorial will assume you have imported igraph using the namespace ``ig``.

Creating a graph
================

The simplest way to create a graph is the :class:`Graph` constructor. To make an empty graph::

  >>> g = ig.Graph()

To make a graph with 10 nodes (numbered ``0`` to ``9``) and two edges connecting nodes ``0-1`` and ``0-5``::

  >>> g = ig.Graph(n=10, edges=[[0, 1], [0, 5]])

We can print the graph to get a summary of its nodes and edges::

  >>> print(g)
  IGRAPH U--- 10 2 --
  + edges:
  0--1 0--5

This means: **U** ndirected graph with **10** vertices and **2** edges, with the exact edges listed out. If the graph has a `name` attribute, it is printed as well.

.. note::

   |igraph| also has a :func:`igraph.summary()` function, which is similar to ``print()`` but it does not list the edges. This is convenient for large graphs with millions of edges::

     >>> ig.summary(g)
     IGRAPH U--- 10 2 --


Adding/deleting vertices and edges
==================================
Let's start from the empty graph again. To add vertices to an existing graph, use :meth:`Graph.add_vertices`::

  >>> g = ig.Graph()
  >>> g.add_vertices(3)

In |igraph|, vertices are always numbered up from zero. The number of a vertex is called the *vertex ID*. A vertex might or might not have a name.

Similarly, to add edges use :meth:`Graph.add_edges`::

  >>> g.add_edges([(0, 1), (1, 2)])

Edges are added by specifying the source and target vertex for each edge. This call added two edges, one connecting vertices ``0`` and ``1``, and one connecting vertices ``1`` and ``2``. Edges are also numbered up from zero (the *edge ID*) and have an optional name.

.. warning::

   Creating an empty graph and adding vertices and edges as shown here can be much slower
   than creating a graph with its vertices and edges as demonstrated earlier. If speed is
   of concern, you should especially avoid adding vertices and edges *one at a time*. If you
   need to do it anyway, you can use :meth:`Graph.add_vertex` and :meth:`Graph.add_edge`.


If you try to add edges to vertices with invalid IDs (i.e., you try to add an edge to vertex ``5`` when the graph has only three vertices), you get an :exc:`igraph.InternalError` exception::

  >>> g.add_edges([(5, 4)])
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/usr/lib/python3.10/site-packages/igraph/__init__.py", line 376, in add_edges
      res = GraphBase.add_edges(self, es)
  igraph._igraph.InternalError: Error at src/graph/type_indexededgelist.c:270: cannot add edges. -- Invalid vertex id

The message tries to explain what went wrong (``cannot add edges. -- Invalid
vertex id``) along with the corresponding line in the source code where the error
occurred.

.. note::
   The whole traceback, including info on the source code, is useful when
   reporting bugs on our
   `GitHub issue page <https://github.com/igraph/python-igraph/issues>`_. Please include it
   if you create a new issue!


Let us add some more vertices and edges to our graph::

  >>> g.add_edges([(2, 0)])
  >>> g.add_vertices(3)
  >>> g.add_edges([(2, 3), (3, 4), (4, 5), (5, 3)])
  >>> print(g)
  IGRAPH U---- 6 7 --
  + edges:
  0--1 1--2 0--2 2--3 3--4 4--5 3--5

We now have an undirected graph with 6 vertices and 7 edges. Vertex and edge IDs are
always *continuous*, so if you delete a vertex all subsequent vertices will be renumbered.
When a vertex is renumbered, edges are **not** renumbered, but their source and target
vertices will. Use :meth:`Graph.delete_vertices` and :meth:`Graph.delete_edges` to perform
these operations. For instance, to delete the edge connecting vertices ``2-3``, get its
ID and then delete it::

  >>> g.get_eid(2, 3)
  3
  >>> g.delete_edges(3)

Generating graphs
=================

|igraph| includes both deterministic and stochastic graph generators (see :doc:`generation`).
*Deterministic* generators produce the same graph every time you call the fuction, e.g.::

  >>> g = ig.Graph.Tree(127, 2)
  >>> summary(g)
  IGRAPH U--- 127 126 --

uses :meth:`Graph.Tree` to generate a regular tree graph with 127 vertices, each vertex
having two children (and one parent, of course). No matter how many times you call
:meth:`Graph.Tree`, the generated graph will always be the same if you use the same
parameters::

  >>> g2 = ig.Graph.Tree(127, 2)
  >>> g2.get_edgelist() == g.get_edgelist()
  True

The above code snippet also shows you that the :meth:`~Graph.get_edgelist()` method,
which returns a list of source and target vertices for all edges, sorted by edge ID.
If you print the first 10 elements, you get::

  >>> g2.get_edgelist()[:10]
  [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 7), (3, 8), (4, 9), (4, 10)]

*Stochastic* generators produce a different graph each time, e.g. :meth:`Graph.GRG`::

  >>> g = ig.Graph.GRG(100, 0.2)
  >>> summary(g)
  IGRAPH U---- 100 516 --
  + attr: x (v), y (v)

.. note:: ``+ attr`` shows attributes for vertices (v) and edges (e), in this case two
   vertex attributes and no edge attributes.

This generates a geometric random graph: *n* points are chosen randomly and
uniformly inside the unit square and pairs of points closer to each other than a predefined
distance *d* are connected by an edge. If you generate GRGs with the same parameters, they
will be different::

  >>> g2 = ig.Graph.GRG(100, 0.2)
  >>> g.get_edgelist() == g2.get_edgelist()
  False

A slightly looser way to check if the graphs are equivalent is via :meth:`~Graph.isomorphic()`::

  >>> g.isomorphic(g2)
  False

Checking for isomorphism can take a while for large graphs (in this case, the
answer can quickly be given by checking the degree distributions of the two graphs).


Setting and retrieving attributes
=================================
As mentioned above, vertices and edges of a graph in |igraph| have numeric IDs from ``0`` upwards. Deleting vertices or edges can therefore cause reassignments of vertex and/or edge IDs. In addition to IDs, vertices and edges can have *attributes* such as a name, coordinates for plotting, metadata, and weights. The graph itself can have such attributes too (e.g. a name, which will show in ``print`` or :meth:`Graph.summary`). In a sense, every :class:`Graph`, vertex and edge can be used as a Python dictionary to store and retrieve these attributes.

To demonstrate the use of attributes, let us create a simple social network::

  >>> g = ig.Graph([(0,1), (0,2), (2,3), (3,4), (4,2), (2,5), (5,0), (6,3), (5,6)])

Each vertex represents a person, so we want to store names, ages and genders::

  >>> g.vs["name"] = ["Alice", "Bob", "Claire", "Dennis", "Esther", "Frank", "George"]
  >>> g.vs["age"] = [25, 31, 18, 47, 22, 23, 50]
  >>> g.vs["gender"] = ["f", "m", "f", "m", "f", "m", "m"]
  >>> g.es["is_formal"] = [False, False, True, True, True, False, True, False, False]

:attr:`Graph.vs` and :attr:`Graph.es` are the standard way to obtain a sequence of all
vertices and edges, respectively. Just like a Python dictionary, we can set each property
using square brackets. The value must be a list with the same length as the vertices (for
:attr:`Graph.vs`) or edges (for :attr:`Graph.es`). This assigns an attribute to *all* vertices/edges at once.

To assign or modify an attribute for a single vertex/edge, you can use indexing::

  >>> g.es[0]["is_formal"] = True

In fact, a single vertex is represented via the class :class:`Vertex`, and a single edge via :class:`Edge`. Both of them plus :class:`Graph` can all be keyed like a dictionary to set attributes, e.g. to add a date to the graph::

  >>> g["date"] = "2009-01-10"
  >>> print(g["date"])
  2009-01-10

To retrieve a dictionary of attributes, you can use :meth:`Graph.attributes`, :meth:`Vertex.attributes`, and :meth:`Edge.attributes`.

Furthermore, each :class:`Vertex` has a special property, :attr:`Vertex.index`, that is used to find out the ID of a vertex. Each :class:`Edge` has :attr:`Edge.index` plus two additional properties, :attr:`Edge.source` and :attr:`Edge.target`, that are used to find the IDs of the vertices connected by this edge. To get both at once as a tuple, you can use :attr:`Edge.tuple`.

To assign attributes to a subset of vertices or edges, you can use slicing::

  >>> g.es[:1]["is_formal"] = True

The output of ``g.es[:1]`` is an instance of :class:`~seq.EdgeSeq`, whereas :class:`~seq.VertexSeq` is the equivalent class representing subsets of vertices.

To delete attributes, use the Python keyword ``del``, e.g.::

  >>> g.vs[3]["foo"] = "bar"
  >>> g.vs["foo"]
  [None, None, None, 'bar', None, None, None]
  >>> del g.vs["foo"]
  >>> g.vs["foo"]
  Traceback (most recent call last):
    File "<stdin>", line 25, in <module>
  KeyError: 'Attribute does not exist'


.. warning::
   Attributes can be arbitrary Python objects, but if you are saving graphs to a
   file, only string and numeric attributes will be kept. See the :mod:`pickle` module in
   the standard Python library if you are looking for a way to save other attribute types.
   You can either pickle your attributes individually, store them as strings and save them,
   or you can pickle the whole :class:`Graph` if you know that you want to load the graph
   back into Python only.



Structural properties of graphs
===============================

Besides the simple graph and attribute manipulation routines described above,
|igraph| provides a large set of methods to calculate various structural properties
of graphs. It is beyond the scope of this tutorial to document all of them, hence
this section will only introduce a few of them for illustrative purposes.
We will work on the small social network we built in the previous section.

Probably the simplest property one can think of is the :dfn:`vertex degree`. The
degree of a vertex equals the number of edges adjacent to it. In case of directed
networks, we can also define :dfn:`in-degree` (the number of edges pointing towards
the vertex) and :dfn:`out-degree` (the number of edges originating from the vertex).
|igraph| is able to calculate all of them using a simple syntax::

  >>> g.degree()
  [3, 1, 4, 3, 2, 3, 2]

If the graph was directed, we would have been able to calculate the in- and out-degrees
separately using ``g.degree(mode="in")`` and ``g.degree(mode="out")``. You can
also pass a single vertex ID or a list of vertex IDs to :meth:`~Graph.degree` if you
want to calculate the degrees for only a subset of vertices::

  >>> g.degree(6)
  2
  >>> g.degree([2,3,4])
  [4, 3, 2]

This calling convention applies to most of the structural properties |igraph| can
calculate. For vertex properties, the methods accept a vertex ID or a list of vertex IDs
(and if they are omitted, the default is the set of all vertices). For edge properties,
the methods accept a single edge ID or a list of edge IDs. Instead of a list of IDs,
you can also supply a :class:`VertexSeq` or an :class:`EdgeSeq` instance appropriately.
Later in the :ref:`next chapter <querying_vertices_and_edges>`, you will learn how to
restrict them to exactly the vertices or edges you want.

.. note::

  For some measures, it does not make sense to calculate them only for a few vertices
  or edges instead of the whole graph, as it would take the same time anyway. In this
  case, the methods won't accept vertex or edge IDs, but you can still restrict the
  resulting list later using standard list indexing and slicing operators. One such
  example is eigenvector centrality (:meth:`Graph.evcent()`).

Besides degree, |igraph| includes built-in routines to calculate many other centrality
properties, including vertex and edge betweenness
(:meth:`Graph.betweenness <GraphBase.betweenness>`,
:meth:`Graph.edge_betweenness <GraphBase.edge_betweenness>`) or Google's PageRank
(:meth:`Graph.pagerank`) just to name a few. Here we just illustrate edge betweenness::

  >>> g.edge_betweenness()
  [6.0, 6.0, 4.0, 2.0, 4.0, 3.0, 4.0, 3.0. 4.0]

Now we can also figure out which connections have the highest betweenness centrality
with some Python magic::

  >>> ebs = g.edge_betweenness()
  >>> max_eb = max(ebs)
  >>> [g.es[idx].tuple for idx, eb in enumerate(ebs) if eb == max_eb]
  [(0, 1), (0, 2)]

Most structural properties can also be retrieved for a subset of vertices or edges
or for a single vertex or edge by calling the appropriate method on the
:class:`VertexSeq`, :class:`EdgeSeq`, :class:`Vertex` or :class:`Edge` object of
interest::

  >>> g.vs.degree()
  [3, 1, 4, 3, 2, 3, 2]
  >>> g.es.edge_betweenness()
  [6.0, 6.0, 4.0, 2.0, 4.0, 3.0, 4.0, 3.0. 4.0]
  >>> g.vs[2].degree()
  4

.. _querying_vertices_and_edges:

Querying vertices and edges based on attributes
===============================================

Selecting vertices and edges
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Imagine that in a given social network, you would like to find out who has the largest
degree or betweenness centrality. You can do that with the tools presented so far and
some basic Python knowledge, but since it is a common task to select vertices and edges
based on attributes or structural properties, |igraph| gives you an easier way to do that::

  >>> g.vs.select(_degree=g.maxdegree())["name"]
  ['Claire']

The syntax may seem a little bit awkward for the first sight, so let's try to interpret
it step by step. :meth:`~VertexSeq.select` is a method of :class:`VertexSeq` and its
sole purpose is to filter a :class:`VertexSeq` based on the properties of individual
vertices. The way it filters the vertices depends on its positional and keyword
arguments. Positional arguments (the ones without an explicit name like
``_degree`` above) are always processed before keyword arguments as follows:

- If the first positional argument is ``None``, an empty sequence (containing no
  vertices) is returned::

    >>> seq = g.vs.select(None)
    >>> len(seq)
    0

- If the first positional argument is a callable object (i.e., a function, a bound
  method or anything that behaves like a function), the object will be called for
  every vertex that's currently in the sequence. If the function returns ``True``,
  the vertex will be included, otherwise it will be excluded::

    >>> graph = ig.Graph.Full(10)
    >>> only_odd_vertices = graph.vs.select(lambda vertex: vertex.index % 2 == 1)
    >>> len(only_odd_vertices)
    5

- If the first positional argument is an iterable (i.e., a list, a generator or
  anything that can be iterated over), it *must* return integers and these integers
  will be considered as indices into the current vertex set (which is *not* necessarily
  the whole graph). Only those vertices that match the given indices will be included
  in the filtered vertex set. Floats, strings, invalid vertex IDs will silently be
  ignored::

    >>> seq = graph.vs.select([2, 3, 7])
    >>> len(seq)
    3
    >>> [v.index for v in seq]
    [2, 3, 7]
    >>> seq = seq.select([0, 2])         # filtering an existing vertex set
    >>> [v.index for v in seq]
    [2, 7]
    >>> seq = graph.vs.select([2, 3, 7, "foo", 3.5])
    >>> len(seq)
    3

- If the first positional argument is an integer, all remaining arguments are also
  expected to be integers and they are interpreted as indices into the current vertex
  set. This is just syntactic sugar, you could achieve an equivalent effect by
  passing a list as the first positional argument, but this way you can omit the
  square brackets::

    >>> seq = graph.vs.select(2, 3, 7)
    >>> len(seq)
    3

Keyword arguments can be used to filter the vertices based on their attributes
or their structural properties. The name of each keyword argument should consist
of at most two parts: the name of the attribute or structural property and the
filtering operator. The operator can be omitted; in that case, we automatically
assume the equality operator. The possibilities are as follows (where
*name* denotes the name of the attribute or property):

================ ================================================================
Keyword argument Meaning
================ ================================================================
``name_eq``      The attribute/property value must be *equal to* the value of the
                 keyword argument
---------------- ----------------------------------------------------------------
``name_ne``      The attribute/property value must *not be equal to* the value of
                 the keyword argument
---------------- ----------------------------------------------------------------
``name_lt``      The attribute/property value must be *less than* the value of
                 the keyword argument
---------------- ----------------------------------------------------------------
``name_le``      The attribute/property value must be *less than or equal to* the
                 value of the keyword argument
---------------- ----------------------------------------------------------------
``name_gt``      The attribute/property value must be *greater than* the value of
                 the keyword argument
---------------- ----------------------------------------------------------------
``name_ge``      The attribute/property value must be *greater than or equal to*
                 the value of the keyword argument
---------------- ----------------------------------------------------------------
``name_in``      The attribute/property value must be *included in* the value of
                 the keyword argument, which must be a sequence in this case
---------------- ----------------------------------------------------------------
``name_notin``   The attribute/property value must *not be included in* the value
                 of the the keyword argument, which must be a sequence in this
                 case
================ ================================================================

For instance, the following command gives you people younger than 30 years in
our imaginary social network::

  >>> g.vs.select(age_lt=30)

.. note::
   Due to the syntactical constraints of Python, you cannot use the admittedly
   simpler syntax of ``g.vs.select(age < 30)`` as only the equality operator is
   allowed to appear in an argument list in Python.

To save you some typing, you can even omit the :meth:`~VertexSeq.select` method if
you wish::

  >>> g.vs(age_lt=30)

Theoretically, it can happen that there exists an attribute and a structural property
with the same name (e.g., you could have a vertex attribute named ``degree``). In that
case, we would not be able to decide whether the user meant ``degree`` as a structural
property or as a vertex attribute. To resolve this ambiguity, structural property names
*must* always be preceded by an underscore (``_``) when used for filtering. For example, to
find vertices with degree larger than 2::

  >>> g.vs(_degree_gt=2)

There are also a few special structural properties for selecting edges:

- Using ``_source`` or ``_from`` in the keyword argument list of :meth:`EdgeSeq.select`
  filters based on the source vertices of the edges. E.g., to select all the edges
  originating from Claire (who has vertex index 2)::

    >>> g.es.select(_source=2)

- Using ``_target`` or ``_to`` filters based on the target vertices. This is different
  from ``_source`` and ``_from`` if the graph is directed.

- ``_within`` takes a :class:`VertexSeq` object or a list or set of vertex indices
  and selects all the edges that originate and terminate in the given vertex
  set. For instance, the following expression selects all the edges between
  Claire (vertex index 2), Dennis (vertex index 3) and Esther (vertex index 4)::

    >>> g.es.select(_within=[2,3,4])

  We could also have used a :class:`VertexSeq` object::

    >>> g.es.select(_within=g.vs[2:5])

- ``_between`` takes a tuple consisting of two :class:`VertexSeq` objects or lists
  containing vertex indices or :class:`Vertex` objects and selects all the edges that
  originate in one of the sets and terminate in the other. E.g., to select all the
  edges that connect men to women::

    >>> men = g.vs.select(gender="m")
    >>> women = g.vs.select(gender="f")
    >>> g.es.select(_between=(men, women))

Finding a single vertex or edge with some properties
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In many cases we are looking for a single vertex or edge of a graph with some properties,
and either we do not care which one of the matches is returned if there are multiple
matches, or we know in advance that there will be only one match. A typical example is
looking up vertices by their names in the ``name`` property. :class:`VertexSeq` and
:class:`EdgeSeq` objects provide the :meth:`~VertexSeq.find` method for such use-cases.
:meth:`~VertexSeq.find` works similarly to :meth:`~VertexSeq.select`, but it returns
only the first match if there are multiple matches, and throws an exception if no
match is found. For instance, to look up the vertex corresponding to Claire, one can
do this::

  >>> claire = g.vs.find(name="Claire")
  >>> type(claire)
  igraph.Vertex
  >>> claire.index
  2

Looking up an unknown name will yield an exception::

  >>> g.vs.find(name="Joe")
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
  ValueError: no such vertex

Looking up vertices by names
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Looking up vertices by names is a very common operation, and it is usually much easier
to remember the names of the vertices in a graph than their IDs. To this end, |igraph|
treats the ``name`` attribute of vertices specially; they are indexed such that vertices
can be looked up by their names in amortized constant time. To make things even easier,
|igraph| accepts vertex names (almost) anywhere where it expects vertex IDs, and also
accepts collections (list, tuples etc) of vertex names anywhere where it expects lists
of vertex IDs or :class:`VertexSeq` instances. E.g, you can simply look up the degree
(number of connections) of Dennis as follows::

  >>> g.degree("Dennis")
  3

or, alternatively::

  >>> g.vs.find("Dennis").degree()
  3

The mapping between vertex names and IDs is maintained transparently by |igraph| in
the background; whenever the graph changes, |igraph| also updates the internal mapping.
However, uniqueness of vertex names is *not* enforced; you can easily create a graph
where two vertices have the same name, but |igraph| will return only one of them when
you look them up by names, the other one will be available only by its index.

Treating a graph as an adjacency matrix
=======================================

Adjacency matrix is another way to form a graph. In adjacency matrix, rows and columns are labeled by graph vertices: the elements of the matrix indicate whether the vertices *i* and *j* have a common edge (*i, j*).
The adjacency matrix for the example graph is

::

  >>> g.get_adjacency()
  Matrix([
    [0, 1, 1, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 1, 1, 1, 0],
    [0, 0, 1, 0, 1, 0, 1],
    [0, 0, 1, 1, 0, 0, 0],
    [1, 0, 1, 0, 0, 0, 1],
    [0, 0, 0, 1, 0, 1, 0]
  ])

For example, Claire (``[1, 0, 0, 1, 1, 1, 0]``) is directly connected to Alice (who has vertex index 0), Dennis (index 3),
Esther (index 4), and Frank (index 5), but not to Bob (index 1) nor George (index 6).

.. _tutorial-layouts-plotting:

Layouts and plotting
====================

A graph is an abstract mathematical object without a specific representation in 2D or
3D space. This means that whenever we want to visualise a graph, we have to find a
mapping from vertices to coordinates in two- or three-dimensional space first,
preferably in a way that is pleasing for the eye. A separate branch of graph theory,
namely graph drawing, tries to solve this problem via several graph layout algorithms.
|igraph| implements quite a few layout algorithms and is also able to draw them onto
the screen or to a PDF, PNG or SVG file using the `Cairo library <https://www.cairographics.org>`_.

.. important::
   To follow the examples of this subsection, you need the Python bindings of the
   Cairo library or matplotlib (depending on what backend is selected). The previous
   chapter (:ref:`installing-igraph`) tells you more about how to install Cairo's Python
   bindings.

Layout algorithms
^^^^^^^^^^^^^^^^^

The layout methods in |igraph| are to be found in the :class:`Graph` object, and they
always start with ``layout_``. The following table summarises them:

==================================== =============== =============================================
Method name                          Short name      Algorithm description
==================================== =============== =============================================
``layout_circle``                    ``circle``,     Deterministic layout that places the
                                     ``circular``    vertices on a circle
------------------------------------ --------------- ---------------------------------------------
``layout_davidson_harel``            ``dh``          Davidson-Harel simulated annealing algorithm
------------------------------------ --------------- ---------------------------------------------
``layout_drl``                       ``drl``         The `Distributed Recursive Layout`_ algorithm
                                                     for large graphs
------------------------------------ --------------- ---------------------------------------------
``layout_fruchterman_reingold``      ``fr``          Fruchterman-Reingold force-directed algorithm
------------------------------------ --------------- ---------------------------------------------
``layout_fruchterman_reingold_3d``   ``fr3d``,       Fruchterman-Reingold force-directed algorithm
                                     ``fr_3d``       in three dimensions
------------------------------------ --------------- ---------------------------------------------
``layout_graphopt``                  ``graphopt``    The GraphOpt algorithm for large graphs
------------------------------------ --------------- ---------------------------------------------
``layout_grid``                      ``grid``        Regular grid layout
------------------------------------ --------------- ---------------------------------------------
``layout_kamada_kawai``              ``kk``          Kamada-Kawai force-directed algorithm
------------------------------------ --------------- ---------------------------------------------
``layout_kamada_kawai_3d``           ``kk3d``,       Kamada-Kawai force-directed algorithm
                                     ``kk_3d``       in three dimensions
------------------------------------ --------------- ---------------------------------------------
``layout_lgl``                       ``large``,      The `Large Graph Layout`_ algorithm for
                                     ``lgl``,        large graphs
                                     ``large_graph``
------------------------------------ --------------- ---------------------------------------------
``layout_mds``                       ``mds``         Multidimensional scaling layout
------------------------------------ --------------- ---------------------------------------------
``layout_random``                    ``random``      Places the vertices completely randomly
------------------------------------ --------------- ---------------------------------------------
``layout_random_3d``                 ``random_3d``   Places the vertices completely randomly in 3D
------------------------------------ --------------- ---------------------------------------------
``layout_reingold_tilford``          ``rt``,         Reingold-Tilford tree layout, useful for
                                     ``tree``        (almost) tree-like graphs
------------------------------------ --------------- ---------------------------------------------
``layout_reingold_tilford_circular`` ``rt_circular`` Reingold-Tilford tree layout with a polar
                                                     coordinate post-transformation, useful for
                                                     (almost) tree-like graphs
------------------------------------ --------------- ---------------------------------------------
``layout_sphere``                    ``sphere``,     Deterministic layout that places the vertices
                                     ``spherical``,  evenly on the surface of a sphere
                                     ``circular_3d``
==================================== =============== =============================================

.. _Distributed Recursive Layout: https://www.osti.gov/doecode/biblio/54626
.. _Large Graph Layout: https://sourceforge.net/projects/lgl/

Layout algorithms can either be called directly or using the common layout method called
:meth:`~Graph.layout`::

  >>> layout = g.layout_kamada_kawai()
  >>> layout = g.layout("kamada_kawai")

The first argument of the :meth:`~Graph.layout` method must be the short name of the
layout algorithm (see the table above). All the remaining positional and keyword arguments
are passed intact to the chosen layout method. For instance, the following two calls are
completely equivalent::

  >>> layout = g.layout_reingold_tilford(root=[2])
  >>> layout = g.layout("rt", root=[2])

Layout methods return a :class:`~layout.Layout` object, which behaves mostly like a list of lists.
Each list entry in a :class:`~layout.Layout` object corresponds to a vertex in the original graph
and contains the vertex coordinates in the 2D or 3D space. :class:`~layout.Layout` objects also
contain some useful methods to translate, scale or rotate the coordinates in a batch.
However, the primary utility of :class:`~layout.Layout` objects is that you can pass them to the
:func:`~drawing.plot` function along with the graph to obtain a 2D drawing.

Drawing a graph using a layout
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For instance, we can plot our imaginary social network with the Kamada-Kawai
layout algorithm as follows::

  >>> layout = g.layout("kk")
  >>> ig.plot(g, layout=layout)

This should open an external image viewer showing a visual representation of the network,
something like the one on the following figure (although the exact placement of
nodes may be different on your machine since the layout is not deterministic):

.. figure:: figures/tutorial_social_network_1.png
   :alt: The visual representation of our social network (Cairo backend)
   :align: center

   Our social network with the Kamada-Kawai layout algorithm

If you prefer to use `matplotlib`_ as a plotting engine, create an axes and use the
``target`` argument::

  >>> import matplotlib.pyplot as plt
  >>> fig, ax = plt.subplots()
  >>> ig.plot(g, layout=layout, target=ax)

.. figure:: figures/tutorial_social_network_1_mpl.png
   :alt: The visual representation of our social network (matplotlib backend)
   :align: center

.. note::
   When plotting rooted trees, Cairo automatically puts the root on top of the image and
   the leaves at the bottom. For `matplotlib`_, the root is usually at the bottom instead.
   You can easily place the root on top by calling `ax.invert_yaxis()`.

Hmm, this is not too pretty so far. A trivial addition would be to use the names as the
vertex labels and to color the vertices according to the gender. Vertex labels are taken
from the ``label`` attribute by default and vertex colors are determined by the
``color`` attribute, so we can simply create these attributes and re-plot the graph::

  >>> g.vs["label"] = g.vs["name"]
  >>> color_dict = {"m": "blue", "f": "pink"}
  >>> g.vs["color"] = [color_dict[gender] for gender in g.vs["gender"]]
  >>> ig.plot(g, layout=layout, bbox=(300, 300), margin=20)  # Cairo backend
  >>> ig.plot(g, layout=layout, target=ax)  # matplotlib backend

Note that we are simply re-using the previous layout object here, but for the Cairo backend
we also specified that we need a smaller plot (300 x 300 pixels) and a larger margin around
the graph to fit the labels (20 pixels). These settings would be ignored for the Matplotlib
backend. The result is:

.. figure:: figures/tutorial_social_network_2.png
   :alt: The visual representation of our social network - with names and genders
   :align: center

   Our social network - with names as labels and genders as colors

and for matplotlib:

.. figure:: figures/tutorial_social_network_2_mpl.png
   :alt: The visual representation of our social network - with names and genders
   :align: center

   Our social network - with names as labels and genders as colors

Instead of specifying the visual properties as vertex and edge attributes, you can
also give them as keyword arguments to :func:`~drawing.plot`::

  >>> color_dict = {"m": "blue", "f": "pink"}
  >>> ig.plot(g, layout=layout, vertex_color=[color_dict[gender] for gender in g.vs["gender"]])

This latter approach is preferred if you want to keep the properties of the visual
representation of your graph separate from the graph itself. You can simply set up
a Python dictionary containing the keyword arguments you would pass to :func:`~drawing.plot`
and then use the double asterisk (``**``) operator to pass your specific styling
attributes to :func:`~drawing.plot`::

  >>> visual_style = {}
  >>> visual_style["vertex_size"] = 20
  >>> visual_style["vertex_color"] = [color_dict[gender] for gender in g.vs["gender"]]
  >>> visual_style["vertex_label"] = g.vs["name"]
  >>> visual_style["edge_width"] = [1 + 2 * int(is_formal) for is_formal in g.es["is_formal"]]
  >>> visual_style["layout"] = layout
  >>> visual_style["bbox"] = (300, 300)
  >>> visual_style["margin"] = 20
  >>> ig.plot(g, **visual_style)

The final plot shows the formal ties with thick lines while informal ones with thin lines:

.. figure:: figures/tutorial_social_network_3.png
   :alt: The visual representation of our social network - with names, genders and formal ties
   :align: center

   Our social network - also showing which ties are formal

To sum it all up: there are special vertex and edge properties that correspond to
the visual representation of the graph. These attributes override the default settings
of |igraph| (see :doc:`configuration` for overriding the system-wide defaults).
Furthermore, appropriate keyword arguments supplied to :func:`~drawing.plot` override the
visual properties provided by the vertex and edge attributes. The following two
tables summarise the most frequently used visual attributes for vertices and edges,
respectively:

Vertex attributes controlling graph plots
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

=============== ====================== ==========================================
Attribute name  Keyword argument       Purpose
=============== ====================== ==========================================
``color``       ``vertex_color``       Color of the vertex
--------------- ---------------------- ------------------------------------------
``font``        ``vertex_font``        Font family of the vertex
--------------- ---------------------- ------------------------------------------
``label``       ``vertex_label``       Label of the vertex
--------------- ---------------------- ------------------------------------------
``label_angle`` ``vertex_label_angle`` The placement of the vertex label on the
                                       circle around the vertex. This is an angle
                                       in radians, with zero belonging to the
                                       right side of the vertex.
--------------- ---------------------- ------------------------------------------
``label_color`` ``vertex_label_color`` Color of the vertex label
--------------- ---------------------- ------------------------------------------
``label_dist``  ``vertex_label_dist``  Distance of the vertex label from the
                                       vertex itself, relative to the vertex size
--------------- ---------------------- ------------------------------------------
``label_size``  ``vertex_label_size``  Font size of the vertex label
--------------- ---------------------- ------------------------------------------
``order``       ``vertex_order``       Drawing order of the vertices. Vertices
                                       with a smaller order parameter will be
                                       drawn first.
--------------- ---------------------- ------------------------------------------
``shape``       ``vertex_shape``       Shape of the vertex. Known shapes are:
                                       ``rectangle``, ``circle``, ``diamond``,
                                       ``hidden``, ``triangle-up``,
                                       ``triangle-down``.
                                       Several aliases are also accepted, see
                                       :data:`drawing.known_shapes`.
--------------- ---------------------- ------------------------------------------
``size``        ``vertex_size``        Size of the vertex in pixels
=============== ====================== ==========================================


Edge attributes controlling graph plots
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

=============== ====================== ==========================================
Attribute name  Keyword argument       Purpose
=============== ====================== ==========================================
``color``       ``edge_color``         Color of the edge
--------------- ---------------------- ------------------------------------------
``curved``      ``edge_curved``        The curvature of the edge. Positive values
                                       correspond to edges curved in CCW
                                       direction, negative numbers correspond to
                                       edges curved in clockwise (CW) direction.
                                       Zero represents straight edges. ``True``
                                       is interpreted as 0.5, ``False`` is
                                       interpreted as zero. This is useful to
                                       make multiple edges visible. See also the
                                       ``autocurve`` keyword argument to
                                       :func:`~drawing.plot`.
--------------- ---------------------- ------------------------------------------
``font``        ``edge_font``          Font family of the edge
--------------- ---------------------- ------------------------------------------
``arrow_size``  ``edge_arrow_size``    Size (length) of the arrowhead on the edge
                                       if the graph is directed, relative to 15
                                       pixels.
--------------- ---------------------- ------------------------------------------
``arrow_width`` ``edge_arrow_width``   Width of the arrowhead on the edge if the
                                       graph is directed, relative to 10 pixels.
--------------- ---------------------- ------------------------------------------
``loop_size``   ``edge_loop_size``     Size of self-loops. It can be set as a
                                       negative number, in which case it scales
                                       with the size of the corresponding vertex
                                       (e.g. -1.0 means the loop has the same size
                                       as the vertex). This attribute is
                                       ignored by edges that are not loops.
                                       This attribute is available only in the
                                       matplotlib backend.
--------------- ---------------------- ------------------------------------------
``width``       ``edge_width``         Width of the edge in pixels.
--------------- ---------------------- ------------------------------------------
``label``       ``edge_label``         If specified, it adds a label to the edge.
--------------- ---------------------- ------------------------------------------
``background``  ``edge_background``    If specified, it adds a rectangular box
                                       around the edge label, of the specified
                                       color (matplotlib only).
--------------- ---------------------- ------------------------------------------
``align_label`` ``edge_align_label``   If True, rotate the edge label such that
                                       it aligns with the edge direction. Labels
                                       that would be upside-down are flipped
                                       (matplotlib only).
=============== ====================== ==========================================


Generic keyword arguments of ``plot()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These settings can be specified as keyword arguments to the :func:`~drawing.plot` function
to control the overall appearance of the plot.

================ ================================================================
Keyword argument Purpose
================ ================================================================
``autocurve``    Whether to determine the curvature of the edges automatically in
                 graphs with multiple edges. The default is ``True`` for graphs
                 with less than 10.000 edges and ``False`` otherwise.
---------------- ----------------------------------------------------------------
``bbox``         The bounding box of the plot. This must be a tuple containing
                 the desired width and height of the plot. The default plot is
                 600 pixels wide and 600 pixels high. Ignored for the
                 Matplotlib backend.
---------------- ----------------------------------------------------------------
``layout``       The layout to be used. It can be an instance of
                 :class:`~layout.Layout`,
                 a list of tuples containing X-Y coordinates, or the name of a
                 layout algorithm. The default is ``auto``, which selects a
                 layout algorithm automatically based on the size and
                 connectedness of the graph.
---------------- ----------------------------------------------------------------
``margin``       The top, right, bottom and left margins of the plot in pixels.
                 This argument must be a list or tuple and its elements will be
                 re-used if you specify a list or tuple with less than four
                 elements. Ignored for the Matplotlib backend.
================ ================================================================

Specifying colors in plots
^^^^^^^^^^^^^^^^^^^^^^^^^^

|igraph| understands the following color specifications wherever it expects a
color (e.g., edge, vertex or label colors in the respective attributes):

X11 color names
    See the `list of X11 color names <https://en.wikipedia.org/wiki/X11_color_names>`_
    in Wikipedia for the complete list. Alternatively you can see the
    keys of the ``igraph.drawing.colors.known_colors`` dictionary. Color
    names are case insensitive in igraph so ``"DarkBlue"`` can be written as
    ``"darkblue"`` as well.

Color specification in CSS syntax
    This is a string according to one of the following formats (where *R*, *G* and
    *B* denote the red, green and blue components, respectively):

    - ``#RRGGBB``, components range from 0 to 255 in hexadecimal format.
      Example: ``"#0088ff"``.
    - ``#RGB``, components range from 0 to 15 in hexadecimal format. Example:
      ``"#08f"``.
    - ``rgb(R, G, B)``, components range from 0 to 255 or from 0% to
      100%. Example: ``"rgb(0, 127, 255)"`` or ``"rgb(0%, 50%, 100%)"``.

Lists or tuples of RGB values in the range 0-1
    Example: ``(1.0, 0.5, 0)`` or ``[1.0, 0.5, 0]``.

Note that when specifying the same color for all vertices or edges, you can use
a string as-is but not the tuple or list syntax as tuples or lists would be
interpreted as if the *items* in the tuple are for individual vertices or
edges. So, this would work::

  >>> ig.plot(g, vertex_color="green")

But this would not, as it would treat the items in the tuple as palette indices
for the first, second and third vertoces::

  >>> ig.plot(g, vertex_color=(1, 0, 0))

In this latter case, you need to expand the color specification for each vertex
explicitly::

  >>> ig.plot(g, vertex_color=[(1, 0, 0)] * g.vcount())


Saving plots
^^^^^^^^^^^^

|igraph| can be used to create publication-quality plots by asking the :func:`~drawing.plot`
function to save the plot into a file instead of showing it on a screen. This can
be done simply by passing the target filename as an additional argument after the
graph itself. The preferred format is inferred from the extension. |igraph| can
save to anything that is supported by Cairo, including SVG, PDF and PNG files.
SVG or PDF files can then later be converted to PostScript (``.ps``) or Encapsulated
PostScript (``.eps``) format if you prefer that, while PNG files can be converted to
TIF (``.tif``)::

  >>> ig.plot(g, "social_network.pdf", **visual_style)

If you are using the matplotlib backend, you can save your plot as usual::

  >>> fig, ax = plt.subplots()
  >>> ig.plot(g, **visual_style)
  >>> fig.savefig("social_network.pdf")

Many file formats are supported by matplotlib.

|igraph| and the outside world
==============================

No graph module would be complete without some kind of import/export functionality
that enables the package to communicate with external programs and toolkits. |igraph|
is no exception: it provides functions to read the most common graph formats and
to save :class:`Graph` objects into files obeying these format specifications.
The following table summarises the formats |igraph| can read or write:

================ ============= ============================ =============================
Format           Short name    Reader method                Writer method
================ ============= ============================ =============================
Adjacency list   ``lgl``       :meth:`Graph.Read_Lgl`       :meth:`Graph.write_lgl`
(a.k.a. `LGL`_)
---------------- ------------- ---------------------------- -----------------------------
Adjacency matrix ``adjacency`` :meth:`Graph.Read_Adjacency` :meth:`Graph.write_adjacency`
---------------- ------------- ---------------------------- -----------------------------
DIMACS           ``dimacs``    :meth:`Graph.Read_DIMACS`    :meth:`Graph.write_dimacs`
---------------- ------------- ---------------------------- -----------------------------
DL               ``dl``        :meth:`Graph.Read_DL`        not supported yet
---------------- ------------- ---------------------------- -----------------------------
Edge list        ``edgelist``, :meth:`Graph.Read_Edgelist`  :meth:`Graph.write_edgelist`
                 ``edges``,
                 ``edge``
---------------- ------------- ---------------------------- -----------------------------
`GraphViz`_      ``graphviz``, not supported yet            :meth:`Graph.write_dot`
                 ``dot``
---------------- ------------- ---------------------------- -----------------------------
GML              ``gml``       :meth:`Graph.Read_GML`       :meth:`Graph.write_gml`
---------------- ------------- ---------------------------- -----------------------------
GraphML          ``graphml``   :meth:`Graph.Read_GraphML`   :meth:`Graph.write_graphml`
---------------- ------------- ---------------------------- -----------------------------
Gzipped GraphML  ``graphmlz``  :meth:`Graph.Read_GraphMLz`  :meth:`Graph.write_graphmlz`
---------------- ------------- ---------------------------- -----------------------------
LEDA             ``leda``      not supported yet            :meth:`Graph.write_leda`
---------------- ------------- ---------------------------- -----------------------------
Labeled edgelist ``ncol``      :meth:`Graph.Read_Ncol`      :meth:`Graph.write_ncol`
(a.k.a. `NCOL`_)
---------------- ------------- ---------------------------- -----------------------------
`Pajek`_ format  ``pajek``,    :meth:`Graph.Read_Pajek`     :meth:`Graph.write_pajek`
                 ``net``
---------------- ------------- ---------------------------- -----------------------------
Pickled graph    ``pickle``    :meth:`Graph.Read_Pickle`    :meth:`Graph.write_pickle`
================ ============= ============================ =============================

.. _GraphViz: https://www.graphviz.org
.. _LGL: https://lgl.sourceforge.net/#FileFormat
.. _NCOL: https://lgl.sourceforge.net/#FileFormat
.. _Pajek: http://mrvar.fdv.uni-lj.si/pajek/

As an exercise, download the graph representation of the well-known
`Zachary karate club study <https://en.wikipedia.org/wiki/Zachary%27s_karate_club>`_
from :download:`this file </assets/zachary.zip>`, unzip it and try to load it into
|igraph|. Since it is a GraphML file, you must use the GraphML reader method from
the table above (make sure you use the appropriate path to the downloaded file)::

  >>> karate = ig.Graph.Read_GraphML("zachary.graphml")
  >>> ig.summary(karate)
  IGRAPH UNW- 34 78 -- Zachary's karate club network

If you want to convert the very same graph into, say, Pajek's format, you can do it
with the Pajek writer method from the table above::

  >>> karate.write_pajek("zachary.net")

.. note:: Most of the formats have their own limitations; for instance, not all of
   them can store attributes. Your best bet is probably GraphML or GML if you
   want to save |igraph| graphs in a format that can be read from an external
   package and you want to preserve numeric and string attributes. Edge list and
   NCOL is also fine if you don't have attributes (NCOL supports vertex names and
   edge weights, though). If you don't want to use your graphs outside |igraph|
   but you want to store them for a later session, the pickled graph format
   ensures that you get exactly the same graph back. The pickled graph format
   uses Python's ``pickle`` module to store and read graphs.

There are two helper methods as well: :func:`read` is a generic entry point for
reader methods which tries to infer the appropriate format from the file extension.
:meth:`Graph.write` is the opposite of :func:`read`: it lets you save a graph where
the preferred format is again inferred from the extension. The format detection of
:func:`read` and :meth:`Graph.write` can be overridden by the ``format`` keyword
argument which accepts the short names of the formats from the above table::

  >>> karate = ig.load("zachary.graphml")
  >>> karate.write("zachary.net")
  >>> karate.write("zachary.my_extension", format="gml")


Where to go next
================

This tutorial was only scratching the surface of what |igraph| can do.  My
long-term plans are to extend this tutorial into a proper manual-style
documentation to |igraph| in the next chapters. In the meanwhile, check out the
:doc:`api/index` which should provide information about almost every
|igraph| class, function or method. A good starting point is the documentation
of the :class:`Graph` class. Should you get stuck, try asking in our
`Discourse group`_ first - maybe there is someone out there who can help you
out immediately.

.. _Discourse group: https://igraph.discourse.group
.. _matplotlib: https://matplotlib.org/
.. _IPython: https://ipython.readthedocs.io/en/stable/
.. _Jupyter: https://jupyter.org/
