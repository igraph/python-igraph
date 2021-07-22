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

from math import atan2, cos, pi, sin, tan, sqrt
from warnings import warn

from igraph._igraph import convex_hull, VertexSeq
from igraph.configuration import Configuration
from igraph.drawing.baseclasses import (
    AbstractDrawer,
    AbstractCairoDrawer,
    AbstractXMLRPCDrawer,
)
from igraph.drawing.colors import color_to_html_format, color_name_to_rgb
from igraph.drawing.edge import ArrowEdgeDrawer, MatplotlibArrowEdgeDrawer
from igraph.drawing.text import TextAlignment, TextDrawer
from igraph.drawing.metamagic import AttributeCollectorBase
from igraph.drawing.shapes import CairoPolygonDrawer, MatplotlibPolygonDrawer
from igraph.drawing.utils import find_cairo, find_matplotlib, Point
from igraph.drawing.vertex import DefaultVertexDrawer, MatplotlibVertexDrawer
from igraph.layout import Layout

__all__ = (
    "CairoGraphDrawer", "MatplotlibGraphDrawer", "CytoscapeGraphDrawer",
    "UbiGraphDrawer",
    "DefaultGraphDrawer",  # TODO: deprecate
)

cairo = find_cairo()
mpl, plt = find_matplotlib()

#####################################################################


class AbstractGraphDrawer(AbstractDrawer):
    """Abstract class that serves as a base class for anything that
    draws an igraph.Graph."""

    def draw(self, graph, *args, **kwds):
        """Abstract method, must be implemented in derived classes."""
        raise NotImplementedError("abstract class")

    def ensure_layout(self, layout, graph=None):
        """Helper method that ensures that I{layout} is an instance
        of L{Layout}. If it is not, the method will try to convert
        it to a L{Layout} according to the following rules:

          - If I{layout} is a string, it is assumed to be a name
            of an igraph layout, and it will be passed on to the
            C{layout} method of the given I{graph} if I{graph} is
            not C{None}.

          - If I{layout} is C{None}, the C{layout} method of
            I{graph} will be invoked with no parameters, which
            will call the default layout algorithm.

          - Otherwise, I{layout} will be passed on to the constructor
            of L{Layout}. This handles lists of lists, lists of tuples
            and such.

        If I{layout} is already a L{Layout} instance, it will still
        be copied and a copy will be returned. This is because graph
        drawers are allowed to transform the layout for their purposes,
        and we don't want the transformation to propagate back to the
        caller.
        """
        if isinstance(layout, Layout):
            layout = Layout(layout.coords)
        elif isinstance(layout, str) or layout is None:
            layout = graph.layout(layout)
        else:
            layout = Layout(layout)
        return layout

    @staticmethod
    def _determine_edge_order(graph, kwds):
        """Returns the order in which the edge of the given graph have to be
        drawn, assuming that the relevant keyword arguments (C{edge_order} and
        C{edge_order_by}) are given in C{kwds} as a dictionary. If neither
        C{edge_order} nor C{edge_order_by} is present in C{kwds}, this
        function returns C{None} to indicate that the graph drawer is free to
        choose the most convenient edge ordering."""
        if "edge_order" in kwds:
            # Edge order specified explicitly
            return kwds["edge_order"]

        if kwds.get("edge_order_by") is None:
            # No edge order specified
            return None

        # Order edges by the value of some attribute
        edge_order_by = kwds["edge_order_by"]
        reverse = False
        if isinstance(edge_order_by, tuple):
            edge_order_by, reverse = edge_order_by
            if isinstance(reverse, str):
                reverse = reverse.lower().startswith("desc")
        attrs = graph.es[edge_order_by]
        edge_order = sorted(
            list(range(len(attrs))), key=attrs.__getitem__, reverse=bool(reverse)
        )

        return edge_order

    @staticmethod
    def _determine_vertex_order(graph, kwds):
        """Returns the order in which the vertices of the given graph have to be
        drawn, assuming that the relevant keyword arguments (C{vertex_order} and
        C{vertex_order_by}) are given in C{kwds} as a dictionary. If neither
        C{vertex_order} nor C{vertex_order_by} is present in C{kwds}, this
        function returns C{None} to indicate that the graph drawer is free to
        choose the most convenient vertex ordering."""
        if "vertex_order" in kwds:
            # Vertex order specified explicitly
            return kwds["vertex_order"]

        if kwds.get("vertex_order_by") is None:
            # No vertex order specified
            return None

        # Order vertices by the value of some attribute
        vertex_order_by = kwds["vertex_order_by"]
        reverse = False
        if isinstance(vertex_order_by, tuple):
            vertex_order_by, reverse = vertex_order_by
            if isinstance(reverse, str):
                reverse = reverse.lower().startswith("desc")
        attrs = graph.vs[vertex_order_by]
        vertex_order = sorted(
            list(range(len(attrs))), key=attrs.__getitem__, reverse=bool(reverse)
        )

        return vertex_order

