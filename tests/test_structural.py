import math
import unittest
import warnings

from igraph import Graph, InternalError, IN, OUT, ALL, TREE_IN
from math import inf, isnan


class SimplePropertiesTests(unittest.TestCase):
    gfull = Graph.Full(10)
    gempty = Graph(10)
    g = Graph(4, [(0, 1), (0, 2), (1, 2), (0, 3), (1, 3)])
    gdir = Graph(
        4, [(0, 1), (0, 2), (1, 2), (2, 1), (0, 3), (1, 3), (3, 0)], directed=True
    )
    tree = Graph.Tree(14, 3)

    def testDensity(self):
        self.assertAlmostEqual(1.0, self.gfull.density(), places=5)
        self.assertAlmostEqual(0.0, self.gempty.density(), places=5)
        self.assertAlmostEqual(5 / 6, self.g.density(), places=5)
        self.assertAlmostEqual(1 / 2, self.g.density(True), places=5)
        self.assertAlmostEqual(7 / 12, self.gdir.density(), places=5)
        self.assertAlmostEqual(7 / 16, self.gdir.density(True), places=5)
        self.assertAlmostEqual(1 / 7, self.tree.density(), places=5)

    def testDiameter(self):
        self.assertTrue(self.gfull.diameter() == 1)
        self.assertTrue(self.gempty.diameter(unconn=False) == inf)
        self.assertTrue(self.gempty.diameter(unconn=False) == inf)
        self.assertTrue(self.g.diameter() == 2)
        self.assertTrue(self.gdir.diameter(False) == 2)
        self.assertTrue(self.gdir.diameter() == 3)
        self.assertTrue(self.tree.diameter() == 5)

        s, t, d = self.tree.farthest_points()
        self.assertTrue((s == 13 or t == 13) and d == 5)
        self.assertTrue(self.gempty.farthest_points(unconn=False) == (None, None, inf))

        d = self.tree.get_diameter()
        self.assertTrue(d[0] == 13 or d[-1] == 13)

        weights = [1, 1, 1, 5, 1, 5, 1, 1, 1, 1, 1, 1, 5]
        self.assertTrue(self.tree.diameter(weights=weights) == 15)

        d = self.tree.farthest_points(weights=weights)
        self.assertTrue(d == (13, 6, 15) or d == (6, 13, 15))

    def testEccentricity(self):
        self.assertEqual(self.gfull.eccentricity(), [1] * self.gfull.vcount())
        self.assertEqual(self.gempty.eccentricity(), [0] * self.gempty.vcount())
        self.assertEqual(self.g.eccentricity(), [1, 1, 2, 2])
        self.assertEqual(self.gdir.eccentricity(), [1, 2, 3, 2])
        self.assertEqual(
            self.tree.eccentricity(), [3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5]
        )
        self.assertEqual(Graph().eccentricity(), [])

    def testRadius(self):
        self.assertEqual(self.gfull.radius(), 1)
        self.assertEqual(self.gempty.radius(), 0)
        self.assertEqual(self.g.radius(), 1)
        self.assertEqual(self.gdir.radius(), 1)
        self.assertEqual(self.tree.radius(), 3)
        self.assertTrue(isnan(Graph().radius()))

    def testTransitivity(self):
        self.assertTrue(self.gfull.transitivity_undirected() == 1.0)
        self.assertTrue(self.tree.transitivity_undirected() == 0.0)
        self.assertTrue(self.g.transitivity_undirected() == 0.75)

    def testLocalTransitivity(self):
        self.assertTrue(
            self.gfull.transitivity_local_undirected() == [1.0] * self.gfull.vcount()
        )
        self.assertTrue(
            self.tree.transitivity_local_undirected(mode="zero")
            == [0.0] * self.tree.vcount()
        )

        transitivity = self.g.transitivity_local_undirected(mode="zero")
        self.assertAlmostEqual(2 / 3, transitivity[0], places=4)
        self.assertAlmostEqual(2 / 3, transitivity[1], places=4)
        self.assertEqual(1, transitivity[2])
        self.assertEqual(1, transitivity[3])

        g = Graph.Full(4) + 1 + [(0, 4)]
        g.es["weight"] = [1, 1, 1, 1, 1, 1, 5]
        self.assertAlmostEqual(
            g.transitivity_local_undirected(0, weights="weight"), 0.25, places=4
        )

    def testAvgLocalTransitivity(self):
        self.assertTrue(self.gfull.transitivity_avglocal_undirected() == 1.0)
        self.assertTrue(self.tree.transitivity_avglocal_undirected() == 0.0)
        self.assertAlmostEqual(
            self.g.transitivity_avglocal_undirected(), 5 / 6.0, places=4
        )

    def testModularity(self):
        g = Graph.Full(5) + Graph.Full(5)
        g.add_edges([(0, 5)])
        cl = [0] * 5 + [1] * 5
        self.assertAlmostEqual(g.modularity(cl), 0.4523, places=3)
        ws = [1] * 21
        self.assertAlmostEqual(g.modularity(cl, ws), 0.4523, places=3)
        ws = [2] * 21
        self.assertAlmostEqual(g.modularity(cl, ws), 0.4523, places=3)
        ws = [2] * 10 + [1] * 11
        self.assertAlmostEqual(g.modularity(cl, ws), 0.4157, places=3)
        self.assertRaises(InternalError, g.modularity, cl, ws[0:20])


