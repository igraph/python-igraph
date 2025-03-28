import random
import unittest

from igraph import Graph


class CycleTests(unittest.TestCase):
    def setUp(self):
        random.seed(42)

    def test_is_acyclic(self):
        g = Graph.Tree(121, 3, mode="out")
        self.assertTrue(g.is_acyclic())

        g = Graph()
        self.assertTrue(g.is_acyclic())

        g = Graph.Ring(5)
        self.assertFalse(g.is_acyclic())

    def test_is_dag(self):
        g = Graph(5, [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)], directed=True)
        self.assertTrue(g.is_dag())
        g.to_undirected()
        self.assertFalse(g.is_dag())
        g = Graph.Barabasi(1000, 2, directed=True)
        self.assertTrue(g.is_dag())
        g = Graph.GRG(100, 0.2)
        self.assertFalse(g.is_dag())
        g = Graph.Ring(10, directed=True, mutual=False)
        self.assertFalse(g.is_dag())

    def test_fundamental_cycles(self):
        g = Graph(
            [
                (1, 2),
                (2, 3),
                (3, 1),
                (4, 5),
                (5, 4),
                (4, 5),
                (6, 7),
                (7, 8),
                (8, 9),
                (9, 6),
                (6, 8),
                (10, 10),
                (10, 11),
                (12, 12),
            ]
        )
        cycles = [sorted(cycle) for cycle in g.fundamental_cycles()]
        assert cycles == [[0, 1, 2], [4, 5], [3, 5], [6, 7, 10], [8, 9, 10], [11], [13]]

        cycles = [sorted(cycle) for cycle in g.fundamental_cycles(start_vid=6)]
        assert cycles == [[6, 7, 10], [8, 9, 10]]

        cycles = [
            sorted(cycle) for cycle in g.fundamental_cycles(start_vid=6, cutoff=1)
        ]
        assert cycles == [[6, 7, 10], [8, 9, 10]]

    def test_simple_cycles(self):
        g = Graph(
            [
                (0, 1),
                (1, 2),
                (2, 0),
                (0, 0),
                (0, 3),
                (3, 4),
                (4, 5),
                (5, 0),
            ]
        )

        vertices = g.simple_cycles(output="vpath")
        edges = g.simple_cycles(output="epath")
        assert len(vertices) == 3
        assert len(edges) == 3

    def test_minimum_cycle_basis(self):
        g = Graph(
            [
                (1, 2),
                (2, 3),
                (3, 1),
                (4, 5),
                (5, 4),
                (4, 5),
                (6, 7),
                (7, 8),
                (8, 9),
                (9, 6),
                (6, 8),
                (10, 10),
                (10, 11),
                (12, 12),
            ]
        )
        cycles = g.minimum_cycle_basis()
        assert cycles == [
            (11,),
            (13,),
            (3, 5),
            (4, 5),
            (0, 1, 2),
            (6, 7, 10),
            (8, 9, 10),
        ]

        g = Graph.Lattice((5, 6), circular=True)
        cycles = g.minimum_cycle_basis()
        expected = [
            (0, 1, 10, 3),
            (0, 51, 50, 53),
            (1, 8, 9, 18),
            (2, 3, 12, 5),
            (2, 53, 52, 55),
            (4, 5, 14, 7),
            (4, 55, 54, 57),
            (6, 7, 16, 9),
            (6, 57, 56, 59),
            (8, 59, 58, 51),
            (10, 11, 20, 13),
            (11, 18, 19, 28),
            (12, 13, 22, 15),
            (14, 15, 24, 17),
            (16, 17, 26, 19),
            (20, 21, 30, 23),
            (21, 28, 29, 38),
            (22, 23, 32, 25),
            (24, 25, 34, 27),
            (26, 27, 36, 29),
            (30, 31, 40, 33),
            (31, 38, 39, 48),
            (32, 33, 42, 35),
            (34, 35, 44, 37),
            (36, 37, 46, 39),
            (40, 41, 50, 43),
            (41, 48, 49, 58),
            (42, 43, 52, 45),
            (44, 45, 54, 47),
            (0, 8, 6, 4, 2),
            (1, 51, 41, 31, 21, 11),
        ]
        assert len(cycles) == len(expected)
        for expected_cycle, observed_cycle in zip(expected, cycles):
            assert expected_cycle == observed_cycle or expected_cycle == (
                observed_cycle[0],
            ) + tuple(reversed(observed_cycle[1:]))

        g = Graph.Lattice((5, 6), circular=True)
        cycles = g.minimum_cycle_basis(cutoff=2, complete=False)
        expected = [
            (0, 1, 10, 3),
            (0, 51, 50, 53),
            (1, 8, 9, 18),
            (2, 3, 12, 5),
            (2, 53, 52, 55),
            (4, 5, 14, 7),
            (4, 55, 54, 57),
            (6, 7, 16, 9),
            (6, 57, 56, 59),
            (8, 59, 58, 51),
            (10, 11, 20, 13),
            (11, 18, 19, 28),
            (12, 13, 22, 15),
            (14, 15, 24, 17),
            (16, 17, 26, 19),
            (20, 21, 30, 23),
            (21, 28, 29, 38),
            (22, 23, 32, 25),
            (24, 25, 34, 27),
            (26, 27, 36, 29),
            (30, 31, 40, 33),
            (31, 38, 39, 48),
            (32, 33, 42, 35),
            (34, 35, 44, 37),
            (36, 37, 46, 39),
            (40, 41, 50, 43),
            (41, 48, 49, 58),
            (42, 43, 52, 45),
            (44, 45, 54, 47),
            (0, 8, 6, 4, 2),
            (1, 51, 41, 31, 21, 11),
        ]
        assert len(cycles) == len(expected) - 1
        for expected_cycle, observed_cycle in zip(expected[:-1], cycles):
            assert expected_cycle == observed_cycle or expected_cycle == (
                observed_cycle[0],
            ) + tuple(reversed(observed_cycle[1:]))


def suite():
    cycle_suite = unittest.defaultTestLoader.loadTestsFromTestCase(CycleTests)
    return unittest.TestSuite([cycle_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
