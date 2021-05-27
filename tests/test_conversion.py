import random
import unittest

from igraph import Graph, Matrix


class DirectedUndirectedTests(unittest.TestCase):
    def testToUndirected(self):
        graph = Graph([(0, 1), (0, 2), (1, 0)], directed=True)

        graph2 = graph.copy()
        graph2.to_undirected(mode=False)
        self.assertTrue(graph2.vcount() == graph.vcount())
        self.assertTrue(graph2.is_directed() == False)
        self.assertTrue(sorted(graph2.get_edgelist()) == [(0, 1), (0, 1), (0, 2)])

        graph2 = graph.copy()
        graph2.to_undirected()
        self.assertTrue(graph2.vcount() == graph.vcount())
        self.assertTrue(graph2.is_directed() == False)
        self.assertTrue(sorted(graph2.get_edgelist()) == [(0, 1), (0, 2)])

        graph2 = graph.copy()
        graph2.es["weight"] = [1, 2, 3]
        graph2.to_undirected(mode="collapse", combine_edges="sum")
        self.assertTrue(graph2.vcount() == graph.vcount())
        self.assertTrue(graph2.is_directed() == False)
        self.assertTrue(sorted(graph2.get_edgelist()) == [(0, 1), (0, 2)])
        self.assertTrue(graph2.es["weight"] == [4, 2])

        graph = Graph([(0, 1), (1, 0), (0, 1), (1, 0), (2, 1), (1, 2)], directed=True)
        graph2 = graph.copy()
        graph2.es["weight"] = [1, 2, 3, 4, 5, 6]
        graph2.to_undirected(mode="mutual", combine_edges="sum")
        self.assertTrue(graph2.vcount() == graph.vcount())
        self.assertTrue(graph2.is_directed() == False)
        self.assertTrue(sorted(graph2.get_edgelist()) == [(0, 1), (0, 1), (1, 2)])
        self.assertTrue(
            graph2.es["weight"] == [7, 3, 11] or graph2.es["weight"] == [3, 7, 11]
        )

    def testToDirectedNoModeArg(self):
        graph = Graph([(0, 1), (0, 2), (2, 3), (2, 4)], directed=False)
        graph.to_directed()
        self.assertTrue(graph.is_directed())
        self.assertTrue(graph.vcount() == 5)
        self.assertTrue(
            sorted(graph.get_edgelist())
            == [(0, 1), (0, 2), (1, 0), (2, 0), (2, 3), (2, 4), (3, 2), (4, 2)]
        )

    def testToDirectedMutual(self):
        graph = Graph([(0, 1), (0, 2), (2, 3), (2, 4)], directed=False)
        graph.to_directed("mutual")
        self.assertTrue(graph.is_directed())
        self.assertTrue(graph.vcount() == 5)
        self.assertTrue(
            sorted(graph.get_edgelist())
            == [(0, 1), (0, 2), (1, 0), (2, 0), (2, 3), (2, 4), (3, 2), (4, 2)]
        )

    def testToDirectedAcyclic(self):
        graph = Graph([(0, 1), (2, 0), (3, 0), (3, 0), (4, 2)], directed=False)
        graph.to_directed("acyclic")
        self.assertTrue(graph.is_directed())
        self.assertTrue(graph.vcount() == 5)
        self.assertTrue(
            sorted(graph.get_edgelist())
            == [(0, 1), (0, 2), (0, 3), (0, 3), (2, 4)]
        )

    def testToDirectedRandom(self):
        random.seed(0)

        graph = Graph.Ring(200, directed=False)
        graph.to_directed("random")

        self.assertTrue(graph.is_directed())
        self.assertTrue(graph.vcount() == 200)
        edgelist1 = sorted(graph.get_edgelist())

        graph = Graph.Ring(200, directed=False)
        graph.to_directed("random")

        self.assertTrue(graph.is_directed())
        self.assertTrue(graph.vcount() == 200)
        edgelist2 = sorted(graph.get_edgelist())

        self.assertTrue(edgelist1 != edgelist2)

    def testToDirectedInvalidMode(self):
        graph = Graph([(0, 1), (0, 2), (2, 3), (2, 4)], directed=False)
        with self.assertRaises(ValueError):
            graph.to_directed("no-such-mode")


class GraphRepresentationTests(unittest.TestCase):
    def testGetAdjacency(self):
        # Undirected case
        g = Graph.Tree(6, 3)
        g.es["weight"] = list(range(5))
        self.assertTrue(
            g.get_adjacency()
            == Matrix(
                [
                    [0, 1, 1, 1, 0, 0],
                    [1, 0, 0, 0, 1, 1],
                    [1, 0, 0, 0, 0, 0],
                    [1, 0, 0, 0, 0, 0],
                    [0, 1, 0, 0, 0, 0],
                    [0, 1, 0, 0, 0, 0],
                ]
            )
        )
        self.assertTrue(
            g.get_adjacency(attribute="weight")
            == Matrix(
                [
                    [0, 0, 1, 2, 0, 0],
                    [0, 0, 0, 0, 3, 4],
                    [1, 0, 0, 0, 0, 0],
                    [2, 0, 0, 0, 0, 0],
                    [0, 3, 0, 0, 0, 0],
                    [0, 4, 0, 0, 0, 0],
                ]
            )
        )
        self.assertTrue(
            g.get_adjacency(eids=True)
            == Matrix(
                [
                    [0, 1, 2, 3, 0, 0],
                    [1, 0, 0, 0, 4, 5],
                    [2, 0, 0, 0, 0, 0],
                    [3, 0, 0, 0, 0, 0],
                    [0, 4, 0, 0, 0, 0],
                    [0, 5, 0, 0, 0, 0],
                ]
            )
            - 1
        )

        # Directed case
        g = Graph.Tree(6, 3, "tree_out")
        g.add_edges([(0, 1), (1, 0)])
        self.assertTrue(
            g.get_adjacency()
            == Matrix(
                [
                    [0, 2, 1, 1, 0, 0],
                    [1, 0, 0, 0, 1, 1],
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                ]
            )
        )

    def testGetSparseAdjacency(self):
        try:
            from scipy import sparse
            import numpy as np
        except ImportError:
            self.skipTest("Scipy and numpy are dependencies of this test.")

        # Undirected case
        g = Graph.Tree(6, 3)
        g.es["weight"] = list(range(5))
        self.assertTrue(
            np.all((g.get_adjacency_sparse() == np.array(g.get_adjacency().data)))
        )
        self.assertTrue(
            np.all(
                (
                    g.get_adjacency_sparse(attribute="weight")
                    == np.array(g.get_adjacency(attribute="weight").data)
                )
            )
        )

        # Directed case
        g = Graph.Tree(6, 3, "tree_out")
        g.add_edges([(0, 1), (1, 0)])
        self.assertTrue(
            np.all(g.get_adjacency_sparse() == np.array(g.get_adjacency().data))
        )


def suite():
    direction_suite = unittest.makeSuite(DirectedUndirectedTests)
    representation_suite = unittest.makeSuite(GraphRepresentationTests)
    return unittest.TestSuite([direction_suite, representation_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
