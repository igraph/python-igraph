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


image_comparison = find_image_comparison()


class GraphTestRunner(unittest.TestCase):
    @image_comparison(baseline_images=["graph_basic"])
    def test_basic(self):
        g = Graph.Ring(5)
        fig = plotly.graph_objects.Figure()
        plot(g, target=fig)
        return fig

    @image_comparison(baseline_images=["graph_directed"])
    def test_directed(self):
        g = Graph.Ring(5, directed=True)
        fig = plotly.graph_objects.Figure()
        plot(g, target=fig)
        return fig

    @image_comparison(baseline_images=["graph_mark_groups_directed"])
    def test_mark_groups(self):
        g = Graph.Ring(5, directed=True)
        fig = plotly.graph_objects.Figure()
        plot(g, target=fig, mark_groups=True)
        return fig

    @image_comparison(
        baseline_images=["graph_mark_groups_squares_directed"]
    )
    def test_mark_groups_squares(self):
        g = Graph.Ring(5, directed=True)
        fig = plotly.graph_objects.Figure()
        plot(g, target=fig, mark_groups=True, vertex_shape="square")
        return fig

    @image_comparison(baseline_images=["graph_edit_children"])
    def test_mark_groups_squares(self):
        g = Graph.Ring(5)
        fig = plotly.graph_objects.Figure()
        plot(g, target=fig, vertex_shape="circle")
        # FIXME
        #dot = ax.get_children()[0]
        #dot.set_facecolor("blue")
        #dot.radius *= 0.5
        return fig


class ClusteringTestRunner(unittest.TestCase):
    @image_comparison(baseline_images=["clustering_directed"])
    def test_clustering_directed_small(self):
        g = Graph.Ring(5, directed=True)
        clu = VertexClustering(g, [0] * 5)
        fig = plotly.graph_objects.Figure()
        plot(clu, target=fig, mark_groups=True)
        return fig

    @image_comparison(baseline_images=["clustering_directed_large"])
    def test_clustering_directed_large(self):
        g = Graph.Ring(50, directed=True)
        clu = VertexClustering(g, [0] * 3 + [1] * 17 + [2] * 30)
        fig = plotly.graph_objects.Figure()
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