class DegreeTests(unittest.TestCase):
    gfull = Graph.Full(10)
    gempty = Graph(10)
    g = Graph(4, [(0, 1), (0, 2), (1, 2), (0, 3), (1, 3), (0, 0)])
    gdir = Graph(
        4, [(0, 1), (0, 2), (1, 2), (2, 1), (0, 3), (1, 3), (3, 0)], directed=True
    )
    tree = Graph.Tree(10, 3)

    def testKnn(self):
        knn, knnk = self.gfull.knn()
        self.assertTrue(knn == [9.0] * 10)
        self.assertAlmostEqual(knnk[8], 9.0, places=6)

        # knn works for simple graphs only -- self.g is not simple
        self.assertRaises(InternalError, self.g.knn)

        # Okay, simplify it and then go on
        g = self.g.copy()
        g.simplify()

        knn, knnk = g.knn()
        diff = max(abs(a - b) for a, b in zip(knn, [7 / 3.0, 7 / 3.0, 3, 3]))
        self.assertAlmostEqual(diff, 0.0, places=6)
        self.assertEqual(len(knnk), 3)
        self.assertAlmostEqual(knnk[1], 3, places=6)
        self.assertAlmostEqual(knnk[2], 7 / 3.0, places=6)

    def testDegree(self):
        self.assertTrue(self.gfull.degree() == [9] * 10)
        self.assertTrue(self.gempty.degree() == [0] * 10)
        self.assertTrue(self.g.degree(loops=False) == [3, 3, 2, 2])
        self.assertTrue(self.g.degree() == [5, 3, 2, 2])
        self.assertTrue(self.gdir.degree(mode=IN) == [1, 2, 2, 2])
        self.assertTrue(self.gdir.degree(mode=OUT) == [3, 2, 1, 1])
        self.assertTrue(self.gdir.degree(mode=ALL) == [4, 4, 3, 3])
        vs = self.gdir.vs.select(0, 2)
        self.assertTrue(self.gdir.degree(vs, mode=ALL) == [4, 3])
        self.assertTrue(self.gdir.degree(self.gdir.vs[1], mode=ALL) == 4)

    def testMaxDegree(self):
        self.assertTrue(self.gfull.maxdegree() == 9)
        self.assertTrue(self.gempty.maxdegree() == 0)
        self.assertTrue(self.g.maxdegree() == 3)
        self.assertTrue(self.g.maxdegree(loops=True) == 5)
        self.assertTrue(self.g.maxdegree([1, 2], loops=True) == 3)
        self.assertTrue(self.gdir.maxdegree(mode=IN) == 2)
        self.assertTrue(self.gdir.maxdegree(mode=OUT) == 3)
        self.assertTrue(self.gdir.maxdegree(mode=ALL) == 4)

    def testStrength(self):
        # Turn off warnings about calling strength without weights
        import warnings

        warnings.filterwarnings(
            "ignore", "No edge weights for strength calculation", RuntimeWarning
        )

        # No weights
        self.assertTrue(self.gfull.strength() == [9] * 10)
        self.assertTrue(self.gempty.strength() == [0] * 10)
        self.assertTrue(self.g.degree(loops=False) == [3, 3, 2, 2])
        self.assertTrue(self.g.degree() == [5, 3, 2, 2])
        # With weights
        ws = [1, 2, 3, 4, 5, 6]
        self.assertTrue(self.g.strength(weights=ws, loops=False) == [7, 9, 5, 9])
        self.assertTrue(self.g.strength(weights=ws) == [19, 9, 5, 9])
        ws = [1, 2, 3, 4, 5, 6, 7]
        self.assertTrue(self.gdir.strength(mode=IN, weights=ws) == [7, 5, 5, 11])
        self.assertTrue(self.gdir.strength(mode=OUT, weights=ws) == [8, 9, 4, 7])
        self.assertTrue(self.gdir.strength(mode=ALL, weights=ws) == [15, 14, 9, 18])
        vs = self.gdir.vs.select(0, 2)
        self.assertTrue(self.gdir.strength(vs, mode=ALL, weights=ws) == [15, 9])
        self.assertTrue(self.gdir.strength(self.gdir.vs[1], mode=ALL, weights=ws) == 14)


class LocalTransitivityTests(unittest.TestCase):
    def testLocalTransitivityFull(self):
        trans = Graph.Full(10).transitivity_local_undirected()
        self.assertTrue(trans == [1.0] * 10)

    def testLocalTransitivityTree(self):
        trans = Graph.Tree(10, 3).transitivity_local_undirected()
        self.assertTrue(trans[0:3] == [0.0, 0.0, 0.0])

    def testLocalTransitivityHalf(self):
        g = Graph(4, [(0, 1), (0, 2), (1, 2), (0, 3), (1, 3)])
        trans = g.transitivity_local_undirected()
        trans = [round(x, 3) for x in trans]
        self.assertTrue(trans == [0.667, 0.667, 1.0, 1.0])

    def testLocalTransitivityPartial(self):
        g = Graph(4, [(0, 1), (0, 2), (1, 2), (0, 3), (1, 3)])
        trans = g.transitivity_local_undirected([1, 2])
        trans = [round(x, 3) for x in trans]
        self.assertTrue(trans == [0.667, 1.0])


