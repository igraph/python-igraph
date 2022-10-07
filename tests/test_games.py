import unittest

from igraph import Graph, InternalError, Layout


class GameTests(unittest.TestCase):
    def testGRG(self):
        g = Graph.GRG(50, 0.2)
        self.assertTrue(isinstance(g, Graph))
        g = Graph.GRG(50, 0.2, True)
        self.assertTrue(isinstance(g, Graph))
        self.assertTrue("x" in g.vertex_attributes())
        self.assertTrue("y" in g.vertex_attributes())
        self.assertTrue(isinstance(Layout(list(zip(g.vs["x"], g.vs["y"]))), Layout))

    def testForestFire(self):
        g = Graph.Forest_Fire(100, 0.1)
        self.assertTrue(isinstance(g, Graph) and g.is_directed() is False)
        g = Graph.Forest_Fire(100, 0.1, directed=True)
        self.assertTrue(isinstance(g, Graph) and g.is_directed() is True)

    def testRecentDegree(self):
        g = Graph.Recent_Degree(100, 5, 10)
        self.assertTrue(isinstance(g, Graph))

    def testPreference(self):
        g = Graph.Preference(100, [1, 1], [[1, 0], [0, 1]])
        self.assertTrue(isinstance(g, Graph))
        self.assertEqual(len(g.connected_components()), 2)

        g = Graph.Preference(100, [1, 1], [[1, 0], [0, 1]], attribute="type")
        types = g.vs.get_attribute_values("type")
        self.assertTrue(min(types) == 0 and max(types) == 1)

    def testAsymmetricPreference(self):
        g = Graph.Asymmetric_Preference(100, [[0, 1], [1, 0]], [[0, 1], [1, 0]])
        self.assertTrue(isinstance(g, Graph))
        self.assertEqual(len(g.connected_components()), 2)

        g = Graph.Asymmetric_Preference(
            100, [[0, 1], [1, 0]], [[1, 0], [0, 1]], attribute="type"
        )
        types = g.vs.get_attribute_values("type")
        types1 = [i[0] for i in types]
        types2 = [i[1] for i in types]
        self.assertTrue(min(types1) == 0 and max(types1) == 1 and min(types2) == 0 and max(types2) == 1)

        g = Graph.Asymmetric_Preference(100, [[0, 1], [1, 0]], [[1, 0], [0, 1]])
        self.assertTrue(isinstance(g, Graph))
        self.assertEqual(len(g.connected_components()), 1)

    def testTreeGame(self):
        # Prufer algorithm
        g = Graph.Tree_Game(10, False, "Prufer")
        self.assertTrue(isinstance(g, Graph) and g.vcount() == 10)
        self.assertFalse(g.is_directed())
        self.assertTrue(g.is_tree())

        # Prufer with directed (should fail)
        self.assertRaises(InternalError, Graph.Tree_Game, 10, True, "Prufer")

        # LERW algorithm
        g = Graph.Tree_Game(10, False, "lerw")
        self.assertTrue(isinstance(g, Graph) and g.vcount() == 10)
        self.assertFalse(g.is_directed())
        self.assertTrue(g.is_tree())

        # Omitting the algorithm should default to LERW
        g = Graph.Tree_Game(10, directed=True)
        self.assertTrue(isinstance(g, Graph) and g.vcount() == 10)
        self.assertTrue(g.is_directed())
        self.assertTrue(g.is_tree())

        # Omitting the directed argument should use undirected graphs
        g = Graph.Tree_Game(42, method="Prufer")
        self.assertTrue(isinstance(g, Graph) and g.vcount() == 42)
        self.assertFalse(g.is_directed())
        self.assertTrue(g.is_tree())

    def testWattsStrogatz(self):
        g = Graph.Watts_Strogatz(1, 20, 1, 0.2)
        self.assertTrue(isinstance(g, Graph) and g.vcount() == 20 and g.ecount() == 20)

    def testRandomBipartiteNP(self):
        # Test np mode, undirected
        g = Graph.Random_Bipartite(10, 20, p=0.25)
        self.assertTrue(g.is_simple())
        self.assertTrue(g.is_bipartite())
        self.assertFalse(g.is_directed())
        self.assertEqual([False] * 10 + [True] * 20, g.vs["type"])

        # Test np mode, directed, "out"
        g = Graph.Random_Bipartite(10, 20, p=0.25, directed=True, neimode="out")
        self.assertTrue(g.is_simple())
        self.assertTrue(g.is_bipartite())
        self.assertTrue(g.is_directed())
        self.assertEqual([False] * 10 + [True] * 20, g.vs["type"])
        self.assertTrue(all(g.vs[e.tuple]["type"] == [False, True] for e in g.es))

        # Test np mode, directed, "in"
        g = Graph.Random_Bipartite(10, 20, p=0.25, directed=True, neimode="in")
        self.assertTrue(g.is_simple())
        self.assertTrue(g.is_bipartite())
        self.assertTrue(g.is_directed())
        self.assertEqual([False] * 10 + [True] * 20, g.vs["type"])
        self.assertTrue(all(g.vs[e.tuple]["type"] == [True, False] for e in g.es))

        # Test np mode, directed, "all"
        g = Graph.Random_Bipartite(10, 20, p=0.25, directed=True, neimode="all")
        self.assertTrue(g.is_simple())
        self.assertTrue(g.is_bipartite())
        self.assertTrue(g.is_directed())
        self.assertEqual([False] * 10 + [True] * 20, g.vs["type"])

    def testRandomBipartiteNM(self):
        # Test np mode, undirected
        g = Graph.Random_Bipartite(10, 20, m=50)
        self.assertTrue(g.is_simple())
        self.assertTrue(g.is_bipartite())
        self.assertFalse(g.is_directed())
        self.assertEqual(50, g.ecount())
        self.assertEqual([False] * 10 + [True] * 20, g.vs["type"])

        # Test np mode, directed, "out"
        g = Graph.Random_Bipartite(10, 20, m=50, directed=True, neimode="out")
        self.assertTrue(g.is_simple())
        self.assertTrue(g.is_bipartite())
        self.assertTrue(g.is_directed())
        self.assertEqual(50, g.ecount())
        self.assertEqual([False] * 10 + [True] * 20, g.vs["type"])
        self.assertTrue(all(g.vs[e.tuple]["type"] == [False, True] for e in g.es))

        # Test np mode, directed, "in"
        g = Graph.Random_Bipartite(10, 20, m=50, directed=True, neimode="in")
        self.assertTrue(g.is_simple())
        self.assertTrue(g.is_bipartite())
        self.assertTrue(g.is_directed())
        self.assertEqual(50, g.ecount())
        self.assertEqual([False] * 10 + [True] * 20, g.vs["type"])
        self.assertTrue(all(g.vs[e.tuple]["type"] == [True, False] for e in g.es))

        # Test np mode, directed, "all"
        g = Graph.Random_Bipartite(10, 20, m=50, directed=True, neimode="all")
        self.assertTrue(g.is_simple())
        self.assertTrue(g.is_bipartite())
        self.assertTrue(g.is_directed())
        self.assertEqual(50, g.ecount())
        self.assertEqual([False] * 10 + [True] * 20, g.vs["type"])

    def testRewire(self):
        # Undirected graph
        g = Graph.GRG(25, 0.4)
        degrees = g.degree()

        # Rewiring without loops
        g.rewire(10000)
        self.assertEqual(degrees, g.degree())
        self.assertTrue(g.is_simple())

        # Rewiring with loops (1)
        g.rewire(10000, mode="loops")
        self.assertEqual(degrees, g.degree())
        self.assertFalse(any(g.is_multiple()))

        # Rewiring with loops (2)
        g = Graph.Full(4)
        g[1, 3] = 0
        degrees = g.degree()
        g.rewire(100, mode="loops")
        self.assertEqual(degrees, g.degree())
        self.assertFalse(any(g.is_multiple()))

        # Directed graph
        g = Graph.GRG(25, 0.4)
        g.to_directed("mutual")
        indeg, outdeg = g.indegree(), g.outdegree()
        g.rewire(10000)
        self.assertEqual(indeg, g.indegree())
        self.assertEqual(outdeg, g.outdegree())
        self.assertTrue(g.is_simple())

        # Directed graph with loops
        g.rewire(10000, mode="loops")
        self.assertEqual(indeg, g.indegree())
        self.assertEqual(outdeg, g.outdegree())
        self.assertFalse(any(g.is_multiple()))


def suite():
    game_suite = unittest.defaultTestLoader.loadTestsFromTestCase(GameTests)
    return unittest.TestSuite([game_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
