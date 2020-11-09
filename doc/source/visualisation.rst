.. include:: include/global.rst

Visualisation of graphs
=======================
|igraph| includes functionality to visualize graphs. There are two main components: graph layouts and graph plotting.

In the following examples, we will assume |igraph| is imported as `ig` and a
:class:`Graph` object has been previously created, e.g.:

>>> import igraph as ig
>>> g = ig.Graph(edges=[[0, 1], [2, 3]])

Read the `API documentation`_ for details on each function and class.

Graph layouts
+++++++++++++
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

The following layouts are supported:

- `Graph.layout_bipartite`: bipartite layout
- `Graph.layout_circle`: circular/spherical layout
- `Graph.layout_davidson_harel`: Davidson-Harel layout
- `Graph.layout_drl`: DrL layout for large graphs (2D and 3D)
- `Graph.layout_fruchterman_reingold`: Fruchterman-Reingold layout (2D and 3D)
- `Graph.layout_grid`: regular grid layout in 2D
- `Graph.layout_grid_3d`: regular grid layout in 3D
- `Graph.layout_graphopt`: the graphopt algorithm
- `Graph.layout_kamada_kawai`: Kamada-Kawai layout (2D and 3D)
- `Graph.layout_lgl`: Large Graph Layout
- `Graph.layout_mds`: multidimensional scaling layout
- `Graph.layout_random`: random layout (2D and 3D)
- `Graph.layout_reingold_tilford`: Reingold-Tilford *tree* layout
- `Graph.layout_reingold_tilford_circular`: circular Reingold-Tilford *tree* layout
- `Graph.layout_star`: star layout
- `Graph.layout_sugiyama`: Sugiyama layout

More might be added in the future, based on request.

Graph plotting
++++++++++++++
Once the layout of a graph has been computed, |igraph| can assist with the plotting itself.




.. _API documentation: https://igraph.org/python/doc/igraph-module.html
