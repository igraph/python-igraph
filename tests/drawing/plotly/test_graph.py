import random
import unittest


from igraph import Graph, InternalError, plot, VertexClustering

# FIXME: find a better way to do this that works for both direct call and module
# import e.g. tox
#try:
#    from ..utils import find_image_comparison
#except ImportError:
#    from utils import find_image_comparison

try:
    import plotly
except ImportError:
    plotly = None

#image_comparison = find_image_comparison()


class GraphTestRunner(unittest.TestCase):
    @unittest.skipIf(plotly is None, "test case depends on plotly")
    #@image_comparison(baseline_images=["graph_basic_plotly"], remove_text=False)
    def test_basic(self):
        g = Graph.Ring(5)
        fig = plotly.graph_objects.Figure()
        plot(g, target=fig)

    @unittest.skipIf(plotly is None, "test case depends on plotly")
    #@image_comparison(baseline_images=["graph_directed"], remove_text=True)
    def test_directed(self):
        g = Graph.Ring(5, directed=True)
        fig = plotly.graph_objects.Figure()
        plot(g, target=fig)

    @unittest.skipIf(plotly is None, "test case depends on plotly")
    #@image_comparison(baseline_images=["graph_mark_groups_directed"], remove_text=True)
    def test_mark_groups(self):
        g = Graph.Ring(5, directed=True)
        fig = plotly.graph_objects.Figure()
        plot(g, target=fig, mark_groups=True)

    @unittest.skipIf(plotly is None, "test case depends on plotly")
    #@image_comparison(
    #    baseline_images=["graph_mark_groups_squares_directed"], remove_text=True
    #)
    def test_mark_groups_squares(self):
        g = Graph.Ring(5, directed=True)
        fig = plotly.graph_objects.Figure()
        plot(g, target=fig, mark_groups=True, vertex_shape="square")

    @unittest.skipIf(plotly is None, "test case depends on plotly")
    #@image_comparison(baseline_images=["graph_edit_children"], remove_text=True)
    def test_mark_groups_squares(self):
        g = Graph.Ring(5)
        fig = plotly.graph_objects.Figure()
        plot(g, target=fig, vertex_shape="circle")
        # FIXME
        #dot = ax.get_children()[0]
        #dot.set_facecolor("blue")
        #dot.radius *= 0.5


class ClusteringTestRunner(unittest.TestCase):
    @unittest.skipIf(plotly is None, "test case depends on plotly")
    #@image_comparison(baseline_images=["clustering_directed"], remove_text=True)
    def test_clustering_directed_small(self):
        g = Graph.Ring(5, directed=True)
        clu = VertexClustering(g, [0] * 5)
        fig = plotly.graph_objects.Figure()
        plot(clu, target=fig, mark_groups=True)

    @unittest.skipIf(plotly is None, "test case depends on plotly")
    #@image_comparison(baseline_images=["clustering_directed_large"], remove_text=True)
    def test_clustering_directed_large(self):
        g = Graph.Ring(50, directed=True)
        clu = VertexClustering(g, [0] * 3 + [1] * 17 + [2] * 30)
        fig = plotly.graph_objects.Figure()
        layout = [(x*2.5, y*2.5) for x, y in g.layout("circle")]
        plot(clu, layout=layout, target=fig, mark_groups=True)


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