#####################################################################


class AbstractCairoGraphDrawer(AbstractGraphDrawer, AbstractCairoDrawer):
    """Abstract base class for graph drawers that draw on a Cairo canvas."""

    def __init__(self, context, bbox):
        """Constructs the graph drawer and associates it to the given
        Cairo context and the given L{BoundingBox}.

        @param context: the context on which we will draw
        @param bbox:    the bounding box within which we will draw.
                        Can be anything accepted by the constructor
                        of L{BoundingBox} (i.e., a 2-tuple, a 4-tuple
                        or a L{BoundingBox} object).
        """
        AbstractCairoDrawer.__init__(self, context, bbox)
        AbstractGraphDrawer.__init__(self)


#####################################################################


class CairoGraphDrawer(AbstractCairoGraphDrawer):
    """Class implementing the default visualisation of a graph.

    The default visualisation of a graph draws the nodes on a 2D plane
    according to a given L{Layout}, then draws a straight or curved
    edge between nodes connected by edges. This is the visualisation
    used when one invokes the L{plot()} function on a L{Graph} object.

    See L{Graph.__plot__()} for the keyword arguments understood by
    this drawer."""

    def __init__(
        self,
        context,
        bbox,
        vertex_drawer_factory=DefaultVertexDrawer,
        edge_drawer_factory=ArrowEdgeDrawer,
        label_drawer_factory=TextDrawer,
    ):
        """Constructs the graph drawer and associates it to the given
        Cairo context and the given L{BoundingBox}.

        @param context: the context on which we will draw
        @param bbox:    the bounding box within which we will draw.
                        Can be anything accepted by the constructor
                        of L{BoundingBox} (i.e., a 2-tuple, a 4-tuple
                        or a L{BoundingBox} object).
        @param vertex_drawer_factory: a factory method that returns an
                        L{AbstractCairoVertexDrawer} instance bound to a
                        given Cairo context. The factory method must take
                        three parameters: the Cairo context, the bounding
                        box of the drawing area and the palette to be
                        used for drawing colored vertices. The default
                        vertex drawer is L{DefaultVertexDrawer}.
        @param edge_drawer_factory: a factory method that returns an
                        L{AbstractEdgeDrawer} instance bound to a
                        given Cairo context. The factory method must take
                        two parameters: the Cairo context and the palette
                        to be used for drawing colored edges. You can use
                        any of the actual L{AbstractEdgeDrawer}
                        implementations here to control the style of
                        edges drawn by igraph. The default edge drawer is
                        L{ArrowEdgeDrawer}.
        @param label_drawer_factory: a factory method that returns a
                        L{TextDrawer} instance bound to a given Cairo
                        context. The method must take one parameter: the
                        Cairo context. The default label drawer is
                        L{TextDrawer}.
        """
        AbstractCairoGraphDrawer.__init__(self, context, bbox)
        self.vertex_drawer_factory = vertex_drawer_factory
        self.edge_drawer_factory = edge_drawer_factory
        self.label_drawer_factory = label_drawer_factory

    def draw(self, graph, palette, *args, **kwds):
        # Some abbreviations for sake of simplicity
        directed = graph.is_directed()
        context = self.context

        # Calculate/get the layout of the graph
        layout = self.ensure_layout(kwds.get("layout", None), graph)

        # Determine the size of the margin on each side
        margin = kwds.get("margin", 0)
        try:
            margin = list(margin)
        except TypeError:
            margin = [margin]
        while len(margin) < 4:
            margin.extend(margin)

        # Contract the drawing area by the margin and fit the layout
        bbox = self.bbox.contract(margin)
        layout.fit_into(bbox, keep_aspect_ratio=kwds.get("keep_aspect_ratio", False))

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
            kwds["edge_curved"] = autocurve(graph, attribute=None, default=default)

        # Construct the vertex, edge and label drawers
        vertex_drawer = self.vertex_drawer_factory(context, bbox, palette, layout)
        edge_drawer = self.edge_drawer_factory(context, palette)
        label_drawer = self.label_drawer_factory(context)

        # Construct the visual vertex/edge builders based on the specifications
        # provided by the vertex_drawer and the edge_drawer
        vertex_builder = vertex_drawer.VisualVertexBuilder(graph.vs, kwds)
        edge_builder = edge_drawer.VisualEdgeBuilder(graph.es, kwds)

        # Determine the order in which we will draw the vertices and edges
        vertex_order = self._determine_vertex_order(graph, kwds)
        edge_order = self._determine_edge_order(graph, kwds)

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

            # We will need a polygon drawer to draw the convex hulls
            polygon_drawer = CairoPolygonDrawer(context, bbox)

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
                context.set_source_rgba(color[0], color[1], color[2], color[3] * 0.25)
                polygon_drawer.draw_path(polygon, corner_radius=corner_radius)
                context.fill_preserve()
                context.set_source_rgba(*color)
                context.stroke()

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
        context.set_line_width(1)
        for vertex, visual_vertex, coords in vertex_coord_iter:
            drawer_method(visual_vertex, vertex, coords)

        # Decide whether the labels have to be wrapped
        wrap = kwds.get("wrap_labels")
        if wrap is None:
            wrap = Configuration.instance()["plotting.wrap_labels"]
        wrap = bool(wrap)

        # Construct the iterator that we will use to draw the vertex labels
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

            # Set the font family, size, color and text
            context.select_font_face(
                vertex.font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL
            )
            context.set_font_size(vertex.label_size)
            context.set_source_rgba(*vertex.label_color)
            label_drawer.text = vertex.label

            if vertex.label_dist:
                # Label is displaced from the center of the vertex.
                _, yb, w, h, _, _ = label_drawer.text_extents()
                w, h = w / 2.0, h / 2.0
                radius = vertex.label_dist * vertex.size / 2.0
                # First we find the reference point that is at distance `radius'
                # from the vertex in the direction given by `label_angle'.
                # Then we place the label in a way that the line connecting the
                # center of the bounding box of the label with the center of the
                # vertex goes through the reference point and the reference
                # point lies exactly on the bounding box of the vertex.
                alpha = vertex.label_angle % (2 * pi)
                cx = coords[0] + radius * cos(alpha)
                cy = coords[1] - radius * sin(alpha)
                # Now we have the reference point. We have to decide which side
                # of the label box will intersect with the line that connects
                # the center of the label with the center of the vertex.
                if w > 0:
                    beta = atan2(h, w) % (2 * pi)
                else:
                    beta = pi / 2.0
                gamma = pi - beta
                if alpha > 2 * pi - beta or alpha <= beta:
                    # Intersection at left edge of label
                    cx += w
                    cy -= tan(alpha) * w
                elif alpha > beta and alpha <= gamma:
                    # Intersection at bottom edge of label
                    try:
                        cx += h / tan(alpha)
                    except Exception:
                        pass  # tan(alpha) == inf
                    cy -= h
                elif alpha > gamma and alpha <= gamma + 2 * beta:
                    # Intersection at right edge of label
                    cx -= w
                    cy += tan(alpha) * w
                else:
                    # Intersection at top edge of label
                    try:
                        cx -= h / tan(alpha)
                    except Exception:
                        pass  # tan(alpha) == inf
                    cy += h
                # Draw the label
                label_drawer.draw_at(cx - w, cy - h - yb, wrap=wrap)
            else:
                # Label is exactly in the center of the vertex
                cx, cy = coords
                half_size = vertex.size / 2.0
                label_drawer.bbox = (
                    cx - half_size,
                    cy - half_size,
                    cx + half_size,
                    cy + half_size,
                )
                label_drawer.draw(wrap=wrap)

        # Construct the iterator that we will use to draw the edge labels
        es = graph.es
        if edge_order is None:
            # Default edge order
            edge_coord_iter = zip(es, edge_builder)
        else:
            # Specified edge order
            edge_coord_iter = ((es[i], edge_builder[i]) for i in edge_order)

        # Draw the edge labels
        for edge, visual_edge in edge_coord_iter:
            if visual_edge.label is None:
                continue

            # Set the font family, size, color and text
            context.select_font_face(
                visual_edge.font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL
            )
            context.set_font_size(visual_edge.label_size)
            context.set_source_rgba(*visual_edge.label_color)
            label_drawer.text = visual_edge.label

            # Ask the edge drawer to propose an anchor point for the label
            src, dest = edge.tuple
            src_vertex, dest_vertex = vertex_builder[src], vertex_builder[dest]
            (x, y), (halign, valign) = edge_drawer.get_label_position(
                edge, src_vertex, dest_vertex
            )

            # Measure the text
            _, yb, w, h, _, _ = label_drawer.text_extents()
            w /= 2.0
            h /= 2.0

            # Place the text relative to the edge
            if halign == TextAlignment.RIGHT:
                x -= w
            elif halign == TextAlignment.LEFT:
                x += w
            if valign == TextAlignment.BOTTOM:
                y -= h - yb / 2.0
            elif valign == TextAlignment.TOP:
                y += h

            # Draw the edge label
            label_drawer.halign = halign
            label_drawer.valign = valign
            label_drawer.bbox = (x - w, y - h, x + w, y + h)
            label_drawer.draw(wrap=wrap)


