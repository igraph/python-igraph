from math import pi

from igraph.drawing.baseclasses import AbstractDrawer
from igraph.drawing.utils import BoundingBox

__all__ = ("AbstractCairoDrawer", )


class AbstractCairoDrawer(AbstractDrawer):
    """Abstract class that serves as a base class for anything that
    draws on a Cairo context within a given bounding box.

    A subclass of L{AbstractCairoDrawer} is guaranteed to have an
    attribute named C{context} that represents the Cairo context
    to draw on, and an attribute named C{bbox} for the L{BoundingBox}
    of the drawing area.
    """

    def __init__(self, context, bbox):
        """Constructs the drawer and associates it to the given
        Cairo context and the given L{BoundingBox}.

        @param context: the context on which we will draw
        @param bbox:    the bounding box within which we will draw.
                        Can be anything accepted by the constructor
                        of L{BoundingBox} (i.e., a 2-tuple, a 4-tuple
                        or a L{BoundingBox} object).
        """
        self.context = context
        self._bbox = None
        self.bbox = bbox

    @property
    def bbox(self):
        """The bounding box of the drawing area where this drawer will
        draw."""
        return self._bbox

    @bbox.setter
    def bbox(self, bbox):
        """Sets the bounding box of the drawing area where this drawer
        will draw."""
        if not isinstance(bbox, BoundingBox):
            self._bbox = BoundingBox(bbox)
        else:
            self._bbox = bbox

    def _mark_point(self, x, y, color=0, size=4):
        """Marks the given point with a small circle on the canvas.
        Used primarily for debugging purposes.

        @param x: the X coordinate of the point to mark
        @param y: the Y coordinate of the point to mark
        @param color: the color of the marker. It can be a
          3-tuple (RGB components, alpha=0.5), a 4-tuple
          (RGBA components) or an index where zero means red, 1 means
          green, 2 means blue and so on.
        @param size: the diameter of the marker.
        """
        if isinstance(color, int):
            colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (0, 1, 1), (1, 0, 1)]
            color = colors[color % len(colors)]
        if len(color) == 3:
            color += (0.5,)

        ctx = self.context
        ctx.save()
        ctx.set_source_rgba(*color)
        ctx.arc(x, y, size / 2.0, 0, 2 * pi)
        ctx.fill()
        ctx.restore()
