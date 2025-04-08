.. include:: include/global.rst

=======================
Visualisation of graphs
=======================
|igraph| includes functionality to visualize graphs. There are two main components: graph layouts and graph plotting.

In the following examples, we will assume |igraph| is imported as `ig` and a
:class:`Graph` object has been previously created, e.g.::

   >>> import igraph as ig
   >>> g = ig.Graph(edges=[[0, 1], [2, 3]])

Read the :doc:`api/index` for details on each function and class. See the :ref:`tutorial <tutorial-layouts-plotting>` and
the :doc:`tutorials/index` for examples.

Graph layouts
=============
A graph *layout* is a low-dimensional (usually: 2 dimensional) representation of a graph. Different layouts for the same
graph can be computed and typically preserve or highlight distinct properties of the graph itself. Some layouts only make
sense for specific kinds of graphs, such as trees.

|igraph| offers several graph layouts. The general function to compute a graph layout is :meth:`Graph.layout`::

   >>> layout = g.layout(layout='auto')

See below for a list of supported layouts. The resulting object is an instance of `igraph.layout.Layout` and has some
useful properties:

- :attr:`Layout.coords`: the coordinates of the vertices in the layout (each row is a vertex)
- :attr:`Layout.dim`: the number of dimensions of the embedding (usually 2)

and methods:

- :meth:`Layout.boundaries` the rectangle with the extreme coordinates of the layout
- :meth:`Layout.bounding_box` the boundary, but as an `igraph.drawing.utils.BoundingBox` (see below)
- :meth:`Layout.centroid` the coordinates of the centroid of the graph layout

Indexing and slicing can be performed and returns the coordinates of the requested vertices::

   >>> coords_subgraph = layout[:2]  # Coordinates of the first two vertices

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
- `Graph.layout_umap`: Uniform Manifold Approximation and Projection (2D and 3D). UMAP works especially well when the graph is composed
  by "clusters" that are loosely connected to each other.

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
function, `igraph.plot`.

Plotting with the default image viewer
++++++++++++++++++++++++++++++++++++++

A naked call to `igraph.plot` generates a temporary file and opens it with the default image viewer::

   >>> ig.plot(g)

(see below if you are using this in a `Jupyter`_ notebook). This uses the `Cairo`_ library behind the scenes.

Saving a plot to a file
+++++++++++++++++++++++

A call to `igraph.plot` with a `target` argument stores the graph image in the specified file and does *not*
open it automatically. Based on the filename extension, any of the following output formats can be chosen:
PNG, PDF, SVG and PostScript::

   >>> ig.plot(g, target='myfile.pdf')

.. note:: PNG is a raster image format while PDF, SVG, and Postscript are vector image formats. Choose one of the last three
   formats if you are planning on refining the image with a vector image editor such as Inkscape or Illustrator.

Plotting graphs within Matplotlib figures
+++++++++++++++++++++++++++++++++++++++++

If the target argument is a `matplotlib`_ axes, the graph will be plotted inside that axes::

   >>> import matplotlib.pyplot as plt
   >>> fig, ax = plt.subplots()
   >>> ig.plot(g, target=ax)

You can then further manipulate the axes and figure however you like via the `ax` and `fig` variables (or whatever you
called them). This variant does not use `Cairo`_ directly and might be lacking some features that are available in the
`Cairo`_ backend: please open an issue on Github to request specific features.

.. note::
   When plotting rooted trees, Cairo automatically puts the root on top of the image and
   the leaves at the bottom. For `matplotlib`_, the root is usually at the bottom instead.
   You can easily place the root on top by calling `ax.invert_yaxis()`.

Plotting via `matplotlib`_ makes it easy to combine igraph with other plots. For instance, if you want to have a figure
with two panels showing different aspects of some data set, say a graph and a bar plot, you can easily do that::

   >>> import matplotlib.pyplot as plt
   >>> fig, axs = plt.subplots(1, 2, figsize=(8, 4))
   >>> ig.plot(g, target=axs[0])
   >>> axs[1].bar(x=[0, 1, 2], height=[1, 5, 3], color='tomato')