# TODO: deprecate
DefaultGraphDrawer = CairoGraphDrawer

#####################################################################


class UbiGraphDrawer(AbstractXMLRPCDrawer, AbstractGraphDrawer):
    """Graph drawer that draws a given graph on an UbiGraph display
    using the XML-RPC API of UbiGraph.

    The following vertex attributes are supported: C{color}, C{label},
    C{shape}, C{size}. See the Ubigraph documentation for supported shape
    names. Sizes are relative to the default Ubigraph size.

    The following edge attributes are supported: C{color}, C{label},
    C{width}. Edge widths are relative to the default Ubigraph width.

    All color specifications supported by igraph (e.g., color names,
    palette indices, RGB triplets, RGBA quadruplets, HTML format)
    are understood by the Ubigraph graph drawer.

    The drawer also has two attributes, C{vertex_defaults} and
    C{edge_defaults}. These are dictionaries that can be used to
    set default values for the vertex/edge attributes in Ubigraph.

    @deprecated: UbiGraph has not received updates since 2008 and is now not
        available for download (at least not from the official sources).
        The UbiGraph graph drawer will be removed from python-igraph in
        0.10.0.
    """

    def __init__(self, url="http://localhost:20738/RPC2"):
        """Constructs an UbiGraph drawer using the display at the given
        URL."""
        super(UbiGraphDrawer, self).__init__(url, "ubigraph")
        self.vertex_defaults = dict(color="#ff0000", shape="cube", size=1.0)
        self.edge_defaults = dict(color="#ffffff", width=1.0)

        warn(
            "UbiGraphDrawer is deprecated from python-igraph 0.9.4",
            DeprecationWarning
        )

    def draw(self, graph, *args, **kwds):
        """Draws the given graph on an UbiGraph display.

        @keyword clear: whether to clear the current UbiGraph display before
                        plotting. Default: C{True}."""
        display = self.service

        # Clear the display and set the default visual attributes
        if kwds.get("clear", True):
            display.clear()

            for k, v in self.vertex_defaults.items():
                display.set_vertex_style_attribute(0, k, str(v))
            for k, v in self.edge_defaults.items():
                display.set_edge_style_attribute(0, k, str(v))

        # Custom color converter function
        def color_conv(color):
            return color_to_html_format(color_name_to_rgb(color))

        # Construct the visual vertex/edge builders
        class VisualVertexBuilder(AttributeCollectorBase):
            """Collects some visual properties of a vertex for drawing"""

            _kwds_prefix = "vertex_"
            color = (str(self.vertex_defaults["color"]), color_conv)
            label = None
            shape = str(self.vertex_defaults["shape"])
            size = float(self.vertex_defaults["size"])

        class VisualEdgeBuilder(AttributeCollectorBase):
            """Collects some visual properties of an edge for drawing"""

            _kwds_prefix = "edge_"
            color = (str(self.edge_defaults["color"]), color_conv)
            label = None
            width = float(self.edge_defaults["width"])

        vertex_builder = VisualVertexBuilder(graph.vs, kwds)
        edge_builder = VisualEdgeBuilder(graph.es, kwds)

        # Add the vertices
        n = graph.vcount()
        new_vertex = display.new_vertex
        vertex_ids = [new_vertex() for _ in range(n)]

        # Add the edges
        new_edge = display.new_edge
        eids = [
            new_edge(vertex_ids[edge.source], vertex_ids[edge.target])
            for edge in graph.es
        ]

        # Add arrowheads if needed
        if graph.is_directed():
            display.set_edge_style_attribute(0, "arrow", "true")

        # Set the vertex attributes
        set_attr = display.set_vertex_attribute
        vertex_defaults = self.vertex_defaults
        for vertex_id, vertex in zip(vertex_ids, vertex_builder):
            if vertex.color != vertex_defaults["color"]:
                set_attr(vertex_id, "color", vertex.color)
            if vertex.label:
                set_attr(vertex_id, "label", str(vertex.label))
            if vertex.shape != vertex_defaults["shape"]:
                set_attr(vertex_id, "shape", vertex.shape)
            if vertex.size != vertex_defaults["size"]:
                set_attr(vertex_id, "size", str(vertex.size))

        # Set the edge attributes
        set_attr = display.set_edge_attribute
        edge_defaults = self.edge_defaults
        for edge_id, edge in zip(eids, edge_builder):
            if edge.color != edge_defaults["color"]:
                set_attr(edge_id, "color", edge.color)
            if edge.label:
                set_attr(edge_id, "label", edge.label)
            if edge.width != edge_defaults["width"]:
                set_attr(edge_id, "width", str(edge.width))


