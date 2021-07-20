import random
import unittest

import matplotlib as mpl
import matplotlib.pyplot as plt
from utils import image_comparison

from igraph import Graph, InternalError, plot


class GraphTestRunner(unittest.TestCase):

    @image_comparison(
            baseline_images=['graph_basic'], remove_text=True)
    def test_basic(self):
        plt.close('all')
        g = Graph.Ring(5)
        fig, ax = plt.subplots()
        plot(g, target=ax)

    @image_comparison(
            baseline_images=['graph_directed'], remove_text=True)
    def test_directed(self):
        plt.close('all')
        g = Graph.Ring(5, directed=True)
        fig, ax = plt.subplots()
        plot(g, target=ax)


def suite():
    undirected_suite = unittest.makeSuite(GraphTestRunner)
    return unittest.TestSuite([undirected_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