class BiconnectedComponentTests(unittest.TestCase):
    g1 = Graph.Full(10)
    g2 = Graph(5, [(0, 1), (1, 2), (2, 3), (3, 4)])
    g3 = Graph(6, [(0, 1), (1, 2), (2, 3), (3, 0), (2, 4), (2, 5), (4, 5)])

    def testBiconnectedComponents(self):
        s = self.g1.biconnected_components()
        self.assertTrue(len(s) == 1 and s[0] == list(range(10)))
        s, ap = self.g1.biconnected_components(True)
        self.assertTrue(len(s) == 1 and s[0] == list(range(10)))

        s = self.g3.biconnected_components()
        self.assertTrue(len(s) == 2 and s[0] == [2, 4, 5] and s[1] == [0, 1, 2, 3])
        s, ap = self.g3.biconnected_components(True)
        self.assertTrue(
            len(s) == 2 and s[0] == [2, 4, 5] and s[1] == [0, 1, 2, 3] and ap == [2]
        )

    def testArticulationPoints(self):
        self.assertTrue(self.g1.articulation_points() == [])
        self.assertTrue(self.g2.cut_vertices() == [1, 2, 3])
        self.assertTrue(self.g3.articulation_points() == [2])


class CentralityTests(unittest.TestCase):
    def testBetweennessCentrality(self):
        g = Graph.Star(5)
        self.assertTrue(g.betweenness() == [6.0, 0.0, 0.0, 0.0, 0.0])
        g = Graph(5, [(0, 1), (0, 2), (0, 3), (1, 4)])
        self.assertTrue(g.betweenness() == [5.0, 3.0, 0.0, 0.0, 0.0])
        self.assertTrue(g.betweenness(cutoff=2) == [3.0, 1.0, 0.0, 0.0, 0.0])
        self.assertTrue(g.betweenness(cutoff=1) == [0.0, 0.0, 0.0, 0.0, 0.0])
        g = Graph.Lattice([3, 3], circular=False)
        self.assertTrue(
            g.betweenness(cutoff=2) == [0.5, 2.0, 0.5, 2.0, 4.0, 2.0, 0.5, 2.0, 0.5]
        )

    def testEdgeBetweennessCentrality(self):
        g = Graph.Star(5)
        self.assertTrue(g.edge_betweenness() == [4.0, 4.0, 4.0, 4.0])
        g = Graph(5, [(0, 1), (0, 2), (0, 3), (1, 4)])
        self.assertTrue(g.edge_betweenness() == [6.0, 4.0, 4.0, 4.0])
        self.assertTrue(g.edge_betweenness(cutoff=2) == [4.0, 3.0, 3.0, 2.0])
        self.assertTrue(g.edge_betweenness(cutoff=1) == [1.0, 1.0, 1.0, 1.0])
        g = Graph.Ring(5)
        self.assertTrue(g.edge_betweenness() == [3.0, 3.0, 3.0, 3.0, 3.0])
        self.assertTrue(
            g.edge_betweenness(weights=[4, 1, 1, 1, 1]) == [0.5, 3.5, 5.5, 5.5, 3.5]
        )

    def testClosenessCentrality(self):
        g = Graph.Star(5)
        cl = g.closeness()
        cl2 = [1.0, 4 / 7.0, 4 / 7.0, 4 / 7.0, 4 / 7.0]
        for idx in range(g.vcount()):
            self.assertAlmostEqual(cl[idx], cl2[idx], places=3)

        g = Graph.Star(5)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cl = g.closeness(cutoff=1.0)
        cl2 = [1.0, 1.0, 1.0, 1.0, 1.0]
        for idx in range(g.vcount()):
            self.assertAlmostEqual(cl[idx], cl2[idx], places=3)

        weights = [1] * 4

        g = Graph.Star(5)
        cl = g.closeness(weights=weights)
        cl2 = [1.0, 0.57142, 0.57142, 0.57142, 0.57142]
        for idx in range(g.vcount()):
            self.assertAlmostEqual(cl[idx], cl2[idx], places=3)

        g = Graph.Star(5)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cl = g.closeness(cutoff=1.0, weights=weights)
        cl2 = [1.0, 1.0, 1.0, 1.0, 1.0]
        for idx in range(g.vcount()):
            self.assertAlmostEqual(cl[idx], cl2[idx], places=3)

        # Test for igraph/igraph:#1078
        g = Graph(
            [
                (0, 1),
                (0, 2),
                (0, 5),
                (0, 6),
                (0, 9),
                (1, 6),
                (1, 8),
                (2, 4),
                (2, 6),
                (2, 7),
                (2, 8),
                (3, 6),
                (4, 8),
                (5, 6),
                (5, 9),
                (6, 7),
                (6, 8),
                (7, 8),
                (7, 9),
                (8, 9),
            ]
        )
        weights = [
            0.69452,
            0.329886,
            0.131649,
            0.503269,
            0.472738,
            0.370933,
            0.23857,
            0.0354043,
            0.189015,
            0.355118,
            0.768335,
            0.893289,
            0.891709,
            0.494896,
            0.924684,
            0.432001,
            0.858159,
            0.246798,
            0.881304,
            0.64685,
        ]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cl = g.closeness(weights=weights)
        expected_cl = [
            1.63318,
            1.52014,
            2.03724,
            0.760158,
            1.91449,
            1.43224,
            1.91761,
            1.60198,
            1.3891,
            1.12829,
        ]
        for obs, exp in zip(cl, expected_cl):
            self.assertAlmostEqual(obs, exp, places=4)

    def testHarmonicCentrality(self):
        g = Graph.Star(5)
        cl = g.harmonic_centrality()
        cl2 = [1.0] + [(1.0 + 1 / 2 * 3) / 4] * 4
        for idx in range(g.vcount()):
            self.assertAlmostEqual(cl[idx], cl2[idx], places=3)

        g = Graph.Star(5)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cl = g.harmonic_centrality(cutoff=1.0)
        cl2 = [1.0, 0.25, 0.25, 0.25, 0.25]
        for idx in range(g.vcount()):
            self.assertAlmostEqual(cl[idx], cl2[idx], places=3)

        weights = [1] * 4

        g = Graph.Star(5)
        cl = g.harmonic_centrality(weights=weights)
        cl2 = [1.0] + [0.625] * 4
        for idx in range(g.vcount()):
            self.assertAlmostEqual(cl[idx], cl2[idx], places=3)

        g = Graph.Star(5)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cl = g.harmonic_centrality(cutoff=1.0, weights=weights)
        cl2 = [1.0, 0.25, 0.25, 0.25, 0.25]
        for idx in range(g.vcount()):
            self.assertAlmostEqual(cl[idx], cl2[idx], places=3)

    def testPageRank(self):
        g = Graph.Star(11)
        cent = g.pagerank()
        self.assertTrue(cent.index(max(cent)) == 0)
        self.assertAlmostEqual(max(cent), 0.4668, places=3)

    def testPersonalizedPageRank(self):
        g = Graph.Star(11)
        self.assertRaises(InternalError, g.personalized_pagerank, reset=[0] * 11)
        cent = g.personalized_pagerank(reset=[0, 10] + [0] * 9, damping=0.5)
        self.assertTrue(cent.index(max(cent)) == 1)
        self.assertAlmostEqual(cent[0], 0.3333, places=3)
        self.assertAlmostEqual(cent[1], 0.5166, places=3)
        self.assertAlmostEqual(cent[2], 0.0166, places=3)
        cent2 = g.personalized_pagerank(reset_vertices=g.vs[1], damping=0.5)
        self.assertTrue(max(abs(x - y) for x, y in zip(cent, cent2)) < 0.001)

    def testEigenvectorCentrality(self):
        g = Graph.Star(11)
        cent = g.evcent()
        self.assertTrue(cent.index(max(cent)) == 0)
        self.assertAlmostEqual(max(cent), 1.0, places=3)
        self.assertTrue(min(cent) >= 0)
        cent, ev = g.evcent(scale=False, return_eigenvalue=True)
        if cent[0] < 0:
            cent = [-x for x in cent]
        self.assertTrue(cent.index(max(cent)) == 0)
        self.assertAlmostEqual(cent[1] / cent[0], 0.3162, places=3)
        self.assertAlmostEqual(ev, 3.162, places=3)

    def testAuthorityScore(self):
        g = Graph.Tree(15, 2, TREE_IN)
        asc = g.authority_score()
        self.assertAlmostEqual(max(asc), 1.0, places=3)

        # Smoke testing
        g.authority_score(scale=False, return_eigenvalue=True)

    def testHubScore(self):
        g = Graph.Tree(15, 2, TREE_IN)
        hsc = g.hub_score()
        self.assertAlmostEqual(max(hsc), 1.0, places=3)

        # Smoke testing
        g.hub_score(scale=False, return_eigenvalue=True)

    def testCoreness(self):
        g = Graph.Full(4) + Graph(4) + [(0, 4), (1, 5), (2, 6), (3, 7)]
        self.assertEqual(g.coreness("all"), [3, 3, 3, 3, 1, 1, 1, 1])


