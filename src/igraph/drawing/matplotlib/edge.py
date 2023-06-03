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

    def build_patch(self, edge, src_vertex, dest_vertex):
        art = mpl.patches.PathPatch(
            mpl.path.Path([[0, 0]]),
            edgecolor=edge.color,
            facecolor=edge.color if src_vertex != dest_vertex else "none",
            linewidth=edge.width,
            zorder=edge.zorder,
            clip_on=True,
        )
        return art

    # The following two methods are replaced by dummy functions, the rest is
    # taken care of in EdgeCollection for efficiency
    def draw_directed_edge(self, edge, src_vertex, dest_vertex):
        return self.build_patch(edge)

    def draw_undirected_edge(self, edge, src_vertex, dest_vertex):
        return self.build_patch(edge)


class EdgeCollection(PatchCollection):
    def __init__(self, *args, **kwargs):
        kwargs["match_original"] = True
        self._visual_vertices = kwargs.pop("visual_vertices", None)
        self._directed = kwargs.pop("directed", False)
        self._arrow_sizes = kwargs.pop("arrow_sizes", None)
        self._arrow_widths = kwargs.pop("arrow_widths", None)
        self._curved = kwargs.pop("curved", None)
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_edge_vertex_sizes(edge_vertices):
        sizes = []
        for visual_vertex in edge_vertices:
            if visual_vertex.size is not None:
                sizes.append(visual_vertex.size)
            else:
                sizes.append(max(visual_vertex.width, visual_vertex.height))
        return sizes

    def _compute_paths(self, transform=None):
        import numpy as np

        visual_vertices = self._visual_vertices
        if transform is None:
            transform = self.get_transform()
        trans = transform.transform
        trans_inv = transform.inverted().transform

        # Get actual coordinates of the vertex border (rough)
        paths = []
        for i, edge_vertices in enumerate(visual_vertices):
            coords = np.vstack(
                [
                    edge_vertices[0].position,
                    edge_vertices[1].position,
                ]
            )
            coordst = trans(coords)
            sizes = self._get_edge_vertex_sizes(edge_vertices)
            if self._curved is not None:
                curved = self._curved[i]
            else:
                curved = False

            # Loops require special attention, discard any previous calculations
            if edge_vertices[0] == edge_vertices[1]:
                path = self._compute_path_loop(
                    coordst[0],
                    sizes[0],
                    trans_inv,
                )

            elif self._directed:
                if (self._arrow_sizes is None) or (self._arrow_widths is None):
                    arrow_size = 0
                    arrow_width = 0
                else:
                    arrow_size = self._arrow_sizes[i]
                    arrow_width = self._arrow_widths[i]
                path = self._compute_path_directed(
                    coordst,
                    sizes,
                    trans_inv,
                    curved,
                    arrow_size,
                    arrow_width,
                )
            else:
                path = self._compute_path_undirected(
                    coordst,
                    sizes,
                    trans_inv,
                    curved,
                )

            paths.append(path)
        return paths

    def _compute_path_loop(self, coordt, size, trans_inv):
        import numpy as np

        # Make arc (class method)
        path = mpl.path.Path.arc(-90, 180)
        vertices = path.vertices.copy()
        codes = path.codes

        # Rescale to be as large as the vertex
        vertices *= size / 2
        # Center top right
        vertices += size / 2
        # Offset to place and transform to data coordinates
        vertices = trans_inv(coordt + vertices)

        # Hack used for any curved lines to deal with facecolor
        vertices = np.vstack([
            vertices,
            vertices[:-1][::-1],
        ])
        codes = np.concatenate([
            codes,
            codes[1:],
        ])

        path = mpl.path.Path(
            vertices, codes=codes,
        )
        return path

    def _compute_path_undirected(self, coordst, sizes, trans_inv, curved):
        path = {"vertices": [], "codes": []}
        path["codes"].append("MOVETO")
        if not curved:
            path["codes"].append("LINETO")

            # Start
            theta = atan2(*((coordst[1] - coordst[0])[::-1]))
            voff = 0 * coordst[0]
            voff[:] = [cos(theta), sin(theta)]
            voff *= sizes[0] / 2
            path["vertices"].append(coordst[0] + voff)

            # End
            voff[:] = [cos(theta), sin(theta)]
            voff *= sizes[1] / 2
            path["vertices"].append(coordst[1] - voff)
        else:
            path["codes"].extend(["CURVE4"] * 3)

            aux1, aux2 = get_bezier_control_points_for_curved_edge(
                *coordst.ravel(),
                curved,
            )

            # Start
            theta = atan2(*((aux1 - coordst[0])[::-1]))
            voff = 0 * coordst[0]
            voff[:] = [cos(theta), sin(theta)]
            voff *= sizes[0] / 2
            path["vertices"].append(coordst[0] + voff)

            # Bezier
            path["vertices"].append(aux1)
            path["vertices"].append(aux2)

            # End
            theta = atan2(*((coordst[1] - aux2)[::-1]))
            voff = 0 * coordst[0]
            voff[:] = [cos(theta), sin(theta)]
            voff *= sizes[1] / 2
            path["vertices"].append(coordst[1] - voff)

        path = mpl.path.Path(
            path["vertices"],
            codes=[getattr(mpl.path.Path, x) for x in path["codes"]],
        )
        path.vertices = trans_inv(path.vertices)
        return path

    def _compute_path_directed(
        self, coordst, sizes, trans_inv, curved, arrow_size, arrow_width
    ):
        path = {"vertices": [], "codes": []}
        path["codes"].append("MOVETO")
        if not curved:
            path["codes"].extend(["LINETO"] * 5)

            # Start
            theta = atan2(*((coordst[1] - coordst[0])[::-1]))
            voff = 0 * coordst[0]
            voff[:] = [cos(theta), sin(theta)]
            voff *= sizes[0] / 2
            path["vertices"].append(coordst[0] + voff)

            # End with arrow (base-left-top-right-base)
            theta = atan2(*((coordst[1] - coordst[0])[::-1]))
            voff_unity = 0 * coordst[0]
            voff_unity[:] = [cos(theta), sin(theta)]
            voff = voff_unity * sizes[1] / 2
            tip = coordst[1] - voff

            voff_unity_90 = voff_unity @ [[0, 1], [-1, 0]]
            headbase = tip - arrow_size * voff_unity
            headleft = headbase + 0.5 * arrow_width * voff_unity_90
            headright = headbase - 0.5 * arrow_width * voff_unity_90
            path["vertices"].extend(
                [
                    headbase,
                    headleft,
                    tip,
                    headright,
                    headbase,
                ]
            )
        else:
            # Bezier
            aux1, aux2 = get_bezier_control_points_for_curved_edge(
                *coordst.ravel(),
                curved,
            )

            # Start
            theta = atan2(*((aux1 - coordst[0])[::-1]))
            voff = 0 * coordst[0]
            voff[:] = [cos(theta), sin(theta)]
            voff *= sizes[0] / 2
            start = coordst[0] + voff

            # End with arrow (base-left-top-right-base)
            theta = atan2(*((coordst[1] - aux2)[::-1]))
            voff_unity = 0 * coordst[0]
            voff_unity[:] = [cos(theta), sin(theta)]
            voff = voff_unity * sizes[1] / 2
            tip = coordst[1] - voff

            voff_unity_90 = voff_unity @ [[0, 1], [-1, 0]]
            headbase = tip - arrow_size * voff_unity
            headleft = headbase + 0.5 * arrow_width * voff_unity_90
            headright = headbase - 0.5 * arrow_width * voff_unity_90

            # This is a dirty trick to make the facecolor work
            # without making a separate Patch, which would be a little messy
            path["codes"].extend(["CURVE4"] * 6 + ["LINETO"] * 4)
            path["vertices"].extend([
                headbase, aux2, aux1,
                start, aux1, aux2,
                headbase,
                headleft,
                tip,
                headright,
                headbase,
            ])

        path = mpl.path.Path(
            path["vertices"],
            codes=[getattr(mpl.path.Path, x) for x in path["codes"]],
        )
        path.vertices = trans_inv(path.vertices)
        return path

    def draw(self, renderer):
        if self._visual_vertices is not None:
            self._paths = self._compute_paths()
        return super().draw(renderer)

    def get_arrow_sizes(self):
        """Same as get_arrow_size."""
        return self.get_arrow_size()

    def get_arrow_size(self):
        """Get arrow sizes for the edges (directed only).

        @return: An array of arrow sizes.
        """
        import numpy as np

        if self._arrow_sizes is None:
            arrow_sizes = [0 for x in self.get_paths()]
        else:
            arrow_sizes = self._arrow_sizes
        return np.array(arrow_sizes)

    def set_arrow_size(self, sizes):
        """Set arrow sizes.

        @param sizes: A sequence of arrow sizes or a single size.
        """
        try:
            iter(sizes)
        except TypeError:
            sizes = [sizes] * len(self._paths)
        self._arrow_sizes = sizes
        self.stale = True

    def set_arrow_sizes(self, sizes):
        """Same as set_arrow_size"""
        return self.set_arrow_size(sizes)

    def get_arrow_widths(self):
        """Same as get_arrow_width."""
        return self.get_arrow_width()

    def get_arrow_width(self):
        """Get arrow widths for the edges (directed only).

        @return: An array of arrow widths.
        """
        import numpy as np

        if self._arrow_widths is None:
            arrow_widths = [0 for x in self.get_paths()]
        else:
            arrow_widths = self._arrow_widths
        return np.array(arrow_widths)

    def set_arrow_width(self, widths):
        """Set arrow widths.

        @param widths: A sequence of arrow widths or a single width.
        """
        try:
            iter(widths)
        except TypeError:
            widths = [widths] * len(self._paths)
        self._arrow_widths = widths
        self.stale = True

    def set_arrow_widths(self, widths):
        """Same as set_arrow_width"""
        return self.set_arrow_width(widths)

    @property
    def stale(self):
        return super().stale

    @stale.setter
    def stale(self, val):
        PatchCollection.stale.fset(self, val)
        if val and hasattr(self, "stale_callback_post"):
            self.stale_callback_post(self)