#####################################################################


class CytoscapeGraphDrawer(AbstractXMLRPCDrawer, AbstractGraphDrawer):
    """Graph drawer that sends/receives graphs to/from Cytoscape using
    CytoscapeRPC.

    This graph drawer cooperates with U{Cytoscape<http://www.cytoscape.org>}
    using U{CytoscapeRPC<http://wiki.nbic.nl/index.php/CytoscapeRPC>}.
    You need to install the CytoscapeRPC plugin first and start the
    XML-RPC server on a given port (port 9000 by default) from the
    appropriate Plugins submenu in Cytoscape.

    Graph, vertex and edge attributes are transferred to Cytoscape whenever
    possible (i.e. when a suitable mapping exists between a Python type
    and a Cytoscape type). If there is no suitable Cytoscape type for a
    Python type, the drawer will use a string attribute on the Cytoscape
    side and invoke C{str()} on the Python attributes.

    If an attribute to be created on the Cytoscape side already exists with
    a different type, an underscore will be appended to the attribute name
    to resolve the type conflict.

    You can use the C{network_id} attribute of this class to figure out the
    network ID of the last graph drawn with this drawer.
    """

    def __init__(self, url="http://localhost:9000/Cytoscape"):
        """Constructs a Cytoscape graph drawer using the XML-RPC interface
        of Cytoscape at the given URL."""
        super(CytoscapeGraphDrawer, self).__init__(url, "Cytoscape")
        self.network_id = None

    def draw(self, graph, name="Network from igraph", create_view=True, *args, **kwds):
        """Sends the given graph to Cytoscape as a new network.

        @param name: the name of the network in Cytoscape.
        @param create_view: whether to create a view for the network
          in Cytoscape.The default is C{True}.
        @keyword node_ids: specifies the identifiers of the nodes to
          be used in Cytoscape. This must either be the name of a
          vertex attribute or a list specifying the identifiers, one
          for each node in the graph. The default is C{None}, which
          simply uses the vertex index for each vertex."""
        from xmlrpc.client import Fault

        cy = self.service

        # Create the network
        if not create_view:
            try:
                network_id = cy.createNetwork(name, False)
            except Fault:
                warn(
                    "CytoscapeRPC too old, cannot create network without view."
                    " Consider upgrading CytoscapeRPC to use this feature."
                )
                network_id = cy.createNetwork(name)
        else:
            network_id = cy.createNetwork(name)
        self.network_id = network_id

        # Create the nodes
        if "node_ids" in kwds:
            node_ids = kwds["node_ids"]
            if isinstance(node_ids, str):
                node_ids = graph.vs[node_ids]
        else:
            node_ids = list(range(graph.vcount()))
        node_ids = [str(identifier) for identifier in node_ids]
        cy.createNodes(network_id, node_ids)

        # Create the edges
        edgelists = [[], []]
        for v1, v2 in graph.get_edgelist():
            edgelists[0].append(node_ids[v1])
            edgelists[1].append(node_ids[v2])
        edge_ids = cy.createEdges(
            network_id,
            edgelists[0],
            edgelists[1],
            ["unknown"] * graph.ecount(),
            [graph.is_directed()] * graph.ecount(),
            False,
        )

        if "layout" in kwds:
            # Calculate/get the layout of the graph
            layout = self.ensure_layout(kwds["layout"], graph)
            size = 100 * graph.vcount() ** 0.5
            layout.fit_into((size, size), keep_aspect_ratio=True)
            layout.translate(-size / 2.0, -size / 2.0)
            cy.setNodesPositions(network_id, node_ids, *list(zip(*list(layout))))
        else:
            # Ask Cytoscape to perform the default layout so the user can
            # at least see something in Cytoscape while the attributes are
            # being transferred
            cy.performDefaultLayout(network_id)

        # Send the network attributes
        attr_names = set(cy.getNetworkAttributeNames())
        for attr in graph.attributes():
            cy_type, value = self.infer_cytoscape_type([graph[attr]])
            value = value[0]
            if value is None:
                continue

            # Resolve type conflicts (if any)
            try:
                while (
                    attr in attr_names and cy.getNetworkAttributeType(attr) != cy_type
                ):
                    attr += "_"
            except Fault:
                # getNetworkAttributeType is not available in some older versions
                # so we simply pass here
                pass
            cy.addNetworkAttributes(attr, cy_type, {network_id: value})

        # Send the node attributes
        attr_names = set(cy.getNodeAttributeNames())
        for attr in graph.vertex_attributes():
            cy_type, values = self.infer_cytoscape_type(graph.vs[attr])
            values = dict(pair for pair in zip(node_ids, values) if pair[1] is not None)
            # Resolve type conflicts (if any)
            while attr in attr_names and cy.getNodeAttributeType(attr) != cy_type:
                attr += "_"
            # Send the attribute values
            cy.addNodeAttributes(attr, cy_type, values, True)

        # Send the edge attributes
        attr_names = set(cy.getEdgeAttributeNames())
        for attr in graph.edge_attributes():
            cy_type, values = self.infer_cytoscape_type(graph.es[attr])
            values = dict(pair for pair in zip(edge_ids, values) if pair[1] is not None)
            # Resolve type conflicts (if any)
            while attr in attr_names and cy.getEdgeAttributeType(attr) != cy_type:
                attr += "_"
            # Send the attribute values
            cy.addEdgeAttributes(attr, cy_type, values)

    def fetch(self, name=None, directed=False, keep_canonical_names=False):
        """Fetches the network with the given name from Cytoscape.

        When fetching networks from Cytoscape, the C{canonicalName} attributes
        of vertices and edges are not converted by default. Use the
        C{keep_canonical_names} parameter to retrieve these attributes as well.

        @param name: the name of the network in Cytoscape.
        @param directed: whether the network is directed.
        @param keep_canonical_names: whether to keep the C{canonicalName}
            vertex/edge attributes that are added automatically by Cytoscape
        @return: an appropriately constructed igraph L{Graph}."""
        from igraph import Graph

        cy = self.service

        # Check the version number. Anything older than 1.3 is bad.
        version = cy.version()
        if " " in version:
            version = version.split(" ")[0]
        version = tuple(map(int, version.split(".")[:2]))
        if version < (1, 3):
            raise NotImplementedError(
                "CytoscapeGraphDrawer requires " "Cytoscape-RPC 1.3 or newer"
            )

        # Find out the ID of the network we are interested in
        if name is None:
            network_id = cy.getNetworkID()
        else:
            network_id = [k for k, v in cy.getNetworkList().items() if v == name]
            if not network_id:
                raise ValueError("no such network: %r" % name)
            elif len(network_id) > 1:
                raise ValueError("more than one network exists with name: %r" % name)
            network_id = network_id[0]

        # Fetch the list of all the nodes and edges
        vertices = cy.getNodes(network_id)
        edges = cy.getEdges(network_id)
        n, m = len(vertices), len(edges)

        # Fetch the graph attributes
        graph_attrs = cy.getNetworkAttributes(network_id)

        # Fetch the vertex attributes
        vertex_attr_names = cy.getNodeAttributeNames()
        vertex_attrs = {}
        for attr_name in vertex_attr_names:
            if attr_name == "canonicalName" and not keep_canonical_names:
                continue
            has_attr = cy.nodesHaveAttribute(attr_name, vertices)
            filtered = [idx for idx, ok in enumerate(has_attr) if ok]
            values = cy.getNodesAttributes(
                attr_name, [name for name, ok in zip(vertices, has_attr) if ok]
            )
            attrs = [None] * n
            for idx, value in zip(filtered, values):
                attrs[idx] = value
            vertex_attrs[attr_name] = attrs

        # Fetch the edge attributes
        edge_attr_names = cy.getEdgeAttributeNames()
        edge_attrs = {}
        for attr_name in edge_attr_names:
            if attr_name == "canonicalName" and not keep_canonical_names:
                continue
            has_attr = cy.edgesHaveAttribute(attr_name, edges)
            filtered = [idx for idx, ok in enumerate(has_attr) if ok]
            values = cy.getEdgesAttributes(
                attr_name, [name for name, ok in zip(edges, has_attr) if ok]
            )
            attrs = [None] * m
            for idx, value in zip(filtered, values):
                attrs[idx] = value
            edge_attrs[attr_name] = attrs

        # Create a vertex name index
        vertex_name_index = dict((v, k) for k, v in enumerate(vertices))
        del vertices

        # Remap the edges list to numeric IDs
        edge_list = []
        for edge in edges:
            parts = edge.split()
            edge_list.append((vertex_name_index[parts[0]], vertex_name_index[parts[2]]))
        del edges

        return Graph(
            n,
            edge_list,
            directed=directed,
            graph_attrs=graph_attrs,
            vertex_attrs=vertex_attrs,
            edge_attrs=edge_attrs,
        )

    @staticmethod
    def infer_cytoscape_type(values):
        """Returns a Cytoscape type that can be used to represent all the
        values in `values` and an appropriately converted copy of `values` that
        is suitable for an XML-RPC call.  Note that the string type in
        Cytoscape is used as a catch-all type; if no other type fits, attribute
        values will be converted to string and then posted to Cytoscape.

        ``None`` entries are allowed in `values`, they will be ignored on the
        Cytoscape side.
        """
        types = [type(value) for value in values if value is not None]
        if all(t == bool for t in types):
            return "BOOLEAN", values
        if all(issubclass(t, (int, int)) for t in types):
            return "INTEGER", values
        if all(issubclass(t, float) for t in types):
            return "FLOATING", values
        return "STRING", [
            str(value) if not isinstance(value, str) else value for value in values
        ]


