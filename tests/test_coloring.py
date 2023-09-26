import unittest
from igraph import Graph


def assert_valid_vertex_coloring(graph, coloring):
    assert min(coloring) == 0
    for edge in graph.es:
        source, target = edge.tuple
        assert source == target or coloring[source] != coloring[target]


class VertexColoringTests(unittest.TestCase):
    def testGreedyVertexColoring(self):
        g = Graph.Famous("petersen")

        col = g.vertex_coloring_greedy()
        assert_valid_vertex_coloring(g, col)

        col = g.vertex_coloring_greedy("colored_neighbors")
        assert_valid_vertex_coloring(g, col)

        col = g.vertex_coloring_greedy("dsatur")
        assert_valid_vertex_coloring(g, col)


def suite():
    vertex_coloring_suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        VertexColoringTests
    )
    return unittest.TestSuite([vertex_coloring_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
