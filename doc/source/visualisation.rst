.. include:: include/global.rst

=======================
Visualisation of graphs
=======================
|igraph| includes functionality to visualize graphs. There are two main components: graph layouts and graph plotting.

In the following examples, we will assume |igraph| is imported as `ig` and a
:class:`Graph` object has been previously created, e.g.:

>>> import igraph as ig
>>> g = ig.Graph(edges=[[0, 1], [2, 3]])

Read the `API documentation`_ for details on each function and class. The `tutorial`_ contains examples to get started.

Graph layouts
=============
A graph *layout* is a low-dimensional (usually: 2 dimensional) representation of a graph. Different layouts for the same
graph can be computed and typically preserve or highlight distinct properties of the graph itself. Some layouts only make
sense for specific kinds of graphs, such as trees.

|igraph| offers several graph layouts. The general function to compute a graph layout is :meth:`Graph.layout`:

>>> layout = g.layout(layout='auto')

See below for a list of supported layouts. The resulting object is an instance of `igraph.layout.Layout` and has some
useful properties:

- :attr:`Layout.coords`: the coordinates of the vertices in the layout (each row is a vertex)
- :attr:`Layout.dim`: the number of dimensions of the embedding (usually 2)

and methods:

- :meth:`Layout.boundaries` the rectangle with the extreme coordinates of the layout
- :meth:`Layout.bounding_box` the boundary, but as an `igraph.drawing.utils.BoundingBox` (see below)
- :meth:`Layout.centroid` the coordinates of the centroid of the graph layout

Indexing and slicing can be performed and returns the coordinates of the requested vertices:

>>> coords_subgraph = layout[:2]  # Coordinate of the first vertex

.. note:: The returned object is a list of lists with the coordinates, not an `igraph.layout.Layout`
   object. You can wrap the result into such an object easily:
 
   >>> layout_subgraph = ig.Layout(coords=layout[:2])

It is possible to perform linear transformations to the layout:

- :meth:`Layout.translate`
- :meth:`Layout.center`
- :meth:`Layout.scale`
- :meth:`Layout.fit_into`
- :meth:`Layout.rotate`
- :meth:`Layout.mirror`

as well as a generic nonlinear transformation via:

- :meth:`Layout.transform`

The following regular layouts are supported:

- `Graph.layout_star`: star layout
- `Graph.layout_circle`: circular/spherical layout
- `Graph.layout_grid`: regular grid layout in 2D
- `Graph.layout_grid_3d`: regular grid layout in 3D
- `Graph.layout_random`: random layout (2D and 3D)

The following algorithms produce nice layouts for general graphs:

- `Graph.layout_davidson_harel`: Davidson-Harel layout, based on simulated annealing optimization including edge crossings
- `Graph.layout_drl`: DrL layout for large graphs (2D and 3D), a scalable force-directed layout
- `Graph.layout_fruchterman_reingold`: Fruchterman-Reingold layout (2D and 3D), a "spring-electric" layout based on classical physics
- `Graph.layout_graphopt`: the graphopt algorithm, another force-directed layout
- `Graph.layout_kamada_kawai`: Kamada-Kawai layout (2D and 3D), a "spring" layout based on classical physics
- `Graph.layout_lgl`: Large Graph Layout
- `Graph.layout_mds`: multidimensional scaling layout

The following algorithms are useful for *trees* (and for Sugiyama *directed acyclic graphs* or *DAGs*):

- `Graph.layout_reingold_tilford`: Reingold-Tilford layout
- `Graph.layout_reingold_tilford_circular`: circular Reingold-Tilford layout
- `Graph.layout_sugiyama`: Sugiyama layout, a hierarchical layout

For *bipartite graphs*, there is a dedicated function:

- `Graph.layout_bipartite`: bipartite layout

More might be added in the future, based on request.

Graph plotting
==============
Once the layout of a graph has been computed, |igraph| can assist with the plotting itself. Plotting happens within a single
function, `igraph.plot`. This function can be called in two ways:

1. without a filename argument: this generates a temporary file and opens it with the default image viewer:

>>> ig.plot(g)

(see below if you are using this in a `Jupyter`_ notebook).

2. with a filename argument: this stores the graph image in the specified file and does *not* open it automatically. Based on
   the filename extension, any of the following output formats can be chosen: PNG, PDF, SVG and PostScript:

>>> ig.plot(g, 'myfile.pdf')

.. note:: PNG is a raster image format while PDF, SVG, and Postscript are vector image formats. Choose one of the last three
   formats if you are planning on refining the image with a vector image editor such as Inkscape or Illustrator.

In both cases, you can add an argument `layout` to the `plot` function to specify a precomputed layout, e.g.:

>>> layout = g.layout("kamada_kawai")
>>> ig.plot(g, layout=layout)

You can specify additional options such as vertex and edge color, size, and labels via additional arguments, e.g.:

>>> ig.plot(g,
>>>         vertex_size=20,
>>>         vertex_color=['blue', 'red', 'green', 'yellow'],
>>>         vertex_label=['first', 'second', 'third', 'fourth'],
>>>         edge_width=[1, 4],
>>>         edge_color=['black', 'grey'],
>>>         )

See the `tutorial`_ for examples and a full list of options.

Jupyter notebook
++++++++++++++++
|igraph| supports inline plots within a `Jupyter`_ notebook. If you are calling `igraph.plot` from a notebook cell, the image
will be shown inline in the corresponding output cell. Use the `bbox` argument to scale the image while preserving the size
of the vertices, text, and other artists. For instance, to get a compact plot:

>>> ig.plot(g, bbox=(0, 0, 100, 100))

These inline plots can be either in PNG or SVG format. There is currently an open bug that makes SVG fail if more than one graph
per notebook is plotted: we are working on a fix for that. In the meanwhile, you can use PNG representation.

Matplotlib interactive plots
++++++++++++++++++++++++++++
We are currently working on extending this functionality to play nicely with `matplotlib`_ for interactive graphs. Stay tuned.


.. _API documentation: https://igraph.org/python/doc/igraph-module.html
.. _matplotlib: https://matplotlib.org
.. _Jupyter: https://jupyter.org/
.. _tutorial: https://igraph.org/python/doc/tutorial/tutorial.html#layouts-and-plotting