class NeighborhoodTests(unittest.TestCase):
    def testNeighborhood(self):
        g = Graph.Ring(10, circular=False)
        self.assertTrue(
            list(map(sorted, g.neighborhood()))
            == [
                [0, 1],
                [0, 1, 2],
                [1, 2, 3],
                [2, 3, 4],
                [3, 4, 5],
                [4, 5, 6],
                [5, 6, 7],
                [6, 7, 8],
                [7, 8, 9],
                [8, 9],
            ]
        )
        self.assertTrue(
            list(map(sorted, g.neighborhood(order=3)))
            == [
                [0, 1, 2, 3],
                [0, 1, 2, 3, 4],
                [0, 1, 2, 3, 4, 5],
                [0, 1, 2, 3, 4, 5, 6],
                [1, 2, 3, 4, 5, 6, 7],
                [2, 3, 4, 5, 6, 7, 8],
                [3, 4, 5, 6, 7, 8, 9],
                [4, 5, 6, 7, 8, 9],
                [5, 6, 7, 8, 9],
                [6, 7, 8, 9],
            ]
        )
        self.assertTrue(
            list(map(sorted, g.neighborhood(order=3, mindist=2)))
            == [
                [2, 3],
                [3, 4],
                [0, 4, 5],
                [0, 1, 5, 6],
                [1, 2, 6, 7],
                [2, 3, 7, 8],
                [3, 4, 8, 9],
                [4, 5, 9],
                [5, 6],
                [6, 7],
            ]
        )

    def testNeighborhoodSize(self):
        g = Graph.Ring(10, circular=False)
        self.assertTrue(g.neighborhood_size() == [2, 3, 3, 3, 3, 3, 3, 3, 3, 2])
        self.assertTrue(g.neighborhood_size(order=3) == [4, 5, 6, 7, 7, 7, 7, 6, 5, 4])
        self.assertTrue(
            g.neighborhood_size(order=3, mindist=2) == [2, 2, 3, 4, 4, 4, 4, 3, 2, 2]
        )


