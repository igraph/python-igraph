"""
Drawing routines to draw the vertices of graphs.

This module provides implementations of vertex drawers, i.e. drawers that the
default graph drawer will use to draw vertices.
"""

from igraph.drawing.baseclasses import AbstractDrawer, AbstractCairoDrawer
from igraph.drawing.metamagic import AttributeCollectorBase
from igraph.drawing.shapes import ShapeDrawerDirectory
from igraph.drawing.utils import find_matplotlib
from math import pi

__all__ = (
    "AbstractVertexDrawer", "AbstractCairoVertexDrawer", "CairoVertexDrawer",
    "MatplotlibVertexDrawer",
    "DefaultVertexDrawer",  # TODO: deprecate
    )

mpl, plt = find_matplotlib()


class AbstractVertexDrawer(AbstractDrawer):
    """Abstract vertex drawer object from which all concrete vertex drawer
    implementations are derived."""

    def __init__(self, palette, layout):
        """Constructs the vertex drawer and associates it to the given
        palette.

        @param palette: the palette that can be used to map integer
                        color indices to colors when drawing vertices
        @param layout:  the layout of the vertices in the graph being drawn
        """
        self.layout = layout
        self.palette = palette

    def draw(self, visual_vertex, vertex, coords):
        """Draws the given vertex.

        @param visual_vertex: object specifying the visual properties of the
            vertex. Its structure is defined by the VisualVertexBuilder of the
            L{DefaultGraphDrawer}; see its source code.
        @param vertex: the raw igraph vertex being drawn
        @param coords: the X and Y coordinates of the vertex as specified by the
            layout algorithm, scaled into the bounding box.
        """
        raise NotImplementedError("abstract class")


class AbstractCairoVertexDrawer(AbstractVertexDrawer, AbstractCairoDrawer):
    """Abstract base class for vertex drawers that draw on a Cairo canvas."""

    def __init__(self, context, bbox, palette, layout):
        """Constructs the vertex drawer and associates it to the given
        Cairo context and the given L{BoundingBox}.

        @param context: the context on which we will draw
        @param bbox:    the bounding box within which we will draw.
                        Can be anything accepted by the constructor
                        of L{BoundingBox} (i.e., a 2-tuple, a 4-tuple
                        or a L{BoundingBox} object).
        @param palette: the palette that can be used to map integer
                        color indices to colors when drawing vertices
        @param layout:  the layout of the vertices in the graph being drawn
        """
        AbstractCairoDrawer.__init__(self, context, bbox)
        AbstractVertexDrawer.__init__(self, palette, layout)


class CairoVertexDrawer(AbstractCairoVertexDrawer):
    """The default vertex drawer implementation of igraph."""

    def __init__(self, context, bbox, palette, layout):
        AbstractCairoVertexDrawer.__init__(self, context, bbox, palette, layout)
        self.VisualVertexBuilder = self._construct_visual_vertex_builder()

    def _construct_visual_vertex_builder(self):
        class VisualVertexBuilder(AttributeCollectorBase):
            """Collects some visual properties of a vertex for drawing"""

            _kwds_prefix = "vertex_"
            color = ("red", self.palette.get)
            frame_color = ("black", self.palette.get)
            frame_width = 1.0
            label = None
            label_angle = -pi / 2
            label_dist = 0.0
            label_color = ("black", self.palette.get)
            font = "sans-serif"
            label_size = 14.0
            position = dict(func=self.layout.__getitem__)
            shape = ("circle", ShapeDrawerDirectory.resolve_default)
            size = 20.0
            width = None
            height = None

        return VisualVertexBuilder

    def draw(self, visual_vertex, vertex, coords):
        context = self.context

        width = (
            visual_vertex.width
            if visual_vertex.width is not None
            else visual_vertex.size
        )
        height = (
            visual_vertex.height
            if visual_vertex.height is not None
            else visual_vertex.size
        )

        visual_vertex.shape.draw_path(context, coords[0], coords[1], width, height)
        context.set_source_rgba(*visual_vertex.color)
        context.fill_preserve()
        context.set_source_rgba(*visual_vertex.frame_color)
        context.set_line_width(visual_vertex.frame_width)
        context.stroke()


# TODO: Deprecate
DefaultVertexDrawer = CairoVertexDrawer


class MatplotlibVertexDrawer(AbstractVertexDrawer):
    def __init__(self, ax, palette, layout):
        self.context = ax
        AbstractVertexDrawer.__init__(self, palette, layout)
        self.VisualVertexBuilder = self._construct_visual_vertex_builder()

    def _construct_visual_vertex_builder(self):
        class VisualVertexBuilder(AttributeCollectorBase):
            """Collects some visual properties of a vertex for drawing"""

            _kwds_prefix = "vertex_"
            color = ("red", self.palette.get)
            frame_color = ("black", self.palette.get)
            frame_width = 1.0
            label = None
            label_angle = -pi / 2
            label_dist = 0.0
            label_color = ("black", self.palette.get)
            font = "sans-serif"
            label_size = 12.0
            # FIXME? mpl.rcParams["font.size"])
            position = dict(func=self.layout.__getitem__)
            shape = ("circle", lambda x: x)
            size = 0.2
            width = None
            height = None
            zorder = 2

        return VisualVertexBuilder

    @staticmethod
    def construct_patch(shape, xy, width, height=0, **kwargs):
        if shape in ('circle', 'o'):
            return mpl.patches.Circle(xy, width / 2, **kwargs)
        elif shape in ('ellipse', 'e'):
            return mpl.patches.Ellipse(xy, width / 2, height / 2, **kwargs)
        elif shape in ('square', 's'):
            return mpl.patches.Rectangle(xy, width, height, **kwargs)
        elif shape in ('triangle-down', 'v'):
            vertices = [
                [xy[0] - 0.5 * width, xy[1] + 0.333 * height],
                [xy[0] + 0.5 * width, xy[1] + 0.333 * height],
                [xy[0], xy[1] - 0.667 * height],
            ]
            return mpl.patches.Polygon(vertices, closed=True, **kwargs)
        elif shape in ('triangle-up', '^'):
            vertices = [
                [xy[0] - 0.5 * width, xy[1] - 0.333 * height],
                [xy[0] + 0.5 * width, xy[1] - 0.333 * height],
                [xy[0], xy[1] + 0.667 * height],
            ]
            return mpl.patches.Polygon(vertices, closed=True, **kwargs)
        elif shape in ('diamond', 'd',):
            vertices = [
                [xy[0] - 0.5 * width, xy[1]],
                [xy[0], xy[1] - 0.5 * height],
                [xy[0] + 0.5 * width, xy[1]],
                [xy[0], xy[1] + 0.5 * height],
            ]
            return mpl.patches.Polygon(vertices, closed=True, **kwargs)

    def draw(self, visual_vertex, vertex, coords):
        ax = self.context

        width = (
            visual_vertex.width
            if visual_vertex.width is not None
            else visual_vertex.size
        )
        height = (
            visual_vertex.height
            if visual_vertex.height is not None
            else visual_vertex.size
        )

        stroke = self.construct_patch(
            visual_vertex.shape,
            coords, width, height,
            facecolor=visual_vertex.color,
            edgecolor=visual_vertex.frame_color,
            linewidth=visual_vertex.frame_width,
            zorder=visual_vertex.zorder,
            )
        ax.add_patch(stroke)