#####################################################################


class GephiGraphStreamingDrawer(AbstractGraphDrawer):
    """Graph drawer that sends a graph to a file-like object (e.g., socket, URL
    connection, file) using the Gephi graph streaming format.

    The Gephi graph streaming format is a simple JSON-based format that can be used
    to post mutations to a graph (i.e. node and edge additions, removals and updates)
    to a remote component. For instance, one can open up Gephi
    (U{http://www.gephi.org}), install the Gephi graph streaming plugin and then
    send a graph from igraph straight into the Gephi window by using
    C{GephiGraphStreamingDrawer} with the appropriate URL where Gephi is
    listening.

    The C{connection} property exposes the L{GephiConnection} that the drawer
    uses. The drawer also has a property called C{streamer} which exposes the underlying
    L{GephiGraphStreamer} that is responsible for generating the JSON objects,
    encoding them and writing them to a file-like object. If you want to customize
    the encoding process, this is the object where you can tweak things to your taste.
    """

    def __init__(self, conn=None, *args, **kwds):
        """Constructs a Gephi graph streaming drawer that will post graphs to the
        given Gephi connection. If C{conn} is C{None}, the remaining arguments of
        the constructor are forwarded intact to the constructor of
        L{GephiConnection} in order to create a connection. This means that any of
        the following are valid:

          - C{GephiGraphStreamingDrawer()} will construct a drawer that connects to
            workspace 0 of the local Gephi instance on port 8080.

          - C{GephiGraphStreamingDrawer(workspace=2)} will connect to workspace 2
            of the local Gephi instance on port 8080.

          - C{GephiGraphStreamingDrawer(port=1234)} will connect to workspace 0
            of the local Gephi instance on port 1234.

          - C{GephiGraphStreamingDrawer(host="remote", port=1234, workspace=7)}
            will connect to workspace 7 of the Gephi instance on host C{remote},
            port 1234.

          - C{GephiGraphStreamingDrawer(url="http://remote:1234/workspace7)} is
            the same as above, but with an explicit URL.
        """
        super(GephiGraphStreamingDrawer, self).__init__()

        from igraph.remote.gephi import GephiGraphStreamer, GephiConnection

        self.connection = conn or GephiConnection(*args, **kwds)
        self.streamer = GephiGraphStreamer()

    def draw(self, graph, *args, **kwds):
        """Draws (i.e. sends) the given graph to the destination of the drawer using
        the Gephi graph streaming API.

        The following keyword arguments are allowed:

            - ``encoder`` lets one specify an instance of ``json.JSONEncoder`` that
              will be used to encode the JSON objects.
        """
        self.streamer.post(graph, self.connection, encoder=kwds.get("encoder"))


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
            edge_drawer_factory=MatplotlibArrowEdgeDrawer,
            ):
        """Constructs the graph drawer and associates it with the mpl Axes


        @param ax: the matplotlib Axes to draw into.
        @param vertex_drawer_factory: a factory method that returns an
                        L{AbstractCairoVertexDrawer} instance bound to a
                        given Cairo context. The factory method must take
                        two parameters: the Axes and the palette to be
                        used for drawing colored vertices. The default
                        vertex drawer is L{MatplotlibVertexDrawer}.
        @param edge_drawer_factory: a factory method that returns an
                        L{AbstractEdgeDrawer} instance bound to a
                        given matplotlib Axes. The factory method must take
                        two parameters: the Axes and the palette
                        to be used for drawing colored edges. The default
                        edge drawer is L{MatplotlibArrowEdgeDrawer}.
                        Additional styles will be added in the future.
        """
        self.ax = ax
        self.vertex_drawer_factory = vertex_drawer_factory
        self.edge_drawer_factory = edge_drawer_factory

    def draw(self, graph, palette, *args, **kwds):
        # Deferred import to avoid a cycle in the import graph
        from igraph.clustering import VertexClustering, VertexCover

        # Some abbreviations for sake of simplicity
        directed = graph.is_directed()
        ax = self.ax

        # Calculate/get the layout of the graph
        layout = self.ensure_layout(kwds.get("layout", None), graph)

        # FIXME: deal with unnamed *args

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
                graph, attribute=None, default=default,
            )

        # Construct the vertex, edge and label drawers
        vertex_drawer = self.vertex_drawer_factory(
                ax, palette, layout,
                )
        edge_drawer = self.edge_drawer_factory(
                ax, palette)

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
                    'handles': [],
                    'labels': [],
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
                drawer = MatplotlibPolygonDrawer(ax, points=polygon)
                drawer.draw(
                        corner_radius=corner_radius,
                        facecolor=facecolor,
                        edgecolor=color,
                        )

                if kwds.get("legend", False):
                    legend_info['handles'].append(
                        plt.Rectangle(
                            (0, 0), 0, 0,
                            facecolor=facecolor,
                            edgecolor=color,
                        )
                    )
                    legend_info['labels'].append(str(color_id))

            if kwds.get("legend", False):
                ax.legend(
                    legend_info['handles'],
                    legend_info['labels'],
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

        # Draw the vertex labels
        labels = kwds.get("vertex_label", None)
        if labels is not None:
            vertex_label_iter = (
                (labels[i], vertex_builder[i], layout[i]) for i in range(graph.vcount())
                )
            for label, visual_vertex, coords in vertex_label_iter:

                label_size = kwds.get(
                    "vertex_label_size",
                    visual_vertex.label_size,
                )

                ax.text(
                    *coords,
                    label,
                    fontsize=label_size,
                    # TODO: alignment, overlap, offset, etc.
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
                    edge, src_vertex, dest_vertex,
                )

                ax.text(
                        x, y,
                        label,
                        fontsize=visual_edge.label_size,
                        color=visual_edge.label_color,
                        ha=halign, va=valign,
                        # TODO: offset, etc.
                        )

        # Despine
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        # Remove axis ticks
        ax.set_xticks([])
        ax.set_yticks([])

        ax.autoscale_view()
