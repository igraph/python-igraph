import random
import unittest


from igraph import Graph, InternalError, plot, VertexClustering

# FIXME: find a better way to do this that works for both direct call and module
# import e.g. tox
try:
    from .utils import find_image_comparison
except ImportError:
    from utils import find_image_comparison

try:
    import plotly
except ImportError:
    raise unittest.SkipTest("plotly not found, skipping tests")

# FIXME: trying to debug this specific import on CI
try:
    from plotly import graph_objects as go
except ImportError:
    raise ImportError('Cannot import graph_objects, dir(plotly): '+str(dir(plotly)))

image_comparison = find_image_comparison()


class GraphTestRunner(unittest.TestCase):
    @property
    def layout_small_ring(self):
        coords = [
            [1.015318095035966, 0.03435580194714975],
            [0.29010409851547664, 1.0184451153265959],
            [-0.8699239050738742, 0.6328259400443561],
            [-0.8616466426732888, -0.5895891303732176],
            [0.30349699041342515, -0.9594640169691343],
        ]
        return coords

    @image_comparison(baseline_images=["graph_basic"])
    def test_basic(self):
        g = Graph.Ring(5)
        fig = go.Figure()
        plot(g, target=fig, layout=self.layout_small_ring)
        return fig

    @image_comparison(baseline_images=["graph_directed"])
    def test_directed(self):
        g = Graph.Ring(5, directed=True)
        fig = go.Figure()
        plot(g, target=fig, layout=self.layout_small_ring)
        return fig

    @image_comparison(baseline_images=["graph_mark_groups_directed"])
    def test_mark_groups(self):
        g = Graph.Ring(5, directed=True)
        fig = go.Figure()
        plot(g, target=fig, mark_groups=True,
             layout=self.layout_small_ring)
        return fig

    @image_comparison(
        baseline_images=["graph_mark_groups_squares_directed"]
    )
    def test_mark_groups_squares(self):
        g = Graph.Ring(5, directed=True)
        fig = go.Figure()
        plot(g, target=fig, mark_groups=True, vertex_shape="square",
             layout=self.layout_small_ring)
        return fig

    @image_comparison(baseline_images=["graph_edit_children"])
    def test_mark_groups_squares(self):
        g = Graph.Ring(5)
        fig = go.Figure()
        plot(g, target=fig, vertex_shape="circle",
             layout=self.layout_small_ring)
        # FIXME
        #dot = ax.get_children()[0]
        #dot.set_facecolor("blue")
        #dot.radius *= 0.5
        return fig


class ClusteringTestRunner(unittest.TestCase):
    @property
    def layout_small_ring(self):
        coords = [
            [1.015318095035966, 0.03435580194714975],
            [0.29010409851547664, 1.0184451153265959],
            [-0.8699239050738742, 0.6328259400443561],
            [-0.8616466426732888, -0.5895891303732176],
            [0.30349699041342515, -0.9594640169691343],
        ]
        return coords

    @image_comparison(baseline_images=["clustering_directed"])
    def test_clustering_directed_small(self):
        g = Graph.Ring(5, directed=True)
        clu = VertexClustering(g, [0] * 5)
        fig = go.Figure()
        plot(clu, target=fig, mark_groups=True, layout=self.layout_small_ring)
        return fig

    @image_comparison(baseline_images=["clustering_directed_large"])
    def test_clustering_directed_large(self):
        g = Graph.Ring(50, directed=True)
        clu = VertexClustering(g, [0] * 3 + [1] * 17 + [2] * 30)
        fig = go.Figure()
        layout = [(x*2.5, y*2.5) for x, y in g.layout("circle")]
        plot(clu, layout=layout, target=fig, mark_groups=True)
        return fig


def suite():
    graph = unittest.makeSuite(GraphTestRunner)
    clustering = unittest.makeSuite(ClusteringTestRunner)
    return unittest.TestSuite([
        graph,
        clustering,
    ])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
