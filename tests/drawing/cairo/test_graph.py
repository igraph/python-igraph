import os
import random
import unittest


from igraph import Graph, InternalError, plot, VertexClustering
from igraph.drawing import find_cairo

# FIXME: find a better way to do this that works for both direct call and module
# import e.g. tox
try:
    from .utils import find_image_comparison, result_image_folder
except ImportError:
    from utils import find_image_comparison, result_image_folder


cairo = find_cairo()
has_cairo = hasattr(cairo, 'version')

image_comparison = find_image_comparison()


class GraphTestRunner(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if not has_cairo:
            raise unittest.SkipTest("cairo not found, skipping tests")
        result_image_folder.mkdir(parents=True, exist_ok=True)

    @image_comparison(baseline_images=["graph_basic"])
    def test_basic(self):
        g = Graph.Ring(5)
        plot(g, target=result_image_folder / 'graph_basic.png')

    @image_comparison(baseline_images=["graph_directed"])
    def test_directed(self):
        g = Graph.Ring(5, directed=True)
        plot(g, target=result_image_folder / 'graph_directed.png')

    @image_comparison(baseline_images=["graph_mark_groups_directed"])
    def test_mark_groups(self):
        g = Graph.Ring(5, directed=True)
        plot(
            g,
            target=result_image_folder / 'graph_mark_groups_directed.png',
            mark_groups=True)

    @image_comparison(
        baseline_images=["graph_mark_groups_squares_directed"]
    )
    def test_mark_groups_squares(self):
        g = Graph.Ring(5, directed=True)
        plot(
            g,
            target=result_image_folder / 'graph_mark_groups_squares_directed.png',
            mark_groups=True,
            vertex_shape="square",
        )


class ClusteringTestRunner(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if not has_cairo:
            raise unittest.SkipTest("cairo not found, skipping tests")
        result_image_folder.mkdir(parents=True, exist_ok=True)

    @image_comparison(baseline_images=["clustering_directed"])
    def test_clustering_directed_small(self):
        g = Graph.Ring(5, directed=True)
        clu = VertexClustering(g, [0] * 5)
        plot(
            clu,
            target=result_image_folder / 'clustering_directed.png',
            mark_groups=True,
        )

    @image_comparison(baseline_images=["clustering_directed_large"])
    def test_clustering_directed_large(self):
        g = Graph.Ring(50, directed=True)
        clu = VertexClustering(g, [0] * 3 + [1] * 17 + [2] * 30)
        layout = [(x*2.5, y*2.5) for x, y in g.layout("circle")]
        plot(
            clu,
            layout=layout,
            target=result_image_folder / 'clustering_directed_large.png',
            mark_groups=True,
        )


def suite():
    graph = unittest.defaultTestLoader.loadTestsFromTestCase(GraphTestRunner)
    clustering = unittest.defaultTestLoader.loadTestsFromTestCase(ClusteringTestRunner)
    return unittest.TestSuite([
        graph,
        clustering,
    ])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
