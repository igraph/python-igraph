# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""
Shape drawing classes for igraph

Vertex shapes in igraph are usually referred to by short names like
C{"rect"} or C{"circle"}. This module contains the classes that
implement the actual drawing routines for these shapes, and a
resolver class that determines the appropriate shape drawer class
given the short name.

Classes that are derived from L{ShapeDrawer} in this module are
automatically registered by L{ShapeDrawerDirectory}. If you
implement a custom shape drawer, you must register it in
L{ShapeDrawerDirectory} manually if you wish to refer to it by a
name in the C{shape} attribute of vertices.
"""


__all__ = ("ShapeDrawerDirectory",)

from math import atan2, copysign, cos, pi, sin
import sys

from igraph.drawing.baseclasses import AbstractCairoDrawer
from igraph.drawing.matplotlib.utils import find_matplotlib
from igraph.drawing.utils import Point
from igraph.utils import consecutive_pairs

mpl, plt = find_matplotlib()


class ShapeDrawer:
    """Static class, the ancestor of all vertex shape drawer classes.

    Custom shapes must implement at least the C{draw_path} method of the class.
    The method I{must not} stroke or fill, it should just set up the current
    Cairo path appropriately."""

    @staticmethod
    def draw_path(ctx, center_x, center_y, width, height=None, **kwargs):
        """Draws the path of the shape on the given Cairo context, without
        stroking or filling it.

        This method must be overridden in derived classes implementing custom shapes
        and declared as a static method using C{staticmethod(...)}.

        @param ctx: the context to draw on
        @param center_x: the X coordinate of the center of the object
        @param center_y: the Y coordinate of the center of the object
        @param width: the width of the object
        @param height: the height of the object. If C{None}, equals to the width.
        """
        raise NotImplementedError("abstract class")

    @staticmethod
    def intersection_point(center_x, center_y, source_x, source_y, width, height=None):
        """Determines where the shape centered at (center_x, center_y)
        intersects with a line drawn from (source_x, source_y) to
        (center_x, center_y).

        Can be overridden in derived classes. Must always be defined as a static
        method using C{staticmethod(...)}

        @param width: the width of the shape
        @param height: the height of the shape. If C{None}, defaults to the width
        @return: the intersection point (the closest to (source_x, source_y) if
            there are more than one) or (center_x, center_y) if there is no
            intersection
        """
        return center_x, center_y


class NullDrawer(ShapeDrawer):
    """Static drawer class which draws nothing.

    This class is used for graph vertices with unknown shapes"""

    names = ["null", "none", "empty", "hidden", ""]

    @staticmethod
    def draw_path(ctx, center_x, center_y, width, height=None):
        """Draws nothing."""
        pass


class RectangleDrawer(ShapeDrawer):
    """Static class which draws rectangular vertices"""

    names = "rectangle rect rectangular square box s"

    @staticmethod
    def draw_path(ctx, center_x, center_y, width, height=None, **kwargs):
        """Draws a rectangle-shaped path on the Cairo context without stroking
        or filling it.
        @see: ShapeDrawer.draw_path"""
        height = height or width
        if isinstance(ctx, plt.Axes):
            return mpl.patches.Rectangle(
                (center_x - width / 2, center_y - height / 2), width, height, **kwargs
            )
        else:
            ctx.rectangle(center_x - width / 2, center_y - height / 2, width, height)

    @staticmethod
    def intersection_point(center_x, center_y, source_x, source_y, width, height=None):
        """Determines where the rectangle centered at (center_x, center_y)
        having the given width and height intersects with a line drawn from
        (source_x, source_y) to (center_x, center_y).

        @see: ShapeDrawer.intersection_point"""
        height = height or width
        delta_x, delta_y = center_x - source_x, center_y - source_y

        if delta_x == 0 and delta_y == 0:
            return center_x, center_y

        if delta_y > 0 and delta_x <= delta_y and delta_x >= -delta_y:
            # this is the top edge
            ry = center_y - height / 2
            ratio = (height / 2) / delta_y
            return center_x - ratio * delta_x, ry

        if delta_y < 0 and delta_x <= -delta_y and delta_x >= delta_y:
            # this is the bottom edge
            ry = center_y + height / 2
            ratio = (height / 2) / -delta_y
            return center_x - ratio * delta_x, ry

        if delta_x > 0 and delta_y <= delta_x and delta_y >= -delta_x:
            # this is the left edge
            rx = center_x - width / 2
            ratio = (width / 2) / delta_x
            return rx, center_y - ratio * delta_y

        if delta_x < 0 and delta_y <= -delta_x and delta_y >= delta_x:
            # this is the right edge
            rx = center_x + width / 2
            ratio = (width / 2) / -delta_x
            return rx, center_y - ratio * delta_y

        if delta_x == 0:
            if delta_y > 0:
                return center_x, center_y - height / 2
            return center_x, center_y + height / 2

        if delta_y == 0:
            if delta_x > 0:
                return center_x - width / 2, center_y
            return center_x + width / 2, center_y


class CircleDrawer(ShapeDrawer):
    """Static class which draws circular vertices"""

    names = "circle circular o"

    @staticmethod
    def draw_path(ctx, center_x, center_y, width, height=None, **kwargs):
        """Draws a circular path on the Cairo context without stroking or
        filling it.

        Height is ignored, it is the width that determines the diameter of the circle.

        @see: ShapeDrawer.draw_path"""
        if isinstance(ctx, plt.Axes):
            return mpl.patches.Circle((center_x, center_y), width / 2, **kwargs)
        else:
            ctx.arc(center_x, center_y, width / 2, 0, 2 * pi)

    @staticmethod
    def intersection_point(center_x, center_y, source_x, source_y, width, height=None):
        """Determines where the circle centered at (center_x, center_y)
        intersects with a line drawn from (source_x, source_y) to
        (center_x, center_y).

        @see: ShapeDrawer.intersection_point"""
        height = height or width
        angle = atan2(center_y - source_y, center_x - source_x)
        return center_x - width / 2 * cos(angle), center_y - height / 2 * sin(angle)


class UpTriangleDrawer(ShapeDrawer):
    """Static class which draws upright triangles"""

    names = "triangle triangle-up up-triangle arrow arrow-up up-arrow ^"

    @staticmethod
    def draw_path(ctx, center_x, center_y, width, height=None, **kwargs):
        """Draws an upright triangle on the Cairo context without stroking or
        filling it.

        @see: ShapeDrawer.draw_path"""
        height = height or width
        if isinstance(ctx, plt.Axes):
            vertices = [
                [center_x - 0.5 * width, center_y - 0.333 * height],
                [center_x + 0.5 * width, center_y - 0.333 * height],
                [center_x, center_x + 0.667 * height],
            ]
            return mpl.patches.Polygon(vertices, closed=True, **kwargs)
        else:
            ctx.move_to(center_x - width / 2, center_y + height / 2)
            ctx.line_to(center_x, center_y - height / 2)
            ctx.line_to(center_x + width / 2, center_y + height / 2)
            ctx.close_path()

    @staticmethod
    def intersection_point(center_x, center_y, source_x, source_y, width, height=None):
        """Determines where the triangle centered at (center_x, center_y)
        intersects with a line drawn from (source_x, source_y) to
        (center_x, center_y).

        @see: ShapeDrawer.intersection_point"""
        # TODO: finish it properly
        height = height or width
        return center_x, center_y


class DownTriangleDrawer(ShapeDrawer):
    """Static class which draws triangles pointing down"""

    names = "down-triangle triangle-down arrow-down down-arrow v"

    @staticmethod
    def draw_path(ctx, center_x, center_y, width, height=None, **kwargs):
        """Draws a triangle on the Cairo context without stroking or
        filling it.

        @see: ShapeDrawer.draw_path"""
        height = height or width
        if isinstance(ctx, plt.Axes):
            vertices = [
                [center_x - 0.5 * width, center_y + 0.333 * height],
                [center_x + 0.5 * width, center_y + 0.333 * height],
                [center_x, center_y - 0.667 * height],
            ]
            return mpl.patches.Polygon(vertices, closed=True, **kwargs)

        else:
            ctx.move_to(center_x - width / 2, center_y - height / 2)
            ctx.line_to(center_x, center_y + height / 2)
            ctx.line_to(center_x + width / 2, center_y - height / 2)
            ctx.close_path()

    @staticmethod
    def intersection_point(center_x, center_y, source_x, source_y, width, height=None):
        """Determines where the triangle centered at (center_x, center_y)
        intersects with a line drawn from (source_x, source_y) to
        (center_x, center_y).

        @see: ShapeDrawer.intersection_point"""
        # TODO: finish it properly
        height = height or width
        return center_x, center_y


class DiamondDrawer(ShapeDrawer):
    """Static class which draws diamonds (i.e. rhombuses)"""

    names = "diamond rhombus d"

    @staticmethod
    def draw_path(ctx, center_x, center_y, width, height=None, **kwargs):
        """Draws a rhombus on the Cairo context without stroking or
        filling it.

        @see: ShapeDrawer.draw_path"""
        height = height or width
        if isinstance(ctx, plt.Axes):
            vertices = [
                [center_x - 0.5 * width, center_y],
                [center_x, center_y - 0.5 * height],
                [center_x + 0.5 * width, center_y],
                [center_x, center_y + 0.5 * height],
            ]
            return mpl.patches.Polygon(vertices, closed=True, **kwargs)
        else:
            ctx.move_to(center_x - width / 2, center_y)
            ctx.line_to(center_x, center_y + height / 2)
            ctx.line_to(center_x + width / 2, center_y)
            ctx.line_to(center_x, center_y - height / 2)
            ctx.close_path()

    @staticmethod
    def intersection_point(center_x, center_y, source_x, source_y, width, height=None):
        """Determines where the rhombus centered at (center_x, center_y)
        intersects with a line drawn from (source_x, source_y) to
        (center_x, center_y).

        @see: ShapeDrawer.intersection_point"""
        height = height or width

        if height == 0 and width == 0:
            return center_x, center_y

        delta_x, delta_y = source_x - center_x, source_y - center_y

        # Treat edge case when delta_x = 0
        if delta_x == 0:
            if delta_y == 0:
                return center_x, center_y
            else:
                return center_x, center_y + copysign(height / 2, delta_y)

        width = copysign(width, delta_x)
        height = copysign(height, delta_y)

        f = height / (height + width * delta_y / delta_x)
        return center_x + f * width / 2, center_y + (1 - f) * height / 2


#####################################################################


class AbstractPolygonDrawer:
    """Abstract class that is used to draw polygons"""

    @staticmethod
    def _round_corners(points, corner_radius):
        points = [Point(*point) for point in points]
        side_vecs = [v - u for u, v in consecutive_pairs(points, circular=True)]
        half_side_lengths = [side.length() / 2 for side in side_vecs]
        corner_radii = [corner_radius] * len(points)
        for idx in range(len(corner_radii)):
            prev_idx = -1 if idx == 0 else idx - 1
            radii = [corner_radius, half_side_lengths[prev_idx], half_side_lengths[idx]]
            corner_radii[idx] = min(radii)
        return corner_radii


class CairoPolygonDrawer(AbstractCairoDrawer, AbstractPolygonDrawer):
    """Class that is used to draw polygons in Cairo.

    The corner points of the polygon can be set by the C{points}
    property of the drawer, or passed at construction time. Most
    drawing methods in this class also have an extra C{points}
    argument that can be used to override the set of points in the
    C{points} property."""

    def __init__(self, context, bbox=(1, 1), points=[]):
        """Constructs a new polygon drawer that draws on the given
        Cairo context.

        @param  context: the Cairo context to draw on
        @param  bbox:    ignored, leave it at its default value
        @param  points:  the list of corner points
        """
        super().__init__(context, bbox)
        self.points = points

    def draw_path(self, points=None, corner_radius=0):
        """Sets up a Cairo path for the outline of a polygon on the given
        Cairo context.

        @param points: the coordinates of the corners of the polygon,
          in clockwise or counter-clockwise order, or C{None} if we are
          about to use the C{points} property of the class.
        @param corner_radius: if zero, an ordinary polygon will be drawn.
          If positive, the corners of the polygon will be rounded with
          the given radius.
        """
        if points is None:
            points = self.points

        self.context.new_path()

        if len(points) < 2:
            # Well, a polygon must have at least two corner points
            return

        ctx = self.context
        if corner_radius <= 0:
            # No rounded corners, this is simple
            ctx.move_to(*points[-1])
            for point in points:
                ctx.line_to(*point)
            return

        # Rounded corners. First, we will take each side of the
        # polygon and find what the corner radius should be on
        # each corner. If the side is longer than 2r (where r is
        # equal to corner_radius), the radius allowed by that side
        # is r; if the side is shorter, the radius is the length
        # of the side / 2. For each corner, the final corner radius
        # is the smaller of the radii on the two sides adjacent to
        # the corner.
        corner_radii = self._round_corners(points, corner_radius)

        # Okay, move to the last corner, adjusted by corner_radii[-1]
        # towards the first corner
        ctx.move_to(*(points[-1].towards(points[0], corner_radii[-1])))
        # Now, for each point in points, draw a line towards the
        # corner, stopping before it in a distance of corner_radii[idx],
        # then draw the corner
        u = points[-1]
        for idx, (v, w) in enumerate(consecutive_pairs(points, True)):
            radius = corner_radii[idx]
            ctx.line_to(*v.towards(u, radius))
            aux1 = v.towards(u, radius / 2)
            aux2 = v.towards(w, radius / 2)
            ctx.curve_to(
                aux1.x, aux1.y, aux2.x, aux2.y, *v.towards(w, corner_radii[idx])
            )
            u = v

    def draw(self, points=None):
        """Draws the polygon using the current stroke of the Cairo context.

        @param points: the coordinates of the corners of the polygon,
          in clockwise or counter-clockwise order, or C{None} if we are
          about to use the C{points} property of the class.
        """
        self.draw_path(points)
        self.context.stroke()


# TODO: deprecate
PolygonDrawer = CairoPolygonDrawer


class MatplotlibPolygonDrawer(AbstractPolygonDrawer):
    """Class that is used to draw polygons in matplotlib.

    The corner points of the polygon can be set by the C{points}
    property of the drawer, or passed at construction time. Most
    drawing methods in this class also have an extra C{points}
    argument that can be used to override the set of points in the
    C{points} property."""

    def __init__(self, ax, points=[]):
        """Constructs a new polygon drawer that draws on the given
        Cairo context.

        @param  ax: the matplotlib Axes to draw on
        @param  points:  the list of corner points
        """
        self.context = ax
        self.points = points

    def draw(self, points=None, corner_radius=0, **kwds):
        """Sets up a mpl.path.Path for the outline of a polygon in matplotlib.

        @param points: the coordinates of the corners of the polygon,
          in clockwise or counter-clockwise order, or C{None} if we are
          about to use the C{points} property of the class.
        @param corner_radius: if zero, an ordinary polygon will be drawn.
          If positive, the corners of the polygon will be rounded with
          the given radius.
        """
        if points is None:
            points = self.points

        if len(points) < 2:
            # Well, a polygon must have at least two corner points
            return

        ax = self.context
        if corner_radius <= 0:
            # No rounded corners, this is simple
            stroke = mpl.patches.Polygon(points, **kwds)
            ax.add_patch(stroke)

        # Rounded corners. First, we will take each side of the
        # polygon and find what the corner radius should be on
        # each corner. If the side is longer than 2r (where r is
        # equal to corner_radius), the radius allowed by that side
        # is r; if the side is shorter, the radius is the length
        # of the side / 2. For each corner, the final corner radius
        # is the smaller of the radii on the two sides adjacent to
        # the corner.
        corner_radii = self._round_corners(points, corner_radius)

        # Okay, move to the last corner, adjusted by corner_radii[-1]
        # towards the first corner
        path = []
        codes = []
        path.append((points[-1].towards(points[0], corner_radii[-1])))
        codes.append(mpl.path.Path.MOVETO)

        # Now, for each point in points, draw a line towards the
        # corner, stopping before it in a distance of corner_radii[idx],
        # then draw the corner
        u = points[-1]
        for idx, (v, w) in enumerate(consecutive_pairs(points, True)):
            radius = corner_radii[idx]
            path.append(v.towards(u, radius))
            codes.append(mpl.path.Path.LINETO)

            aux1 = v.towards(u, radius / 2)
            aux2 = v.towards(w, radius / 2)

            path.append(aux1)
            path.append(aux2)
            path.append(v.towards(w, corner_radii[idx]))
            codes.extend([mpl.path.Path.CURVE4] * 3)
            u = v

        stroke = mpl.patches.PathPatch(
            mpl.path.Path(path, codes=codes, closed=True),
            **kwds,
        )
        ax.add_patch(stroke)


#####################################################################


class ShapeDrawerDirectory:
    """Static class that resolves shape names to their corresponding
    shape drawer classes.

    Classes that are derived from L{ShapeDrawer} in this module are
    automatically registered by L{ShapeDrawerDirectory} when the module
    is loaded for the first time.
    """

    known_shapes = {}

    @classmethod
    def register(cls, drawer_class):
        """Registers the given shape drawer class under the given names.

        @param drawer_class: the shape drawer class to be registered
        """
        names = drawer_class.names
        if isinstance(names, str):
            names = names.split()

        for name in names:
            cls.known_shapes[name] = drawer_class

    @classmethod
    def register_namespace(cls, namespace):
        """Registers all L{ShapeDrawer} classes in the given namespace

        @param namespace: a Python dict mapping names to Python objects."""
        for name, value in namespace.items():
            if name.startswith("__"):
                continue
            if isinstance(value, type):
                if issubclass(value, ShapeDrawer) and value != ShapeDrawer:
                    cls.register(value)

    @classmethod
    def resolve(cls, shape):
        """Given a shape name, returns the corresponding shape drawer class

        @param shape: the name of the shape
        @return: the corresponding shape drawer class

        @raise ValueError: if the shape is unknown
        """
        try:
            return cls.known_shapes[shape]
        except KeyError:
            raise ValueError("unknown shape: %s" % shape)

    @classmethod
    def resolve_default(cls, shape, default=NullDrawer):
        """Given a shape name, returns the corresponding shape drawer class
        or the given default shape drawer if the shape name is unknown.

        @param shape: the name of the shape
        @param default: the default shape drawer to return when the shape
          is unknown
        @return: the shape drawer class corresponding to the given name or
          the default shape drawer class if the name is unknown
        """
        return cls.known_shapes.get(shape, default)


ShapeDrawerDirectory.register_namespace(sys.modules[__name__].__dict__)
