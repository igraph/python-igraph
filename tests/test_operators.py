import unittest

from igraph import *

try:
    import numpy as np
except ImportError:
    np = None


class OperatorTests(unittest.TestCase):
    def testComplementer(self):
        g = Graph.Full(3)
        g2 = g.complementer()
        self.assertTrue(g2.vcount() == 3 and g2.ecount() == 3)
        self.assertTrue(sorted(g2.get_edgelist()) == [(0, 0), (1, 1), (2, 2)])

        g = Graph.Full(3) + Graph.Full(2)
        g2 = g.complementer(False)
        self.assertTrue(
            sorted(g2.get_edgelist())
            == [(0, 3), (0, 4), (1, 3), (1, 4), (2, 3), (2, 4)]
        )

        g2 = g.complementer(loops=True)
        self.assertTrue(
            sorted(g2.get_edgelist())
            == [
                (0, 0),
                (0, 3),
                (0, 4),
                (1, 1),
                (1, 3),
                (1, 4),
                (2, 2),
                (2, 3),
                (2, 4),
                (3, 3),
                (4, 4),
            ]
        )

    def testMultiplication(self):
        g = Graph.Full(3) * 3
        self.assertTrue(
            g.vcount() == 9
            and g.ecount() == 9
            and g.clusters().membership == [0, 0, 0, 1, 1, 1, 2, 2, 2]
        )

    def testDifference(self):
        g = Graph.Tree(7, 2) - Graph.Lattice([7])
        self.assertTrue(g.vcount() == 7 and g.ecount() == 5)
        self.assertTrue(
            sorted(g.get_edgelist()) == [(0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
        )

    def testDifferenceWithSelfLoop(self):
        # https://github.com/igraph/igraph/issues/597#
        g = Graph.Ring(10) + [(0, 0)]
        g -= Graph.Ring(5)
        self.assertTrue(g.vcount() == 10 and g.ecount() == 7)
        self.assertTrue(
            sorted(g.get_edgelist())
            == [(0, 0), (0, 9), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
        )

    def testIntersection(self):
        g = Graph.Tree(7, 2) & Graph.Lattice([7])
        self.assertTrue(g.get_edgelist() == [(0, 1)])

    def testIntersectionMethod(self):
        g = Graph.Tree(7, 2).intersection(Graph.Lattice([7]))
        self.assertTrue(g.get_edgelist() == [(0, 1)])

    def testIntersectionNoGraphs(self):
        self.assertRaises(ValueError, intersection, [])

    def testIntersectionSingle(self):
        g1 = Graph.Tree(7, 2)
        g = intersection([g1])
        self.assertTrue(g != g1)
        self.assertTrue(g.vcount() == g1.vcount() and g.ecount() == g1.ecount())
        self.assertTrue(g.is_directed() == g1.is_directed())
        self.assertTrue(g.get_edgelist() == g1.get_edgelist())

    def testDisjointUnion(self):
        g1 = Graph.Tree(7, 2)
        g2 = Graph.Lattice([7])

        # Method
        g = g1.disjoint_union(g2)
        self.assertTrue(g.vcount() == 14 and g.ecount() == 13)

        # Module function
        g = disjoint_union([g1, g2])
        self.assertTrue(g.vcount() == 14 and g.ecount() == 13)

    def testDisjointUnionNoGraphs(self):
        self.assertRaises(ValueError, disjoint_union, [])

    def testDisjointUnionSingle(self):
        g1 = Graph.Tree(7, 2)
        g = disjoint_union([g1])
        self.assertTrue(g != g1)
        self.assertTrue(g.vcount() == g1.vcount() and g.ecount() == g1.ecount())
        self.assertTrue(g.is_directed() == g1.is_directed())
        self.assertTrue(g.get_edgelist() == g1.get_edgelist())

    def testUnion(self):
        g = Graph.Tree(7, 2) | Graph.Lattice([7])
        self.assertTrue(g.vcount() == 7 and g.ecount() == 12)
        self.assertTrue(
            sorted(g.get_edgelist())
            == [
                (0, 1),
                (0, 2),
                (0, 6),
                (1, 2),
                (1, 3),
                (1, 4),
                (2, 3),
                (2, 5),
                (2, 6),
                (3, 4),
                (4, 5),
                (5, 6),
            ]
        )

    def testUnionWithConflict(self):
        g1 = Graph.Tree(7, 2)
        g1['name'] = 'Tree'
        g2 = Graph.Lattice([7])
        g2['name'] = 'Lattice'
        g = union([g1, g2]) # Issue 422
        self.assertTrue(
            sorted(g.get_edgelist())
            == [
                (0, 1),
                (0, 2),
                (0, 6),
                (1, 2),
                (1, 3),
                (1, 4),
                (2, 3),
                (2, 5),
                (2, 6),
                (3, 4),
                (4, 5),
                (5, 6),
            ]
        )
        self.assertTrue(
            sorted(g.attributes()),
            ['name_1', 'name_2'],
        )

    def testUnionMethod(self):
        g = Graph.Tree(7, 2).union(Graph.Lattice([7]))
        self.assertTrue(g.vcount() == 7 and g.ecount() == 12)

    def testUnionNoGraphs(self):
        self.assertRaises(ValueError, union, [])

    def testUnionSingle(self):
        g1 = Graph.Tree(7, 2)
        g = union([g1])
        self.assertTrue(g != g1)
        self.assertTrue(g.vcount() == g1.vcount() and g.ecount() == g1.ecount())
        self.assertTrue(g.is_directed() == g1.is_directed())
        self.assertTrue(g.get_edgelist() == g1.get_edgelist())

    def testUnionMany(self):
        gs = [Graph.Tree(7, 2), Graph.Lattice([7]), Graph.Lattice([7])]
        g = union(gs)
        self.assertTrue(g.vcount() == 7 and g.ecount() == 12)

    def testUnionManyAttributes(self):
        gs = [
            Graph.Formula("A-B"),
            Graph.Formula("A-B,C-D"),
        ]
        gs[0]["attr"] = "graph1"
        gs[0].vs["attr"] = ["set", "set_too"]
        gs[0].vs["attr2"] = ["set", "set_too"]
        gs[1].vs[0]["attr"] = "set"
        gs[1].vs[0]["attr2"] = "conflict"
        g = union(gs)
        names = g.vs["name"]
        self.assertTrue(g["attr"] == "graph1")
        self.assertTrue(g.vs[names.index("A")]["attr"] == "set")
        self.assertTrue(g.vs[names.index("B")]["attr"] == "set_too")
        self.assertTrue(g.ecount() == 2)
        self.assertTrue(
            sorted(g.vertex_attributes()) == ["attr", "attr2_1", "attr2_2", "name"]
        )

    def testUnionManyEdgemap(self):
        gs = [
            Graph.Formula("A-B"),
            Graph.Formula("C-D, A-B"),
        ]
        gs[0].es[0]["attr"] = "set"
        gs[1].es[0]["attr"] = "set_too"
        g = union(gs)
        for e in g.es:
            vnames = [g.vs[e.source]["name"], g.vs[e.target]["name"]]
            if set(vnames) == set(["A", "B"]):
                self.assertTrue(e["attr"] == "set")
            else:
                self.assertTrue(e["attr"] == "set_too")

    def testIntersectionNoGraphs(self):
        self.assertRaises(ValueError, intersection, [])

    def testIntersectionSingle(self):
        g1 = Graph.Tree(7, 2)
        g = intersection([g1])
        self.assertTrue(g != g1)
        self.assertTrue(g.vcount() == g1.vcount() and g.ecount() == g1.ecount())
        self.assertTrue(g.is_directed() == g1.is_directed())
        self.assertTrue(g.get_edgelist() == g1.get_edgelist())

    def testIntersectionMany(self):
        gs = [Graph.Tree(7, 2), Graph.Lattice([7])]
        g = intersection(gs)
        self.assertTrue(g.get_edgelist() == [(0, 1)])

    def testIntersectionManyAttributes(self):
        gs = [Graph.Tree(7, 2), Graph.Lattice([7])]
        gs[0]["attr"] = "graph1"
        gs[0].vs["name"] = ["one", "two", "three", "four", "five", "six", "7"]
        gs[1].vs["name"] = ["one", "two", "three", "four", "five", "six", "7"]
        gs[0].vs[0]["attr"] = "set"
        gs[1].vs[5]["attr"] = "set_too"
        g = intersection(gs)
        names = g.vs["name"]
        self.assertTrue(g["attr"] == "graph1")
        self.assertTrue(g.vs[names.index("one")]["attr"] == "set")
        self.assertTrue(g.vs[names.index("six")]["attr"] == "set_too")
        self.assertTrue(g.ecount() == 1)
        self.assertTrue(
            set(g.get_edgelist()[0]) == set([names.index("one"), names.index("two")]),
        )

    def testIntersectionManyEdgemap(self):
        gs = [
            Graph.Formula("A-B"),
            Graph.Formula("A-B,C-D"),
        ]
        gs[0].es[0]["attr"] = "set"
        gs[1].es[1]["attr"] = "set_too"
        g = intersection(gs)
        self.assertTrue(g.es["attr"] == ["set"])

    def testInPlaceAddition(self):
        g = Graph.Full(3)
        orig = g

        # Adding vertices
        g += 2
        self.assertTrue(
            g.vcount() == 5
            and g.ecount() == 3
            and g.clusters().membership == [0, 0, 0, 1, 2]
        )

        # Adding a vertex by name
        g += "spam"
        self.assertTrue(
            g.vcount() == 6
            and g.ecount() == 3
            and g.clusters().membership == [0, 0, 0, 1, 2, 3]
        )

        # Adding a single edge
        g += (2, 3)
        self.assertTrue(
            g.vcount() == 6
            and g.ecount() == 4
            and g.clusters().membership == [0, 0, 0, 0, 1, 2]
        )

        # Adding two edges
        g += [(3, 4), (2, 4), (4, 5)]
        self.assertTrue(
            g.vcount() == 6 and g.ecount() == 7 and g.clusters().membership == [0] * 6
        )

        # Adding two more vertices
        g += ["eggs", "bacon"]
        self.assertEqual(
            g.vs["name"], [None, None, None, None, None, "spam", "eggs", "bacon"]
        )

        # Did we really use the original graph so far?
        # TODO: disjoint union should be modified so that this assertion
        # could be moved to the end
        self.assertTrue(id(g) == id(orig))

        # Adding another graph
        g += Graph.Full(3)
        self.assertTrue(
            g.vcount() == 11
            and g.ecount() == 10
            and g.clusters().membership == [0, 0, 0, 0, 0, 0, 1, 2, 3, 3, 3]
        )

        # Adding two graphs
        g += [Graph.Full(3), Graph.Full(2)]
        self.assertTrue(
            g.vcount() == 16
            and g.ecount() == 14
            and g.clusters().membership
            == [0, 0, 0, 0, 0, 0, 1, 2, 3, 3, 3, 4, 4, 4, 5, 5]
        )

    def testAddition(self):
        g0 = Graph.Full(3)

        # Adding vertices
        g = g0 + 2
        self.assertTrue(
            g.vcount() == 5
            and g.ecount() == 3
            and g.clusters().membership == [0, 0, 0, 1, 2]
        )
        g0 = g

        # Adding vertices by name
        g = g0 + "spam"
        self.assertTrue(
            g.vcount() == 6
            and g.ecount() == 3
            and g.clusters().membership == [0, 0, 0, 1, 2, 3]
        )
        g0 = g

        # Adding a single edge
        g = g0 + (2, 3)
        self.assertTrue(
            g.vcount() == 6
            and g.ecount() == 4
            and g.clusters().membership == [0, 0, 0, 0, 1, 2]
        )
        g0 = g

        # Adding two edges
        g = g0 + [(3, 4), (2, 4), (4, 5)]
        self.assertTrue(
            g.vcount() == 6 and g.ecount() == 7 and g.clusters().membership == [0] * 6
        )
        g0 = g

        # Adding another graph
        g = g0 + Graph.Full(3)
        self.assertTrue(
            g.vcount() == 9
            and g.ecount() == 10
            and g.clusters().membership == [0, 0, 0, 0, 0, 0, 1, 1, 1]
        )

    def testInPlaceSubtraction(self):
        g = Graph.Full(8)
        orig = g

        # Deleting a vertex by vertex selector
        g -= 7
        self.assertTrue(
            g.vcount() == 7
            and g.ecount() == 21
            and g.clusters().membership == [0, 0, 0, 0, 0, 0, 0]
        )

        # Deleting a vertex
        g -= g.vs[6]
        self.assertTrue(
            g.vcount() == 6
            and g.ecount() == 15
            and g.clusters().membership == [0, 0, 0, 0, 0, 0]
        )

        # Deleting two vertices
        g -= [4, 5]
        self.assertTrue(
            g.vcount() == 4
            and g.ecount() == 6
            and g.clusters().membership == [0, 0, 0, 0]
        )

        # Deleting an edge
        g -= (1, 2)
        self.assertTrue(
            g.vcount() == 4
            and g.ecount() == 5
            and g.clusters().membership == [0, 0, 0, 0]
        )

        # Deleting three more edges
        g -= [(1, 3), (0, 2), (0, 3)]
        self.assertTrue(
            g.vcount() == 4
            and g.ecount() == 2
            and g.clusters().membership == [0, 0, 1, 1]
        )

        # Did we really use the original graph so far?
        self.assertTrue(id(g) == id(orig))

        # Subtracting a graph
        g2 = Graph.Tree(3, 2)
        g -= g2
        self.assertTrue(
            g.vcount() == 4
            and g.ecount() == 1
            and g.clusters().membership == [0, 1, 2, 2]
        )

    def testNonzero(self):
        self.assertTrue(Graph(1))
        self.assertFalse(Graph(0))

    def testLength(self):
        self.assertRaises(TypeError, len, Graph(15))
        self.assertTrue(len(Graph(15).vs) == 15)
        self.assertTrue(len(Graph.Full(5).es) == 10)

    def testSimplify(self):
        el = [(0, 1), (1, 0), (1, 2), (2, 3), (2, 3), (2, 3), (3, 3)]
        g = Graph(el)
        g.es["weight"] = [1, 2, 3, 4, 5, 6, 7]

        g2 = g.copy()
        g2.simplify()
        self.assertTrue(g2.vcount() == g.vcount())
        self.assertTrue(g2.ecount() == 3)

        g2 = g.copy()
        g2.simplify(loops=False)
        self.assertTrue(g2.vcount() == g.vcount())
        self.assertTrue(g2.ecount() == 4)

        g2 = g.copy()
        g2.simplify(multiple=False)
        self.assertTrue(g2.vcount() == g.vcount())
        self.assertTrue(g2.ecount() == g.ecount() - 1)

    def testContractVertices(self):
        g = Graph.Full(4) + Graph.Full(4) + [(0, 5), (1, 4)]

        g2 = g.copy()
        g2.contract_vertices([0, 1, 2, 3, 1, 0, 4, 5])
        self.assertEqual(g2.vcount(), 6)
        self.assertEqual(g2.ecount(), g.ecount())
        self.assertEqual(
            sorted(g2.get_edgelist()),
            [
                (0, 0),
                (0, 1),
                (0, 1),
                (0, 2),
                (0, 3),
                (0, 4),
                (0, 5),
                (1, 1),
                (1, 2),
                (1, 3),
                (1, 4),
                (1, 5),
                (2, 3),
                (4, 5),
            ],
        )

        g2 = g.copy()
        g2.contract_vertices([0, 1, 2, 3, 1, 0, 6, 7])
        self.assertEqual(g2.vcount(), 8)
        self.assertEqual(g2.ecount(), g.ecount())
        self.assertEqual(
            sorted(g2.get_edgelist()),
            [
                (0, 0),
                (0, 1),
                (0, 1),
                (0, 2),
                (0, 3),
                (0, 6),
                (0, 7),
                (1, 1),
                (1, 2),
                (1, 3),
                (1, 6),
                (1, 7),
                (2, 3),
                (6, 7),
            ],
        )

        g2 = Graph(10)
        g2.contract_vertices([0, 0, 1, 1, 2, 2, 3, 3, 4, 4])
        self.assertEqual(g2.vcount(), 5)
        self.assertEqual(g2.ecount(), 0)

    @unittest.skipIf(np is None, "test case depends on NumPy")
    def testContractVerticesWithNumPyIntegers(self):
        g = Graph.Full(4) + Graph.Full(4) + [(0, 5), (1, 4)]
        g2 = g.copy()
        g2.contract_vertices([np.int32(x) for x in [0, 1, 2, 3, 1, 0, 6, 7]])
        self.assertEqual(g2.vcount(), 8)
        self.assertEqual(g2.ecount(), g.ecount())
        self.assertEqual(
            sorted(g2.get_edgelist()),
            [
                (0, 0),
                (0, 1),
                (0, 1),
                (0, 2),
                (0, 3),
                (0, 6),
                (0, 7),
                (1, 1),
                (1, 2),
                (1, 3),
                (1, 6),
                (1, 7),
                (2, 3),
                (6, 7),
            ],
        )


def suite():
    operator_suite = unittest.makeSuite(OperatorTests)
    return unittest.TestSuite([operator_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