class MiscTests(unittest.TestCase):
    def assert_valid_maximum_cardinality_search_result(self, graph, alpha, alpham1):
        visited = []
        n = graph.vcount()
        not_visited = list(range(n))

        # Check if alpham1 is a valid visiting order
        for vertex in reversed(alpham1):
            neis = graph.neighbors(vertex)
            visited_neis = sum(1 for v in neis if v in visited)
            for other_vertex in not_visited:
                neis = graph.neighbors(other_vertex)
                other_visited_neis = sum(1 for v in neis if v in visited)
                self.assertTrue(other_visited_neis <= visited_neis)

            visited.append(vertex)
            not_visited.remove(vertex)

        # Check if alpha is the inverse of alpham1
        for index, vertex in enumerate(alpham1):
            self.assertEqual(alpha[vertex], index)

    def testBridges(self):
        g = Graph(5, [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4)])
        self.assertEqual(g.bridges(), [3, 4])
        g = Graph(7, [(0, 1), (1, 2), (2, 0), (1, 6), (1, 3), (1, 4), (3, 5), (4, 5)])
        self.assertEqual(g.bridges(), [3])
        g = Graph(3, [(0, 1), (1, 2), (2, 3)])
        self.assertEqual(g.bridges(), [0, 1, 2])

    def testChordalCompletion(self):
        g = Graph()
        self.assertListEqual([], g.chordal_completion())

        g = Graph.Full(3)
        self.assertListEqual([], g.chordal_completion())

        g = Graph.Full(5)
        self.assertListEqual([], g.chordal_completion())

        g = Graph.Ring(4)
        cc = g.chordal_completion()
        self.assertEqual(len(cc), 1)
        g += cc
        self.assertTrue(g.is_chordal())
        self.assertListEqual([], g.chordal_completion())

        g = Graph.Ring(5)
        cc = g.chordal_completion()
        self.assertEqual(len(cc), 2)
        g += cc
        self.assertListEqual([], g.chordal_completion())

    def testChordalCompletionWithHints(self):
        g = Graph.Ring(4)
        alpha, _ = g.maximum_cardinality_search()
        cc = g.chordal_completion(alpha=alpha)
        self.assertEqual(len(cc), 1)
        g += cc
        self.assertTrue(g.is_chordal())
        self.assertListEqual([], g.chordal_completion())

        g = Graph.Ring(5)
        _, alpham1 = g.maximum_cardinality_search()
        cc = g.chordal_completion(alpham1=alpham1)
        self.assertEqual(len(cc), 2)
        g += cc
        self.assertListEqual([], g.chordal_completion())

    def testChordalCompletion(self):
        g = Graph()
        self.assertListEqual([], g.chordal_completion())

        g = Graph.Full(3)
        self.assertListEqual([], g.chordal_completion())

        g = Graph.Full(5)
        self.assertListEqual([], g.chordal_completion())

        g = Graph.Ring(4)
        cc = g.chordal_completion()
        self.assertEqual(len(cc), 1)
        g += cc
        self.assertTrue(g.is_chordal())
        self.assertListEqual([], g.chordal_completion())

        g = Graph.Ring(5)
        cc = g.chordal_completion()
        self.assertEqual(len(cc), 2)
        g += cc
        self.assertListEqual([], g.chordal_completion())

    def testChordalCompletionWithHints(self):
        g = Graph.Ring(4)
        alpha, _ = g.maximum_cardinality_search()
        cc = g.chordal_completion(alpha=alpha)
        self.assertEqual(len(cc), 1)
        g += cc
        self.assertTrue(g.is_chordal())
        self.assertListEqual([], g.chordal_completion())

        g = Graph.Ring(5)
        _, alpham1 = g.maximum_cardinality_search()
        cc = g.chordal_completion(alpham1=alpham1)
        self.assertEqual(len(cc), 2)
        g += cc
        self.assertListEqual([], g.chordal_completion())

    def testConstraint(self):
        g = Graph(4, [(0, 1), (0, 2), (1, 2), (0, 3), (1, 3)])
        self.assertTrue(isinstance(g.constraint(), list))  # TODO check more

    def testTopologicalSorting(self):
        g = Graph(5, [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)], directed=True)
        self.assertTrue(g.topological_sorting() == [0, 4, 1, 2, 3])
        self.assertTrue(g.topological_sorting(IN) == [3, 4, 2, 1, 0])
        g.to_undirected()
        self.assertRaises(InternalError, g.topological_sorting)

    def testIsTree(self):
        g = Graph()
        self.assertFalse(g.is_tree())

        g = Graph(directed=True)
        self.assertFalse(g.is_tree())

        g = Graph(1)
        self.assertTrue(g.is_tree())

        g = Graph(1, directed=True)
        self.assertTrue(g.is_tree() and g.is_tree("out") and g.is_tree("in") and g.is_tree("all"))

        g = Graph(5, [(0, 1), (1, 2), (1, 3), (3, 4)])
        self.assertTrue(g.is_tree())

        g = Graph(5, [(0, 1), (1, 2), (1, 3), (3, 4)], directed=True)
        self.assertTrue(g.is_tree())
        self.assertTrue(g.is_tree("out"))
        self.assertFalse(g.is_tree("in"))
        self.assertTrue(g.is_tree("all"))

        g = Graph(5, [(0, 1), (1, 2), (3, 1), (3, 4)], directed=True)
        self.assertFalse(g.is_tree())
        self.assertFalse(g.is_tree("in"))
        self.assertFalse(g.is_tree("out"))
        self.assertTrue(g.is_tree("all"))

        g = Graph(6, [(0, 4), (1, 5), (2, 1), (3, 1), (4, 3)], directed=True)
        self.assertFalse(g.is_tree())
        self.assertTrue(g.is_tree("in"))
        self.assertFalse(g.is_tree("out"))
        self.assertTrue(g.is_tree("all"))

        g = Graph.Ring(10)
        self.assertFalse(
            g.is_tree() or g.is_tree("in") or g.is_tree("out") or
            g.is_tree("all")
        )

    def testIsChordal(self):
        g = Graph()
        self.assertTrue(g.is_chordal())

        g = Graph.Full(3)
        self.assertTrue(g.is_chordal())

        g = Graph.Full(5)
        self.assertTrue(g.is_chordal())

        g = Graph.Ring(4)
        self.assertFalse(g.is_chordal())

        g = Graph.Ring(5)
        self.assertFalse(g.is_chordal())

    def testIsChordalWithHint(self):
        g = Graph()
        alpha, _ = g.maximum_cardinality_search()
        self.assertTrue(g.is_chordal(alpha=alpha))

        g = Graph.Full(3)
        alpha, _ = g.maximum_cardinality_search()
        self.assertTrue(g.is_chordal(alpha=alpha))

        g = Graph.Ring(5)
        alpha, _ = g.maximum_cardinality_search()
        self.assertFalse(g.is_chordal(alpha=alpha))

        g = Graph.Ring(4)
        _, alpham1 = g.maximum_cardinality_search()
        self.assertFalse(g.is_chordal(alpham1=alpham1))

        g = Graph.Full(5)
        _, alpham1 = g.maximum_cardinality_search()
        self.assertTrue(g.is_chordal(alpham1=alpham1))

    def testLineGraph(self):
        g = Graph(4, [(0, 1), (0, 2), (1, 2), (0, 3), (1, 3)])
        el = g.linegraph().get_edgelist()
        el.sort()
        self.assertTrue(
            el == [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (2, 4), (3, 4)]
        )

        g = Graph(4, [(0, 1), (0, 2), (1, 2), (0, 3), (1, 3)], directed=True)
        el = g.linegraph().get_edgelist()
        el.sort()
        self.assertTrue(el == [(0, 2), (0, 4)])

    def testMaximumCardinalitySearch(self):
        g = Graph()
        alpha, alpham1 = g.maximum_cardinality_search()
        self.assertListEqual([], alpha)
        self.assertListEqual([], alpham1)

        g = Graph.Famous("petersen")
        alpha, alpham1 = g.maximum_cardinality_search()

        self.assert_valid_maximum_cardinality_search_result(g, alpha, alpham1)

        g = Graph.GRG(100, 0.2)
        alpha, alpham1 = g.maximum_cardinality_search()

        self.assert_valid_maximum_cardinality_search_result(g, alpha, alpham1)


