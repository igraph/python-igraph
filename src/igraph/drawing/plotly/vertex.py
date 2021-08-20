"""Vertices drawer. Unlike other backends, all vertices are drawn at once"""

from .utils import find_plotly

__all__ = ('PlotlyVerticesDrawer',)

plotly = find_plotly()


class PlotlyVerticesDrawer:
    default_args = {
        'symbol': 'circle',
        'size': 0.2,
        'fillcolor': 'green',
        'line_color': 'black',
    }


    def __init__(self, fig):
        self.fig = fig

    def draw(self, vertex_iter):
        fig = self.fig

        # Vertices
        marker_kwds = {
            'x': [],
            'y': [],
            'symbol': [],
            'size': [],
            'fillcolor': [],
            'line_color': [],
        }
        # Vertex text
        text_kwds = {
            'x': [],
            'y': [],
            'text': [],
        }
        # We iterate only once as it can exhaust
        for vertex, visual_vertex, point in vertex_iter:
            if visual_vertex.size > 0:
                marker_kwds['x'].append(point[0])
                marker_kwds['y'].append(point[1])
                marker_kwds['symbol'] = visual_vertex.shape
                marker_kwds['size'] = visual_vertex.size
                marker_kwds['fillcolor'] = visual_vertex.color
                marker_kwds['line_color'] = visual_vertex.edge_color

            if visual_vertex.label is not None:
                text_kwds['x'].append(point[0])
                text_kwds['y'].append(point[1])
                text_kwds['text'].append(visual_vertex.label)

        # Draw dots
        if len(marker_kwds['x']):
            stroke = plotly.graph_objects.Scatter(
                mode='markers',
                **marker_kwds,
            )
            fig.add_trace(stroke)

        # Draw text labels
        if len(text_kwds['x']):
            stroke = plotly.graph_objects.Scatter(
                mode='text',
                **text_kwds,
            )
            fig.add_trace(stroke)
