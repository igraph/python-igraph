import random
import unittest

from igraph import Graph, plot, VertexClustering

# FIXME: find a better way to do this that works for both direct call and module
# import e.g. tox
try:
    from .utils import are_tests_supported, find_image_comparison, result_image_folder
except ImportError:
    from utils import are_tests_supported, find_image_comparison, result_image_folder


image_comparison = find_image_comparison()


class GraphTestRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        supported, msg = are_tests_supported()
        if not supported:
            raise unittest.SkipTest(f"{msg}, skipping tests")
        result_image_folder.mkdir(parents=True, exist_ok=True)

    def setUp(self) -> None:
        random.seed(42)

    @image_comparison(baseline_images=["graph_basic"])
    def test_basic(self):
        g = Graph.Ring(5)
        lo = g.layout("auto")
        plot(
            g,
            layout=lo,
            target=result_image_folder / "graph_basic.png",
            backend="cairo",
        )

    @image_comparison(baseline_images=["graph_directed"])
    def test_directed(self):
        g = Graph.Ring(5, directed=True)
        lo = g.layout("auto")
        plot(
            g,
            layout=lo,
            target=result_image_folder / "graph_directed.png",
            backend="cairo",
        )

    @image_comparison(baseline_images=["graph_mark_groups_directed"])
    def test_mark_groups(self):
        g = Graph.Ring(5, directed=True)
        lo = g.layout("auto")
        plot(
            g,
            layout=lo,
            target=result_image_folder / "graph_mark_groups_directed.png",
            backend="cairo",
            mark_groups=True,
        )

    @image_comparison(baseline_images=["graph_mark_groups_squares_directed"])
    def test_mark_groups_squares(self):
        g = Graph.Ring(5, directed=True)
        lo = g.layout("auto")
        plot(
            g,
            layout=lo,
            target=result_image_folder / "graph_mark_groups_squares_directed.png",
            backend="cairo",
            mark_groups=True,
            vertex_shape="square",
        )

    @image_comparison(baseline_images=["graph_with_curved_edges"])
    def test_graph_with_curved_edges(self):
        g = Graph.Ring(24, directed=True, mutual=True)
        lo = g.layout("circle")
        plot(
            g,
            layout=lo,
            target=result_image_folder / "graph_with_curved_edges.png",
            bbox=(800, 800),
            edge_curved=0.25,
            backend="cairo",
        )


class ClusteringTestRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        supported, msg = are_tests_supported()
        if not supported:
            raise unittest.SkipTest(f"{msg}, skipping tests")
        result_image_folder.mkdir(parents=True, exist_ok=True)

    def setUp(self) -> None:
        random.seed(42)

    @image_comparison(baseline_images=["clustering_directed"])
    def test_clustering_directed_small(self):
        g = Graph.Ring(5, directed=True)
        clu = VertexClustering(g, [0] * 5)
        lo = g.layout("auto")
        plot(
            clu,
            layout=lo,
            backend="cairo",
            target=result_image_folder / "clustering_directed.png",
            mark_groups=True,
        )

    @image_comparison(baseline_images=["clustering_directed_large"])
    def test_clustering_directed_large(self):
        g = Graph.Ring(50, directed=True)
        clu = VertexClustering(g, [0] * 3 + [1] * 17 + [2] * 30)
        layout = [(x * 2.5, y * 2.5) for x, y in g.layout("circle")]
        plot(
            clu,
            backend="cairo",
            layout=layout,
            target=result_image_folder / "clustering_directed_large.png",
            mark_groups=True,
        )


def suite():
    graph = unittest.defaultTestLoader.loadTestsFromTestCase(GraphTestRunner)
    clustering = unittest.defaultTestLoader.loadTestsFromTestCase(ClusteringTestRunner)
    return unittest.TestSuite([graph, clustering])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
