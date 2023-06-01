"""Drawers for various edge styles in Matplotlib graph plots."""

from math import atan2, cos, pi, sin, sqrt
from copy import deepcopy

from igraph.drawing.baseclasses import AbstractEdgeDrawer
from igraph.drawing.metamagic import AttributeCollectorBase
from igraph.drawing.matplotlib.utils import find_matplotlib
from igraph.drawing.utils import (
    euclidean_distance,
    get_bezier_control_points_for_curved_edge,
    intersect_bezier_curve_and_circle,
    FakeModule,
)

__all__ = ("MatplotlibEdgeDrawer", "EdgeCollection")

mpl, plt = find_matplotlib()
try:
    PatchCollection = mpl.collections.PatchCollection
except AttributeError:
    PatchCollection = FakeModule


class MatplotlibEdgeDrawer(AbstractEdgeDrawer):
    """Matplotlib-specific abstract edge drawer object."""

    def __init__(self, context, palette):
        """Constructs the edge drawer.

        @param context: a Matplotlib axes object on which the edges will be
            drawn.
        @param palette: the palette that can be used to map integer color
            indices to colors when drawing edges
        """
        self.context = context
        self.palette = palette
        self.VisualEdgeBuilder = self._construct_visual_edge_builder()

    def _construct_visual_edge_builder(self):
        """Construct the visual edge builder that will collect the visual
        attributes of an edge when it is being drawn."""

        class VisualEdgeBuilder(AttributeCollectorBase):
            """Builder that collects some visual properties of an edge for
            drawing"""

            _kwds_prefix = "edge_"
            arrow_size = 15
            arrow_width = 15
            color = ("#444", self.palette.get)
            curved = (0.0, self._curvature_to_float)
            label = None
            label_color = ("black", self.palette.get)
            label_size = 12.0
            font = "sans-serif"
            width = 2.0
            background = None
            align_label = False
            zorder = 1

        return VisualEdgeBuilder

    def draw_directed_edge(self, edge, src_vertex, dest_vertex):
        if src_vertex == dest_vertex:
            return self.draw_loop_edge(edge, src_vertex)

        ax = self.context
        (x1, y1), (x2, y2) = src_vertex.position, dest_vertex.position
        (x_src, y_src), (x_dest, y_dest) = src_vertex.position, dest_vertex.position

        # Draw the edge
        path = {"vertices": [], "codes": []}
        path["vertices"].append([x1, y1])
        path["codes"].append("MOVETO")

        if edge.curved:
            # Calculate the curve
            aux1, aux2 = get_bezier_control_points_for_curved_edge(x1, y1, x2, y2, edge.curved)

            # Coordinates of the control points of the Bezier curve
            xc1, yc1 = aux1
            xc2, yc2 = aux2

            # Determine where the edge intersects the circumference of the
            # vertex shape: Tip of the arrow
            ## FIXME
            #x2, y2 = intersect_bezier_curve_and_circle(
            #    x_src, y_src, xc1, yc1, xc2, yc2, x_dest, y_dest, dest_vertex.size / 2.0
            #)
            x2, y2 = x_dest, y_dest

            # Calculate the arrow head coordinates
            angle = atan2(y_dest - y2, x_dest - x2)  # navid
            arrow_size = 15.0 * edge.arrow_size
            arrow_width = 10.0 / edge.arrow_width
            aux_points = [
                (
                    x2 - arrow_size * cos(angle - pi / arrow_width),
                    y2 - arrow_size * sin(angle - pi / arrow_width),
                ),
                (
                    x2 - arrow_size * cos(angle + pi / arrow_width),
                    y2 - arrow_size * sin(angle + pi / arrow_width),
                ),
            ]

            # Midpoint of the base of the arrow triangle
            x_arrow_mid, y_arrow_mid = (aux_points[0][0] + aux_points[1][0]) / 2.0, (
                aux_points[0][1] + aux_points[1][1]
            ) / 2.0

            # Vector representing the base of the arrow triangle
            x_arrow_base_vec, y_arrow_base_vec = (
                aux_points[0][0] - aux_points[1][0]
            ), (aux_points[0][1] - aux_points[1][1])

            # Recalculate the curve such that it lands on the base of the arrow triangle
            aux1, aux2 = get_bezier_control_points_for_curved_edge(x_src, y_src, x_arrow_mid, y_arrow_mid, edge.curved)

            # Offset the second control point (aux2) such that it falls precisely
            # on the normal to the arrow base vector. Strictly speaking,
            # offset_length is the offset length divided by the length of the
            # arrow base vector.
            offset_length = (x_arrow_mid - aux2[0]) * x_arrow_base_vec + (
                y_arrow_mid - aux2[1]
            ) * y_arrow_base_vec
            offset_length /= (
                euclidean_distance(0, 0, x_arrow_base_vec, y_arrow_base_vec) ** 2
            )

            aux2 = (
                aux2[0] + x_arrow_base_vec * offset_length,
                aux2[1] + y_arrow_base_vec * offset_length,
            )

            # Draw the curve from the first vertex to the midpoint of the base
            # of the arrow head
            path["vertices"].append(aux1)
            path["vertices"].append(aux2)
            path["vertices"].append([x_arrow_mid, y_arrow_mid])
            path["codes"].extend(["CURVE4"] * 3)

        else:
            path["vertices"].append(dest_vertex.position)
            path["codes"].append("LINETO")

        # Add arrowhead in the path, the exact positions are recomputed within
        # EdgeCollection before each draw so they don't matter here. The
        # path for an arrowhead is: headbase (current), headleft, tip,
        # headright, headbase, so we need to add 4 (degenerate) vertices.
        # Assuming the arrowhead uses straight lines, they are all LINETO
        path["vertices"].extend([path["vertices"][-1] for x in range(4)])
        path["codes"].extend(["LINETO" for x in range(4)])

        # Draw the edge
        arrowpatch = mpl.patches.PathPatch(
            mpl.path.Path(
                path["vertices"],
                codes=[getattr(mpl.path.Path, x) for x in path["codes"]],
            ),
            edgecolor=edge.color,
            facecolor=edge.color,
            linewidth=edge.width,
            zorder=edge.zorder,
            clip_on=True,
        )

        return arrowpatch

    def draw_loop_edge(self, edge, vertex):
        """Draws a loop edge.

        The default implementation draws a small circle.

        @param edge: the edge to be drawn. Visual properties of the edge
          are defined by the attributes of this object.
        @param vertex: the vertex to which the edge is attached. Visual
          properties are given again as attributes.
        """
        ax = self.context
        radius = vertex.size * 1.5
        center_x = vertex.position[0] + cos(pi / 4) * radius / 2.0
        center_y = vertex.position[1] - sin(pi / 4) * radius / 2.0
        art = mpl.patches.Arc(
            (center_x, center_y),
            radius / 2.0,
            radius / 2.0,
            theta1=0,
            theta2=360.0,
            linewidth=edge.width,
            facecolor="none",
            edgecolor=edge.color,
            zorder=edge.zorder,
            clip_on=True,
        )
        return art

    def draw_undirected_edge(self, edge, src_vertex, dest_vertex):
        """Draws an undirected edge.

        The default implementation of this method draws undirected edges
        as straight lines. Loop edges are drawn as small circles.

        @param edge: the edge to be drawn. Visual properties of the edge
          are defined by the attributes of this object.
        @param src_vertex: the source vertex. Visual properties are given
          again as attributes.
        @param dest_vertex: the target vertex. Visual properties are given
          again as attributes.
        """
        if src_vertex == dest_vertex:
            return self.draw_loop_edge(edge, src_vertex)

        ax = self.context

        path = {"vertices": [], "codes": []}
        path["vertices"].append(src_vertex.position)
        path["codes"].append("MOVETO")

        if edge.curved:
            (x1, y1), (x2, y2) = src_vertex.position, dest_vertex.position
            aux1, aux2 = get_bezier_control_points_for_curved_edge(x1, y1, x2, y2, edge.curved)
            path["vertices"].append(aux1)
            path["vertices"].append(aux2)
            path["vertices"].append(dest_vertex.position)
            path["codes"].extend(["CURVE4"] * 3)
        else:
            path["vertices"].append(dest_vertex.position)
            path["codes"].append("LINETO")

        art = mpl.patches.PathPatch(
            mpl.path.Path(
                path["vertices"],
                codes=[getattr(mpl.path.Path, x) for x in path["codes"]],
            ),
            edgecolor=edge.color,
            facecolor="none",
            linewidth=edge.width,
            zorder=edge.zorder,
            clip_on=True,
        )
        return art


