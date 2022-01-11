"""
Drawing routines to draw graphs.

This module contains routines to draw graphs on:

  - Cairo surfaces (L{DefaultGraphDrawer})
  - Matplotlib axes (L{MatplotlibGraphDrawer})

It also contains routines to send an igraph graph directly to
(U{Cytoscape<http://www.cytoscape.org>}) using the
(U{CytoscapeRPC plugin<http://gforge.nbic.nl/projects/cytoscaperpc/>}), see
L{CytoscapeGraphDrawer}. L{CytoscapeGraphDrawer} can also fetch the current
network from Cytoscape and convert it to igraph format.
"""

from warnings import warn

from igraph._igraph import convex_hull, VertexSeq
from igraph.drawing.baseclasses import AbstractGraphDrawer
from igraph.drawing.utils import Point

from .edge import MatplotlibEdgeDrawer
from .polygon import MatplotlibPolygonDrawer
from .utils import find_matplotlib
from .vertex import MatplotlibVertexDrawer

__all__ = ("MatplotlibGraphDrawer",)

_, plt = find_matplotlib()

#####################################################################


class MatplotlibGraphDrawer(AbstractGraphDrawer):
    """Graph drawer that uses a pyplot.Axes as context"""

    _shape_dict = {
        "rectangle": "s",
        "circle": "o",
        "hidden": "none",
        "triangle-up": "^",
        "triangle-down": "v",
    }

    def __init__(
        self,
        ax,
        vertex_drawer_factory=MatplotlibVertexDrawer,
        edge_drawer_factory=MatplotlibEdgeDrawer,
    ):
        """Constructs the graph drawer and associates it with the mpl Axes

        @param ax: the matplotlib Axes to draw into.
        @param vertex_drawer_factory: a factory method that returns an
            L{AbstractVertexDrawer} instance bound to the given Matplotlib axes.
            The factory method must take three parameters: the axes and the
            palette to be used for drawing colored vertices, and the layout of
            the graph. The default vertex drawer is L{MatplotlibVertexDrawer}.
        @param edge_drawer_factory: a factory method that returns an
            L{AbstractEdgeDrawer} instance bound to a given Matplotlib Axes.
            The factory method must take two parameters: the Axes and the palette
            to be used for drawing colored edges. The default edge drawer is
            L{MatplotlibEdgeDrawer}.
        """
        self.ax = ax
        self.vertex_drawer_factory = vertex_drawer_factory
        self.edge_drawer_factory = edge_drawer_factory

    def draw(self, graph, *args, **kwds):
        # Deferred import to avoid a cycle in the import graph
        from igraph.clustering import VertexClustering, VertexCover

        # Positional arguments are not used
        if args:
            warn(
                "Positional arguments to plot functions are ignored "
                "and will be deprecated soon.",
                DeprecationWarning,
            )

        # Some abbreviations for sake of simplicity
        directed = graph.is_directed()
        ax = self.ax

        # Palette
        palette = kwds.pop("palette", None)

        # Calculate/get the layout of the graph
        layout = self.ensure_layout(kwds.get("layout", None), graph)

        # Decide whether we need to calculate the curvature of edges
        # automatically -- and calculate them if needed.
        autocurve = kwds.get("autocurve", None)
        if autocurve or (
            autocurve is None
            and "edge_curved" not in kwds
            and "curved" not in graph.edge_attributes()
            and graph.ecount() < 10000
        ):
            from igraph import autocurve

            default = kwds.get("edge_curved", 0)
            if default is True:
                default = 0.5
            default = float(default)
            kwds["edge_curved"] = autocurve(
                graph,
                attribute=None,
                default=default,
            )

        # Construct the vertex, edge and label drawers
        vertex_drawer = self.vertex_drawer_factory(ax, palette, layout)
        edge_drawer = self.edge_drawer_factory(ax, palette)

        # Construct the visual vertex/edge builders based on the specifications
        # provided by the vertex_drawer and the edge_drawer
        vertex_builder = vertex_drawer.VisualVertexBuilder(graph.vs, kwds)
        edge_builder = edge_drawer.VisualEdgeBuilder(graph.es, kwds)

        # Draw the highlighted groups (if any)
        if "mark_groups" in kwds:
            mark_groups = kwds["mark_groups"]

            # Deferred import to avoid a cycle in the import graph
            from igraph.clustering import VertexClustering, VertexCover

            # Figure out what to do with mark_groups in order to be able to
            # iterate over it and get memberlist-color pairs
            if isinstance(mark_groups, dict):
                # Dictionary mapping vertex indices or tuples of vertex
                # indices to colors
                group_iter = iter(mark_groups.items())
            elif isinstance(mark_groups, (VertexClustering, VertexCover)):
                # Vertex clustering
                group_iter = ((group, color) for color, group in enumerate(mark_groups))
            elif hasattr(mark_groups, "__iter__"):
                # Lists, tuples, iterators etc
                group_iter = iter(mark_groups)
            else:
                # False
                group_iter = iter({}.items())

            if kwds.get("legend", False):
                legend_info = {
                    "handles": [],
                    "labels": [],
                }

            # Iterate over color-memberlist pairs
            for group, color_id in group_iter:
                if not group or color_id is None:
                    continue

                color = palette.get(color_id)

                if isinstance(group, VertexSeq):
                    group = [vertex.index for vertex in group]
                if not hasattr(group, "__iter__"):
                    raise TypeError("group membership list must be iterable")

                # Get the vertex indices that constitute the convex hull
                hull = [group[i] for i in convex_hull([layout[idx] for idx in group])]

                # Calculate the preferred rounding radius for the corners
                corner_radius = 1.25 * max(vertex_builder[idx].size for idx in hull)

                # Construct the polygon
                polygon = [layout[idx] for idx in hull]

                if len(polygon) == 2:
                    # Expand the polygon (which is a flat line otherwise)
                    a, b = Point(*polygon[0]), Point(*polygon[1])
                    c = corner_radius * (a - b).normalized()
                    n = Point(-c[1], c[0])
                    polygon = [a + n, b + n, b - c, b - n, a - n, a + c]
                else:
                    # Expand the polygon around its center of mass
                    center = Point(
                        *[sum(coords) / float(len(coords)) for coords in zip(*polygon)]
                    )
                    polygon = [
                        Point(*point).towards(center, -corner_radius)
                        for point in polygon
                    ]

                # Draw the hull
                facecolor = (color[0], color[1], color[2], 0.25 * color[3])
                drawer = MatplotlibPolygonDrawer(ax)
                drawer.draw(
                    polygon,
                    corner_radius=corner_radius,
                    facecolor=facecolor,
                    edgecolor=color,
                )

                if kwds.get("legend", False):
                    legend_info["handles"].append(
                        plt.Rectangle(
                            (0, 0),
                            0,
                            0,
                            facecolor=facecolor,
                            edgecolor=color,
                        )
                    )
                    legend_info["labels"].append(str(color_id))

            if kwds.get("legend", False):
                ax.legend(
                    legend_info["handles"],
                    legend_info["labels"],
                )

        # Determine the order in which we will draw the vertices and edges
        vertex_order = self._determine_vertex_order(graph, kwds)
        edge_order = self._determine_edge_order(graph, kwds)

        # Construct the iterator that we will use to draw the vertices
        vs = graph.vs
        if vertex_order is None:
            # Default vertex order
            vertex_coord_iter = zip(vs, vertex_builder, layout)
        else:
            # Specified vertex order
            vertex_coord_iter = (
                (vs[i], vertex_builder[i], layout[i]) for i in vertex_order
            )

        # Draw the vertices
        drawer_method = vertex_drawer.draw
        for vertex, visual_vertex, coords in vertex_coord_iter:
            drawer_method(visual_vertex, vertex, coords)

        # Construct the iterator that we will use to draw the vertex labels
        vs = graph.vs
        if vertex_order is None:
            # Default vertex order
            vertex_coord_iter = zip(vertex_builder, layout)
        else:
            # Specified vertex order
            vertex_coord_iter = ((vertex_builder[i], layout[i]) for i in vertex_order)

        # Draw the vertex labels
        for vertex, coords in vertex_coord_iter:
            if vertex.label is None:
                continue

            label_size = kwds.get(
                "vertex_label_size",
                vertex.label_size,
            )

            ax.text(
                *coords,
                vertex.label,
                fontsize=label_size,
                ha='center',
                va='center',
                # TODO: overlap, offset, etc.
            )

        # Construct the iterator that we will use to draw the edges
        es = graph.es
        if edge_order is None:
            # Default edge order
            edge_coord_iter = zip(es, edge_builder)
        else:
            # Specified edge order
            edge_coord_iter = ((es[i], edge_builder[i]) for i in edge_order)

        # Draw the edges
        if directed:
            drawer_method = edge_drawer.draw_directed_edge
        else:
            drawer_method = edge_drawer.draw_undirected_edge
        for edge, visual_edge in edge_coord_iter:
            src, dest = edge.tuple
            src_vertex, dest_vertex = vertex_builder[src], vertex_builder[dest]
            drawer_method(visual_edge, src_vertex, dest_vertex)

        # Draw the edge labels
        labels = kwds.get("edge_label", None)
        if labels is not None:
            edge_label_iter = (
                (labels[i], edge_builder[i], graph.es[i]) for i in range(graph.ecount())
            )
            for label, visual_edge, edge in edge_label_iter:
                # Ask the edge drawer to propose an anchor point for the label
                src, dest = edge.tuple
                src_vertex, dest_vertex = vertex_builder[src], vertex_builder[dest]
                (x, y), (halign, valign) = edge_drawer.get_label_position(
                    visual_edge,
                    src_vertex,
                    dest_vertex,
                )

                text_kwargs = {}
                text_kwargs['ha'] = halign.value
                text_kwargs['va'] = valign.value

                if visual_edge.background is not None:
                    text_kwargs['bbox'] = dict(
                        facecolor=visual_edge.background,
                        edgecolor='none',
                    )
                    text_kwargs['ha'] = 'center'
                    text_kwargs['va'] = 'center'

                if visual_edge.align_label:
                    # Rotate the text to align with the edge
                    rotation = edge_drawer.get_label_rotation(
                        visual_edge, src_vertex, dest_vertex,
                    )
                    text_kwargs['rotation'] = rotation

                ax.text(
                    x,
                    y,
                    label,
                    fontsize=visual_edge.label_size,
                    color=visual_edge.label_color,
                    **text_kwargs,
                    # TODO: offset, etc.
                )

        # Despine
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)

        # Remove axis ticks
        ax.set_xticks([])
        ax.set_yticks([])

        # Set equal aspect to get actual circles
        ax.set_aspect(1)

        # Autoscale for x/y axis limits
        ax.autoscale_view()