Another common situation is modifying the graph plot after the fact, to achieve some kind of customization. For instance,
you might want to change the size and color of the vertices::

   >>> import matplotlib.pyplot as plt
   >>> fig, ax = plt.subplots()
   >>> ig.plot(g, target=ax)
   >>> artist = ax.get_children()[0] # This is a GraphArtist
   >>> dots = artist.get_vertices()
   >>> dot.set_facecolors(['tomato'] * g.vcount())
   >>> dot.set_sizes(dot.get_sizes() * 2) # double the default radius

That also helps as a workaround if you cannot figure out how to use the plotting options below: just use the defaults and
then customize the appearance of your graph via standard `matplotlib`_ tools.

.. note:: The order of `artist.get_children()` is the following: (i) one artist for clustering hulls if requested;
   (ii) one artist for edges; (iii) one artist for vertices; (iv) one artist for **each** edge label; (v) one
   artist for **each** vertex label.

To use `matplotlib_` as your default plotting backend, you can set:

>>> ig.config['plotting.backend'] = 'matplotlib'

Then you don't have to specify an `Axes` anymore:

>>> ig.plot(g)

will automatically make a new `Axes` for you and return it.


Plotting graphs in Jupyter notebooks
++++++++++++++++++++++++++++++++++++

|igraph| supports inline plots within a `Jupyter`_ notebook via both the `Cairo`_ and `matplotlib`_ backend. If you are
calling `igraph.plot` from a notebook cell without a `matplotlib`_ axes, the image will be shown inline in the corresponding
output cell. Use the `bbox` argument to scale the image while preserving the size of the vertices, text, and other artists.
For instance, to get a compact plot (using the Cairo backend only)::

   >>> ig.plot(g, bbox=(0, 0, 100, 100))

These inline plots can be either in PNG or SVG format. There is currently an open bug that makes SVG fail if more than one graph
per notebook is plotted: we are working on a fix for that. In the meanwhile, you can use PNG representation.

If you want to use the `matplotlib`_ engine in a Jupyter notebook, you can use the recipe above. First create an axes, then
tell `igraph.plot` about it via the `target` argument::

   >>> import matplotlib.pyplot as plt
   >>> fig, ax = plt.subplots()
   >>> ig.plot(g, target=ax)

Exporting to other graph formats
++++++++++++++++++++++++++++++++++
If igraph is missing a certain plotting feature and you cannot wait for us to include it, you can always export your graph
to a number of formats and use an external graph plotting tool. We support both conversion to file (e.g. DOT format used by
`graphviz`_) and to popular graph libraries such as `networkx`_ and `graph-tool`_::

   >>> dot = g.write('/myfolder/myfile.dot')
   >>> n = g.to_networkx()
   >>> gt = g.to_graph_tool()

You do not need to have any libraries installed if you export to file, but you do need them to convert directly to external
Python objects (`networkx`_, `graph-tool`_).

Plotting options
================

You can add an argument `layout` to the `plot` function to specify a precomputed layout, e.g.::

   >>> layout = g.layout("kamada_kawai")
   >>> ig.plot(g, layout=layout)

It is also possible to use the name of the layout algorithm directly::

   >>> ig.plot(g, layout="kamada_kawai")

If the layout is left unspecified, igraph uses the dedicated `layout_auto()` function, which chooses between one of several
possible layouts based on the number of vertices and edges.

You can also specify vertex and edge color, size, and labels - and more - via additional arguments, e.g.::

   >>> ig.plot(g,
   ...         vertex_size=20,
   ...         vertex_color=['blue', 'red', 'green', 'yellow'],
   ...         vertex_label=['first', 'second', 'third', 'fourth'],
   ...         edge_width=[1, 4],
   ...         edge_color=['black', 'grey'],
   ...         )

See the :ref:`tutorial <tutorial-layouts-plotting>` for examples and a full list of options.

.. _matplotlib: https://matplotlib.org
.. _Jupyter: https://jupyter.org/
.. _Cairo: https://www.cairographics.org
.. _graphviz: https://www.graphviz.org
.. _networkx: https://networkx.org/
.. _graph-tool: https://graph-tool.skewed.de/
