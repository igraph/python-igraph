import unittest

from igraph import Graph, InternalError


try:
    import numpy as np
except ImportError:
    np = None

try:
    import scipy.sparse as sparse
except ImportError:
    sparse = None

try:
    import pandas as pd
except ImportError:
    pd = None


class GeneratorTests(unittest.TestCase):
    def testStar(self):
        g = Graph.Star(5, "in")
        el = [(1, 0), (2, 0), (3, 0), (4, 0)]
        self.assertTrue(g.is_directed())
        self.assertTrue(g.get_edgelist() == el)
        g = Graph.Star(5, "out", center=2)
        el = [(2, 0), (2, 1), (2, 3), (2, 4)]
        self.assertTrue(g.is_directed())
        self.assertTrue(g.get_edgelist() == el)
        g = Graph.Star(5, "mutual", center=2)
        el = [(0, 2), (1, 2), (2, 0), (2, 1), (2, 3), (2, 4), (3, 2), (4, 2)]
        self.assertTrue(g.is_directed())
        self.assertTrue(sorted(g.get_edgelist()) == el)
        g = Graph.Star(5, center=3)
        el = [(0, 3), (1, 3), (2, 3), (3, 4)]
        self.assertTrue(not g.is_directed())
        self.assertTrue(sorted(g.get_edgelist()) == el)

    def testFamous(self):
        g = Graph.Famous("tutte")
        self.assertTrue(g.vcount() == 46 and g.ecount() == 69)
        self.assertRaises(InternalError, Graph.Famous, "unknown")

    def testFormula(self):
        tests = [
            (None, [], []),
            ("", [""], []),
            ("A", ["A"], []),
            ("A-B", ["A", "B"], [(0, 1)]),
            ("A --- B", ["A", "B"], [(0, 1)]),
            (
                "A--B, C--D, E--F, G--H, I, J, K",
                ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"],
                [(0, 1), (2, 3), (4, 5), (6, 7)],
            ),
            (
                "A:B:C:D -- A:B:C:D",
                ["A", "B", "C", "D"],
                [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
            ),
            ("A -> B -> C", ["A", "B", "C"], [(0, 1), (1, 2)]),
            ("A <- B -> C", ["A", "B", "C"], [(1, 0), (1, 2)]),
            ("A <- B -- C", ["A", "B", "C"], [(1, 0)]),
            (
                "A <-> B <---> C <> D",
                ["A", "B", "C", "D"],
                [(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2)],
            ),
            (
                "'this is' <- 'a silly' -> 'graph here'",
                ["this is", "a silly", "graph here"],
                [(1, 0), (1, 2)],
            ),
            (
                "Alice-Bob-Cecil-Alice, Daniel-Cecil-Eugene, Cecil-Gordon",
                ["Alice", "Bob", "Cecil", "Daniel", "Eugene", "Gordon"],
                [(0, 1), (1, 2), (0, 2), (2, 3), (2, 4), (2, 5)],
            ),
            (
                "Alice-Bob:Cecil:Daniel, Cecil:Daniel-Eugene:Gordon",
                ["Alice", "Bob", "Cecil", "Daniel", "Eugene", "Gordon"],
                [(0, 1), (0, 2), (0, 3), (2, 4), (2, 5), (3, 4), (3, 5)],
            ),
            (
                "Alice <-> Bob --> Cecil <-- Daniel, Eugene --> Gordon:Helen",
                ["Alice", "Bob", "Cecil", "Daniel", "Eugene", "Gordon", "Helen"],
                [(0, 1), (1, 0), (1, 2), (3, 2), (4, 5), (4, 6)],
            ),
            (
                "Alice -- Bob -- Daniel, Cecil:Gordon, Helen",
                ["Alice", "Bob", "Daniel", "Cecil", "Gordon", "Helen"],
                [(0, 1), (1, 2)],
            ),
            (
                '"+" -- "-", "*" -- "/", "%%" -- "%/%"',
                ["+", "-", "*", "/", "%%", "%/%"],
                [(0, 1), (2, 3), (4, 5)],
            ),
            ("A-B-C\nC-D", ["A", "B", "C", "D"], [(0, 1), (1, 2), (2, 3)]),
            ("A-B-C\n    C-D", ["A", "B", "C", "D"], [(0, 1), (1, 2), (2, 3)]),
        ]
        for formula, names, edges in tests:
            g = Graph.Formula(formula)
            self.assertEqual(g.vs["name"], names)
            self.assertEqual(g.get_edgelist(), sorted(edges))

    def testFull(self):
        g = Graph.Full(20, directed=True)
        el = g.get_edgelist()
        el.sort()
        self.assertTrue(
            g.get_edgelist() == [(x, y) for x in range(20) for y in range(20) if x != y]
        )

    def testFullCitation(self):
        g = Graph.Full_Citation(20)
        el = g.get_edgelist()
        el.sort()
        self.assertTrue(not g.is_directed())
        self.assertTrue(el == [(x, y) for x in range(19) for y in range(x + 1, 20)])

        g = Graph.Full_Citation(20, True)
        el = g.get_edgelist()
        el.sort()
        self.assertTrue(g.is_directed())
        self.assertTrue(el == [(x, y) for x in range(1, 20) for y in range(x)])

        self.assertRaises(InternalError, Graph.Full_Citation, -2)

    def testLCF(self):
        g1 = Graph.LCF(12, (5, -5), 6)
        g2 = Graph.Famous("Franklin")
        self.assertTrue(g1.isomorphic(g2))
        self.assertRaises(InternalError, Graph.LCF, 12, (5, -5), -3)

    def testRealizeDegreeSequence(self):
        # Test case insensitivity of options too
        g = Graph.Realize_Degree_Sequence(
            [1, 1], None, "simPLE", "smallest",
        )
        self.assertFalse(g.is_directed())
        self.assertTrue(g.degree() == [1, 1])

        # Not implemented, should fail
        self.assertRaises(
            NotImplementedError, Graph.Realize_Degree_Sequence,
            [1, 1], None, "loops", "largest"
        )

        g = Graph.Realize_Degree_Sequence(
            [1, 1], None, "all", "largest",
        )
        self.assertFalse(g.is_directed())
        self.assertTrue(g.degree() == [1, 1])

        g = Graph.Realize_Degree_Sequence(
            [1, 1], None, "multi", "index",
        )
        self.assertFalse(g.is_directed())
        self.assertTrue(g.degree() == [1, 1])

        g = Graph.Realize_Degree_Sequence(
            [1, 1], [1, 1], "simple", "largest",
        )
        self.assertTrue(g.is_directed())
        self.assertTrue(g.indegree() == [1, 1])
        self.assertTrue(g.outdegree() == [1, 1])

        # Not implemented, should fail
        self.assertRaises(
            NotImplementedError, Graph.Realize_Degree_Sequence,
            [1, 1], [1, 1], "multi", "largest"
        )

        self.assertRaises(
            ValueError, Graph.Realize_Degree_Sequence,
            [1, 1], [1, 1], "should_fail", "index"
        )
        self.assertRaises(
            ValueError, Graph.Realize_Degree_Sequence,
            [1, 1], [1, 1], "multi", "should_fail"
        )

        # Degree sequence of Zachary karate club, using optional arguments
        zachary = Graph.Famous("zachary")
        degrees = zachary.degree()
        g = Graph.Realize_Degree_Sequence(degrees)
        self.assertFalse(g.is_directed())
        self.assertTrue(g.degree() == degrees)

    def testKautz(self):
        g = Graph.Kautz(2, 2)
        deg_in = g.degree(mode="in")
        deg_out = g.degree(mode="out")
        # This is not a proper test, but should spot most errors
        self.assertTrue(g.is_directed() and deg_in == [2] * 12 and deg_out == [2] * 12)

    def testDeBruijn(self):
        g = Graph.De_Bruijn(2, 3)
        deg_in = g.degree(mode="in", loops=True)
        deg_out = g.degree(mode="out", loops=True)
        # This is not a proper test, but should spot most errors
        self.assertTrue(g.is_directed() and deg_in == [2] * 8 and deg_out == [2] * 8)

    def testSBM(self):
        pref_matrix = [[0.5, 0, 0], [0, 0, 0.5], [0, 0.5, 0]]
        n = 60
        types = [20, 20, 20]
        g = Graph.SBM(n, pref_matrix, types)

        # Simple smoke tests for the expected structure of the graph
        self.assertTrue(g.is_simple())
        self.assertFalse(g.is_directed())
        self.assertEqual([0] * 20 + [1] * 40, g.clusters().membership)
        g2 = g.subgraph(list(range(20, 60)))
        self.assertTrue(not any(e.source // 20 == e.target // 20 for e in g2.es))

        # Check loops argument
        g = Graph.SBM(n, pref_matrix, types, loops=True)
        self.assertFalse(g.is_simple())
        self.assertTrue(sum(g.is_loop()) > 0)

        # Check directedness
        g = Graph.SBM(n, pref_matrix, types, directed=True)
        self.assertTrue(g.is_directed())
        self.assertTrue(sum(g.is_mutual()) < g.ecount())
        self.assertTrue(sum(g.is_loop()) == 0)

        # Check error conditions
        self.assertRaises(InternalError, Graph.SBM, -1, pref_matrix, types)
        self.assertRaises(InternalError, Graph.SBM, 61, pref_matrix, types)
        pref_matrix[0][1] = 0.7
        self.assertRaises(InternalError, Graph.SBM, 60, pref_matrix, types)

    @unittest.skipIf(np is None, "test case depends on NumPy")
    def testAdjacencyNumPy(self):
        mat = np.array(
            [[0, 1, 1, 0], [1, 0, 0, 0], [0, 0, 2, 0], [0, 1, 0, 0]],
        )

        # ADJ_DIRECTED (default)
        g = Graph.Adjacency(mat)
        el = g.get_edgelist()
        self.assertTrue(el == [(0, 1), (0, 2), (1, 0), (2, 2), (2, 2), (3, 1)])

        # ADJ MIN
        g = Graph.Adjacency(mat, mode="min")
        el = g.get_edgelist()
        self.assertTrue(el == [(0, 1), (2, 2), (2, 2)])

        # ADJ LOWER
        g = Graph.Adjacency(mat, mode="lower")
        el = g.get_edgelist()
        self.assertTrue(el == [(0, 1), (2, 2), (2, 2), (1, 3)])

    @unittest.skipIf(
        (sparse is None) or (np is None), "test case depends on NumPy/SciPy"
    )
    def testSparseAdjacency(self):
        mat = sparse.coo_matrix(
            [[0, 1, 1, 0], [1, 0, 0, 0], [0, 0, 2, 0], [0, 1, 0, 0]],
        )

        # ADJ_DIRECTED (default)
        g = Graph.Adjacency(mat)
        el = g.get_edgelist()
        self.assertTrue(g.is_directed())
        self.assertEqual(4, g.vcount())
        self.assertTrue(el == [(0, 1), (0, 2), (1, 0), (2, 2), (2, 2), (3, 1)])

        # ADJ MIN
        g = Graph.Adjacency(mat, mode="min")
        el = g.get_edgelist()
        self.assertFalse(g.is_directed())
        self.assertEqual(4, g.vcount())
        self.assertTrue(el == [(0, 1), (2, 2), (2, 2)])

        # ADJ LOWER
        g = Graph.Adjacency(mat, mode="lower")
        el = g.get_edgelist()
        self.assertFalse(g.is_directed())
        self.assertEqual(4, g.vcount())
        self.assertTrue(el == [(0, 1), (2, 2), (2, 2), (1, 3)])

    def testWeightedAdjacency(self):
        mat = [[0, 1, 2, 0], [2, 0, 0, 0], [0, 0, 2.5, 0], [0, 1, 0, 0]]

        g = Graph.Weighted_Adjacency(mat, attr="w0")
        el = g.get_edgelist()
        self.assertTrue(el == [(0, 1), (0, 2), (1, 0), (2, 2), (3, 1)])
        self.assertTrue(g.es["w0"] == [1, 2, 2, 2.5, 1])

        g = Graph.Weighted_Adjacency(mat, mode="plus")
        el = g.get_edgelist()
        self.assertTrue(el == [(0, 1), (0, 2), (1, 3), (2, 2)])
        self.assertTrue(g.es["weight"] == [3, 2, 1, 2.5])

        g = Graph.Weighted_Adjacency(mat, attr="w0", loops=False)
        el = g.get_edgelist()
        self.assertTrue(el == [(0, 1), (0, 2), (1, 0), (3, 1)])
        self.assertTrue(g.es["w0"] == [1, 2, 2, 1])

    @unittest.skipIf(np is None, "test case depends on NumPy")
    def testWeightedAdjacencyNumPy(self):
        mat = np.array(
            [[0, 1, 2, 0], [2, 0, 0, 0], [0, 0, 2.5, 0], [0, 1, 0, 0]],
        )

        g = Graph.Weighted_Adjacency(mat, attr="w0")
        el = g.get_edgelist()
        self.assertTrue(el == [(0, 1), (0, 2), (1, 0), (2, 2), (3, 1)])
        self.assertTrue(g.es["w0"] == [1, 2, 2, 2.5, 1])

        g = Graph.Weighted_Adjacency(mat, mode="plus")
        el = g.get_edgelist()
        self.assertTrue(el == [(0, 1), (0, 2), (1, 3), (2, 2)])
        self.assertTrue(g.es["weight"] == [3, 2, 1, 2.5])

        g = Graph.Weighted_Adjacency(mat, attr="w0", loops=False)
        el = g.get_edgelist()
        self.assertTrue(el == [(0, 1), (0, 2), (1, 0), (3, 1)])
        self.assertTrue(g.es["w0"] == [1, 2, 2, 1])

    @unittest.skipIf(
        (sparse is None) or (np is None), "test case depends on NumPy/SciPy"
    )
    def testSparseWeighedAdjacency(self):
        mat = sparse.coo_matrix(
            [[0, 1, 2, 0], [2, 0, 0, 0], [0, 0, 2.5, 0], [0, 1, 0, 0]]
        )

        g = Graph.Weighted_Adjacency(mat, attr="w0")
        el = g.get_edgelist()
        self.assertTrue(g.is_directed())
        self.assertEqual(4, g.vcount())
        self.assertTrue(el == [(0, 1), (0, 2), (1, 0), (2, 2), (3, 1)])
        self.assertTrue(g.es["w0"] == [1, 2, 2, 2.5, 1])

        g = Graph.Weighted_Adjacency(mat, mode="plus")
        el = g.get_edgelist()
        self.assertFalse(g.is_directed())
        self.assertEqual(4, g.vcount())
        self.assertTrue(el == [(0, 1), (0, 2), (2, 2), (1, 3)])
        self.assertTrue(g.es["weight"] == [3, 2, 2.5, 1])

        g = Graph.Weighted_Adjacency(mat, mode="min")
        el = g.get_edgelist()
        self.assertFalse(g.is_directed())
        self.assertEqual(4, g.vcount())
        self.assertTrue(el == [(0, 1), (2, 2)])
        self.assertTrue(g.es["weight"] == [1, 2.5])

        g = Graph.Weighted_Adjacency(mat, attr="w0", loops=False)
        el = g.get_edgelist()
        self.assertTrue(g.is_directed())
        self.assertEqual(4, g.vcount())
        self.assertTrue(el == [(0, 1), (0, 2), (1, 0), (3, 1)])
        self.assertTrue(g.es["w0"] == [1, 2, 2, 1])

    @unittest.skipIf((np is None) or (pd is None), "test case depends on NumPy/Pandas")
    def testDataFrame(self):
        edges = pd.DataFrame(
            [["C", "A", 0.4], ["A", "B", 0.1]], columns=[0, 1, "weight"]
        )
        g = Graph.DataFrame(edges, directed=False)
        self.assertTrue(g.es["weight"] == [0.4, 0.1])

        vertices = pd.DataFrame(
            [["A", "blue"], ["B", "yellow"], ["C", "blue"]], columns=[0, "color"]
        )
        g = Graph.DataFrame(edges, directed=True, vertices=vertices)
        self.assertTrue(g.vs["name"] == ["A", "B", "C"])
        self.assertTrue(g.vs["color"] == ["blue", "yellow", "blue"])
        self.assertTrue(g.es["weight"] == [0.4, 0.1])

        # Issue #347
        edges = pd.DataFrame({"source": [1, 2, 3], "target": [4, 5, 6]})
        vertices = pd.DataFrame(
            {"node": [1, 2, 3, 4, 5, 6], "label": ["1", "2", "3", "4", "5", "6"]}
        )[["node", "label"]]
        g = Graph.DataFrame(
            edges,
            directed=True,
            vertices=vertices
        )
        self.assertTrue(g.vs["name"] == [1, 2, 3, 4, 5, 6])
        self.assertTrue(g.vs["label"] == ["1", "2", "3", "4", "5", "6"])

        # Vertex ids
        edges = pd.DataFrame({"source": [1, 2, 3], "target": [4, 5, 6]})
        g = Graph.DataFrame(edges)
        self.assertTrue(g.vcount() == 6)

        edges = pd.DataFrame({"source": [1, 2, 3], "target": [4, 5, 6]})
        g = Graph.DataFrame(edges, use_vids=True)
        self.assertTrue(g.vcount() == 7)

        # Graph clone
        g = Graph.Full(n=100, directed=True, loops=True)
        g.vs["name"] = [f"v{i}" for i in range(g.vcount())]
        g.vs["x"] = [float(i) for i in range(g.vcount())]
        g.es["w"] = [1.0] * g.ecount()
        df_edges = g.get_edge_dataframe()
        df_vertices = g.get_vertex_dataframe()
        g_clone = Graph.DataFrame(df_edges, g.is_directed(), df_vertices, True)
        self.assertTrue(df_edges.equals(g_clone.get_edge_dataframe()))
        self.assertTrue(df_vertices.equals(g_clone.get_vertex_dataframe()))

        # Invalid input
        with self.assertRaisesRegex(ValueError, "two columns"):
            edges = pd.DataFrame({"source": [1, 2, 3]})
            Graph.DataFrame(edges)
        with self.assertRaisesRegex(ValueError, "one column"):
            edges = pd.DataFrame({"source": [1, 2, 3], "target": [4, 5, 6]})
            Graph.DataFrame(edges, vertices=pd.DataFrame())
        with self.assertRaisesRegex(TypeError, "integers"):
            edges = pd.DataFrame({"source": [1, 2, 3], "target": [4, 5, 6]}).astype(str)
            Graph.DataFrame(edges, use_vids=True)
        with self.assertRaisesRegex(ValueError, "negative"):
            edges = -pd.DataFrame({"source": [1, 2, 3], "target": [4, 5, 6]})
            Graph.DataFrame(edges, use_vids=True)
        with self.assertRaisesRegex(TypeError, "integers"):
            edges = pd.DataFrame({"source": [1, 2, 3], "target": [4, 5, 6]})
            vertices = pd.DataFrame({0: [1, 2, 3]}, index=["1", "2", "3"])
            Graph.DataFrame(edges, vertices=vertices, use_vids=True)
        with self.assertRaisesRegex(ValueError, "negative"):
            edges = pd.DataFrame({"source": [1, 2, 3], "target": [4, 5, 6]})
            vertices = pd.DataFrame({0: [1, 2, 3]}, index=[-1, 2, 3])
            Graph.DataFrame(edges, vertices=vertices, use_vids=True)
        with self.assertRaisesRegex(ValueError, "sequence"):
            edges = pd.DataFrame({"source": [1, 2, 3], "target": [4, 5, 6]})
            vertices = pd.DataFrame({0: [1, 2, 3]}, index=[1, 2, 4])
            Graph.DataFrame(edges, vertices=vertices, use_vids=True)
        with self.assertRaisesRegex(TypeError, "integers"):
            edges = pd.DataFrame({"source": [1, 2, 3], "target": [4, 5, 6]})
            vertices = pd.DataFrame({0: [1, 2, 3]}, index=pd.MultiIndex.from_tuples([(1, 1), (2, 2), (3, 3)]))
            Graph.DataFrame(edges, vertices=vertices, use_vids=True)
        with self.assertRaisesRegex(ValueError, "unique"):
            edges = pd.DataFrame({"source": [1, 2, 3], "target": [4, 5, 6]})
            vertices = pd.DataFrame({0: [1, 2, 2]})
            Graph.DataFrame(edges, vertices=vertices)
        with self.assertRaisesRegex(ValueError, "already contains"):
            edges = pd.DataFrame({"source": [1, 2, 3], "target": [4, 5, 6]})
            vertices = pd.DataFrame({0: [1, 2, 3], "name": [1, 2, 2]})
            Graph.DataFrame(edges, vertices=vertices)
        with self.assertRaisesRegex(ValueError, "missing from"):
            edges = pd.DataFrame({"source": [1, 2, 3], "target": [4, 5, 6]})
            vertices = pd.DataFrame({0: [1, 2, 3]}, index=[0, 1, 2])
            Graph.DataFrame(edges, vertices=vertices, use_vids=True)


def suite():
    generator_suite = unittest.makeSuite(GeneratorTests)
    return unittest.TestSuite([generator_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
