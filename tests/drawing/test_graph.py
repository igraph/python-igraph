import random
import unittest


from igraph import Graph, InternalError, plot, VertexClustering
from .utils import find_image_comparison

try:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
except ImportError:
    mpl = None
    plt = None

image_comparison = find_image_comparison()


class GraphTestRunner(unittest.TestCase):
    @unittest.skipIf(plt is None, "test case depends on matplotlib")
    @image_comparison(
            baseline_images=['graph_basic'], remove_text=True)
    def test_basic(self):
        plt.close('all')
        g = Graph.Ring(5)
        fig, ax = plt.subplots()
        plot(g, target=ax)

    @unittest.skipIf(plt is None, "test case depends on matplotlib")
    @image_comparison(
            baseline_images=['graph_directed'], remove_text=True)
    def test_directed(self):
        plt.close('all')
        g = Graph.Ring(5, directed=True)
        fig, ax = plt.subplots()
        plot(g, target=ax)

    @unittest.skipIf(plt is None, "test case depends on matplotlib")
    @image_comparison(
            baseline_images=['graph_mark_groups_directed'], remove_text=True)
    def test_mark_groups(self):
        plt.close('all')
        g = Graph.Ring(5, directed=True)
        fig, ax = plt.subplots()
        plot(g, target=ax, mark_groups=True)

    @unittest.skipIf(plt is None, "test case depends on matplotlib")
    @image_comparison(
            baseline_images=['graph_mark_groups_squares_directed'], remove_text=True)
    def test_mark_groups_squares(self):
        plt.close('all')
        g = Graph.Ring(5, directed=True)
        fig, ax = plt.subplots()
        plot(g, target=ax, mark_groups=True, vertex_shape='s')


class ClusteringTestRunner(unittest.TestCase):
    @unittest.skipIf(plt is None, "test case depends on matplotlib")
    @image_comparison(
            baseline_images=['clustering_directed'], remove_text=True)
    def test_clustering_directed_small(self):
        plt.close('all')
        g = Graph.Ring(5, directed=True)
        clu = VertexClustering(g, [0] * 5)
        fig, ax = plt.subplots()
        plot(clu, target=ax, mark_groups=True)

    @unittest.skipIf(plt is None, "test case depends on matplotlib")
    @image_comparison(
            baseline_images=['clustering_directed_large'], remove_text=True)
    def test_clustering_directed_large(self):
        plt.close('all')
        g = Graph.Ring(50, directed=True)
        clu = VertexClustering(g, [0] * 3 + [1] * 17 + [2] * 30)
        fig, ax = plt.subplots()
        plot(clu, target=ax, mark_groups=True)



def suite():
    graph = unittest.makeSuite(GraphTestRunner)
    clustering = unittest.makeSuite(ClusteringTestRunner)
    return unittest.TestSuite([graph, clustering])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