class EdgeCollection(PatchCollection):
    def __init__(self, *args, **kwargs):
        kwargs["match_original"] = True
        self._vertex_sizes = kwargs.pop("vertex_sizes", None)
        self._directed = kwargs.pop("directed", False)
        self._arrow_sizes = kwargs.pop("arrow_sizes", 0)
        self._arrow_widths = kwargs.pop("arrow_widths", 0)
        self._curved = kwargs.pop("curved", None)
        super().__init__(*args, **kwargs)
        self._paths_original = deepcopy(self._paths)

    def _update_paths(self):
        paths_original = self._paths_original
        vertex_sizes = self._vertex_sizes
        trans = self.axes.transData.transform
        trans_inv = self.axes.transData.inverted().transform

        # Get actual coordinates of the vertex border (rough)
        for i, (path_orig, sizes) in enumerate(zip(paths_original, vertex_sizes)):
            self._paths[i] = path = deepcopy(path_orig)
            coords = path_orig.vertices
            coordst = trans(coords)
            self._update_path_edge_start(path, coords, coordst, sizes[0], trans, trans_inv)
            if self._directed:
                self._update_path_edge_end_directed(
                    path, coords, coordst, sizes[1], trans, trans_inv,
                    self._arrow_sizes[i], self._arrow_widths[i],
                )
            else:
                self._update_path_edge_end_undirected(
                    path, coords, coordst, sizes[1], trans, trans_inv,
                )

    def _update_path_edge_start(self, path, coords, coordst, size, trans, trans_inv):
        theta = atan2(*((coordst[1] - coordst[0])[::-1]))
        voff = 0 * coordst[0]
        voff[:] = [cos(theta), sin(theta)]
        voff *= size / 2
        start = trans_inv(trans(coords[0]) + voff)
        path.vertices[0] = start

    def _update_path_edge_end_undirected(
            elf, path, coords, coordst, size, trans, trans_inv,
    ):
        theta = atan2(*((coordst[-2] - coordst[-1])[::-1]))
        voff = 0 * coordst[0]
        voff[:] = [cos(theta), sin(theta)]
        voff *= size / 2
        end = trans_inv(trans(coords[-1]) + voff)
        path.vertices[-1] = end

    def _update_path_edge_end_directed(
            self, path, coords, coordst, size, trans, trans_inv,
            arrow_size, arrow_width):
        # The path for arrows is start-headmid-headleft-tip-headright-headmid
        # So, tip is the 3rd-to-last and headmid the last
        theta = atan2(*((coordst[-6] - coordst[-3])[::-1]))
        voff_unity = 0 * coordst[0]
        voff_unity[:] = [cos(theta), sin(theta)]
        voff = voff_unity * size / 2
        voff_unity_90 = voff_unity @ [[0, 1], [-1, 0]]

        tip = trans_inv(trans(coords[-3]) + voff)
        headbase = trans_inv(trans(tip) + arrow_size * voff_unity)
        headleft = trans_inv(trans(headbase) + 0.5 * arrow_width * voff_unity_90)
        headright = trans_inv(trans(headbase) - 0.5 * arrow_width * voff_unity_90)
        path.vertices[-5:] = [headbase, headleft, tip, headright, headbase]

    def draw(self, renderer):
        if self._vertex_sizes is not None:
            self._update_paths()
        return super().draw(renderer)