class PathTests(unittest.TestCase):
    def testDistances(self):
        g = Graph(
            10,
            [
                (0, 1),
                (0, 2),
                (0, 3),
                (1, 2),
                (1, 4),
                (1, 5),
                (2, 3),
                (2, 6),
                (3, 2),
                (3, 6),
                (4, 5),
                (4, 7),
                (5, 6),
                (5, 8),
                (5, 9),
                (7, 5),
                (7, 8),
                (8, 9),
                (5, 2),
                (2, 1),
            ],
            directed=True,
        )
        ws = [0, 2, 1, 0, 5, 2, 1, 1, 0, 2, 2, 8, 1, 1, 3, 1, 1, 4, 2, 1]
        g.es["weight"] = ws
        expected = [
            [0, 0, 0, 1, 5, 2, 1, 13, 3, 5],
            [inf, 0, 0, 1, 5, 2, 1, 13, 3, 5],
            [inf, 1, 0, 1, 6, 3, 1, 14, 4, 6],
            [inf, 1, 0, 0, 6, 3, 1, 14, 4, 6],
            [inf, 5, 4, 5, 0, 2, 3, 8, 3, 5],
            [inf, 3, 2, 3, 8, 0, 1, 16, 1, 3],
            [inf, inf, inf, inf, inf, inf, 0, inf, inf, inf],
            [inf, 4, 3, 4, 9, 1, 2, 0, 1, 4],
            [inf, inf, inf, inf, inf, inf, inf, inf, 0, 4],
            [inf, inf, inf, inf, inf, inf, inf, inf, inf, 0],
        ]
        self.assertTrue(g.distances(weights=ws) == expected)
        self.assertTrue(g.distances(weights="weight") == expected)
        self.assertTrue(
            g.distances(weights="weight", target=[2, 3])
            == [row[2:4] for row in expected]
        )

    def testGetShortestPaths(self):
        g = Graph(4, [(0, 1), (0, 2), (1, 3), (3, 2), (2, 1)], directed=True)
        sps = g.get_shortest_paths(0)
        expected = [[0], [0, 1], [0, 2], [0, 1, 3]]
        self.assertTrue(sps == expected)
        sps = g.get_shortest_paths(0, output="vpath")
        expected = [[0], [0, 1], [0, 2], [0, 1, 3]]
        self.assertTrue(sps == expected)
        sps = g.get_shortest_paths(0, output="epath")
        expected = [[], [0], [1], [0, 2]]
        self.assertTrue(sps == expected)
        self.assertRaises(ValueError, g.get_shortest_paths, 0, output="x")

    def testGetAllShortestPaths(self):
        g = Graph(4, [(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5)], directed=True)

        sps = sorted(g.get_all_shortest_paths(0, 0))
        expected = [[0]]
        self.assertEqual(expected, sps)

        sps = sorted(g.get_all_shortest_paths(0, 5))
        expected = [[0, 1, 2, 4, 5], [0, 1, 3, 4, 5]]
        self.assertEqual(expected, sps)

        sps = sorted(g.get_all_shortest_paths(1, 4))
        expected = [[1, 2, 4], [1, 3, 4]]
        self.assertEqual(expected, sps)

        g = Graph.Lattice([5, 5], circular=False)

        sps = sorted(g.get_all_shortest_paths(0, 12))
        expected = [
            [0, 1, 2, 7, 12],
            [0, 1, 6, 7, 12],
            [0, 1, 6, 11, 12],
            [0, 5, 6, 7, 12],
            [0, 5, 6, 11, 12],
            [0, 5, 10, 11, 12],
        ]
        self.assertEqual(expected, sps)

        g = Graph.Lattice([100, 100], circular=False)
        sps = sorted(g.get_all_shortest_paths(0, 202))
        expected = [
            [0, 1, 2, 102, 202],
            [0, 1, 101, 102, 202],
            [0, 1, 101, 201, 202],
            [0, 100, 101, 102, 202],
            [0, 100, 101, 201, 202],
            [0, 100, 200, 201, 202],
        ]
        self.assertEqual(expected, sps)

        g = Graph.Lattice([100, 100], circular=False)
        sps = sorted(g.get_all_shortest_paths(0, [0, 202]))
        self.assertEqual([[0]] + expected, sps)

        g = Graph([(0, 1), (1, 2), (0, 2)])
        g.es["weight"] = [0.5, 0.5, 1]
        sps = sorted(g.get_all_shortest_paths(0, weights="weight"))
        self.assertEqual([[0], [0, 1], [0, 1, 2], [0, 2]], sps)

        g = Graph.Lattice([4, 4], circular=False)
        g.es["weight"] = 1
        g.es[2, 8]["weight"] = 100
        sps = sorted(g.get_all_shortest_paths(0, [3, 12, 15], weights="weight"))
        self.assertEqual(20, len(sps))
        self.assertEqual(4, sum(1 for path in sps if path[-1] == 3))
        self.assertEqual(4, sum(1 for path in sps if path[-1] == 12))
        self.assertEqual(12, sum(1 for path in sps if path[-1] == 15))

    def testGetKShortestPaths(self):
        g = Graph(4, [(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5)], directed=True)
    
        sps = sorted(g.get_k_shortest_paths(0, 0))
        expected = [[0]]
        self.assertEqual(expected, sps)
    
        sps = sorted(g.get_k_shortest_paths(0, 5, 2))
        expected = [[0, 1, 2, 4, 5], [0, 1, 3, 4, 5]]
        self.assertEqual(expected, sps)
    
        sps = sorted(g.get_k_shortest_paths(1, 4, 2))
        expected = [[1, 2, 4], [1, 3, 4]]
        self.assertEqual(expected, sps)
    
        g = Graph.Lattice([5, 5], circular=False)
    
        sps = sorted(g.get_k_shortest_paths(0, 12, 6))
        expected = [
            [0, 1, 2, 7, 12],
            [0, 1, 6, 7, 12],
            [0, 1, 6, 11, 12],
            [0, 5, 6, 7, 12],
            [0, 5, 6, 11, 12],
            [0, 5, 10, 11, 12],
        ]
        self.assertEqual(expected, sps)
    
        g = Graph.Lattice([100, 100], circular=False)
        sps = sorted(g.get_k_shortest_paths(0, 202, 6))
        expected = [
            [0, 1, 2, 102, 202],
            [0, 1, 101, 102, 202],
            [0, 1, 101, 201, 202],
            [0, 100, 101, 102, 202],
            [0, 100, 101, 201, 202],
            [0, 100, 200, 201, 202],
        ]
        self.assertEqual(expected, sps)
    
        g = Graph([(0, 1), (1, 2), (0, 2)])
        g.es["weight"] = [0.5, 0.5, 1]
        sps = sorted(g.get_k_shortest_paths(0, 2, 2, weights="weight"))
        self.assertEqual(sorted([[0, 2], [0, 1, 2]]), sorted(sps))
    
    def testGetAllSimplePaths(self):
        g = Graph.Ring(20)
        sps = sorted(g.get_all_simple_paths(0, 10))
        self.assertEqual(
            [
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                [0, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10],
            ],
            sps,
        )

        g = Graph.Ring(20, directed=True)
        sps = sorted(g.get_all_simple_paths(0, 10))
        self.assertEqual([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]], sps)
        sps = sorted(g.get_all_simple_paths(0, 10, mode="in"))
        self.assertEqual([[0, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10]], sps)
        sps = sorted(g.get_all_simple_paths(0, 10, mode="all"))
        self.assertEqual(
            [
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                [0, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10],
            ],
            sps,
        )

        g = Graph.Lattice([4, 4], circular=False)
        g = Graph([(min(u, v), max(u, v)) for u, v in g.get_edgelist()], directed=True)
        sps = sorted(g.get_all_simple_paths(0, 15))
        self.assertEqual(20, len(sps))
        for path in sps:
            self.assertEqual(0, path[0])
            self.assertEqual(15, path[-1])
            curr = path[0]
            for next in path[1:]:
                self.assertTrue(g.are_connected(curr, next))
                curr = next

    def testPathLengthHist(self):
        g = Graph.Tree(15, 2)
        h = g.path_length_hist()
        self.assertTrue(h.unconnected == 0)
        self.assertTrue(
            [(int(value), x) for value, _, x in h.bins()]
            == [(1, 14), (2, 19), (3, 20), (4, 20), (5, 16), (6, 16)]
        )
        g = Graph.Full(5) + Graph.Full(4)
        h = g.path_length_hist()
        self.assertTrue(h.unconnected == 20)
        g.to_directed()
        h = g.path_length_hist()
        self.assertTrue(h.unconnected == 40)
        h = g.path_length_hist(False)
        self.assertTrue(h.unconnected == 20)


class DominatorTests(unittest.TestCase):
    def compareDomTrees(self, alist, blist):
        """
        Required due to NaN use for isolated nodes
        """
        if len(alist) != len(blist):
            return False
        for i, (a, b) in enumerate(zip(alist, blist)):
            if math.isnan(a) and math.isnan(b):
                continue
            elif a == b:
                continue
            else:
                return False
        return True

    def testDominators(self):
        # examples taken from igraph's examples/simple/dominator_tree.out

        # initial
        g = Graph(
            13,
            [
                (0, 1),
                (0, 7),
                (0, 10),
                (1, 2),
                (1, 5),
                (2, 3),
                (3, 4),
                (4, 3),
                (4, 0),
                (5, 3),
                (5, 6),
                (6, 3),
                (7, 8),
                (7, 10),
                (7, 11),
                (8, 9),
                (9, 4),
                (9, 8),
                (10, 11),
                (11, 12),
                (12, 9),
            ],
            directed=True,
        )
        s = [-1, 0, 1, 0, 0, 1, 5, 0, 0, 0, 0, 0, 11]
        r = g.dominator(0)
        self.assertTrue(self.compareDomTrees(s, r))

        # flipped edges
        g = Graph(
            13,
            [
                (1, 0),
                (2, 0),
                (3, 0),
                (4, 1),
                (1, 2),
                (4, 2),
                (5, 2),
                (6, 3),
                (7, 3),
                (12, 4),
                (8, 5),
                (9, 6),
                (9, 7),
                (10, 7),
                (5, 8),
                (11, 8),
                (11, 9),
                (9, 10),
                (9, 11),
                (0, 11),
                (8, 12),
            ],
            directed=True,
        )
        s = [-1, 0, 0, 0, 0, 0, 3, 3, 0, 0, 7, 0, 4]
        r = g.dominator(0, mode=IN)
        self.assertTrue(self.compareDomTrees(s, r))

        # disconnected components
        g = Graph(
            20,
            [
                (0, 1),
                (0, 2),
                (0, 3),
                (1, 4),
                (2, 1),
                (2, 4),
                (2, 8),
                (3, 9),
                (3, 10),
                (4, 15),
                (8, 11),
                (9, 12),
                (10, 12),
                (10, 13),
                (11, 8),
                (11, 14),
                (12, 14),
                (13, 12),
                (14, 12),
                (14, 0),
                (15, 11),
            ],
            directed=True,
        )
        s = [
            -1,
            0,
            0,
            0,
            0,
            float("nan"),
            float("nan"),
            float("nan"),
            0,
            3,
            3,
            0,
            0,
            10,
            0,
            4,
            float("nan"),
            float("nan"),
            float("nan"),
            float("nan"),
        ]
        r = g.dominator(0, mode=OUT)
        self.assertTrue(self.compareDomTrees(s, r))


def suite():
    simple_suite = unittest.defaultTestLoader.loadTestsFromTestCase(SimplePropertiesTests)
    degree_suite = unittest.defaultTestLoader.loadTestsFromTestCase(DegreeTests)
    local_transitivity_suite = unittest.defaultTestLoader.loadTestsFromTestCase(LocalTransitivityTests)
    biconnected_suite = unittest.defaultTestLoader.loadTestsFromTestCase(BiconnectedComponentTests)
    centrality_suite = unittest.defaultTestLoader.loadTestsFromTestCase(CentralityTests)
    neighborhood_suite = unittest.defaultTestLoader.loadTestsFromTestCase(NeighborhoodTests)
    path_suite = unittest.defaultTestLoader.loadTestsFromTestCase(PathTests)
    misc_suite = unittest.defaultTestLoader.loadTestsFromTestCase(MiscTests)
    dominator_suite = unittest.defaultTestLoader.loadTestsFromTestCase(DominatorTests)
    return unittest.TestSuite(
        [
            simple_suite,
            degree_suite,
            local_transitivity_suite,
            biconnected_suite,
            centrality_suite,
            neighborhood_suite,
            path_suite,
            misc_suite,
            dominator_suite,
        ]
    )


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
