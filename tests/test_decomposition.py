import math
import random
import unittest

from igraph import (
    Clustering,
    CohesiveBlocks,
    Cover,
    Graph,
    Histogram,
    InternalError,
    UniqueIdGenerator,
    VertexClustering,
    compare_communities,
    split_join_distance,
    set_random_number_generator,
)


class SubgraphTests(unittest.TestCase):
    def testSubgraph(self):
        g = Graph.Lattice([10, 10], circular=False, mutual=False)
        g.vs["id"] = list(range(g.vcount()))

        vs = [0, 1, 2, 10, 11, 12, 20, 21, 22]
        sg = g.subgraph(vs)

        self.assertTrue(
            sg.isomorphic(Graph.Lattice([3, 3], circular=False, mutual=False))
        )
        self.assertTrue(sg.vs["id"] == vs)

    def testSubgraphEdges(self):
        g = Graph.Lattice([10, 10], circular=False, mutual=False)
        g.es["id"] = list(range(g.ecount()))

        es = [0, 1, 2, 5, 20, 21, 22, 24, 38, 40]
        sg = g.subgraph_edges(es)
        exp = Graph.Lattice([3, 3], circular=False, mutual=False)
        exp.delete_edges([7, 8])

        self.assertTrue(sg.isomorphic(exp))
        self.assertTrue(sg.es["id"] == es)


class DecompositionTests(unittest.TestCase):
    def testDecomposeUndirected(self):
        g = Graph([(0, 1), (1, 2), (2, 3)], n=4, directed=False)
        components = g.decompose()

        assert len(components) == 1
        assert components[0].isomorphic(g)

        g = Graph.Full(5) + Graph.Full(3)
        components = g.decompose()

        assert len(components) == 2
        assert components[0].isomorphic(Graph.Full(5))
        assert components[1].isomorphic(Graph.Full(3))

    def testDecomposeDirected(self):
        g = Graph([(0, 1), (1, 2), (2, 3)], n=4, directed=True)
        components = g.decompose()

        g1 = Graph(1, directed=True)
        assert len(components) == 4
        for component in components:
            assert component.isomorphic(g1)

    def testKCores(self):
        g = Graph(
            11,
            [
                (0, 1),
                (0, 2),
                (0, 3),
                (1, 2),
                (1, 3),
                (2, 3),
                (2, 4),
                (2, 5),
                (3, 6),
                (3, 7),
                (1, 7),
                (7, 8),
                (1, 9),
                (1, 10),
                (9, 10),
            ],
        )
        self.assertTrue(g.coreness() == [3, 3, 3, 3, 1, 1, 1, 2, 1, 2, 2])
        self.assertTrue(g.shell_index() == g.coreness())

        edgelist = g.k_core(3).get_edgelist()
        edgelist.sort()
        self.assertTrue(edgelist == [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])


class ClusteringTests(unittest.TestCase):
    def setUp(self):
        self.cl = Clustering([0, 0, 0, 1, 1, 2, 1, 1, 4, 4])

    def testClusteringIndex(self):
        self.assertTrue(self.cl[0] == [0, 1, 2])
        self.assertTrue(self.cl[1] == [3, 4, 6, 7])
        self.assertTrue(self.cl[2] == [5])
        self.assertTrue(self.cl[3] == [])
        self.assertTrue(self.cl[4] == [8, 9])

    def testClusteringLength(self):
        self.assertTrue(len(self.cl) == 5)

    def testClusteringMembership(self):
        self.assertTrue(self.cl.membership == [0, 0, 0, 1, 1, 2, 1, 1, 4, 4])

    def testClusteringSizes(self):
        self.assertTrue(self.cl.sizes() == [3, 4, 1, 0, 2])
        self.assertTrue(self.cl.sizes(2, 4, 1) == [1, 2, 4])
        self.assertTrue(self.cl.size(2) == 1)

    def testClusteringHistogram(self):
        self.assertTrue(isinstance(self.cl.size_histogram(), Histogram))


class VertexClusteringTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph.Full(10)
        self.graph.vs["string"] = list("aaabbcccab")
        self.graph.vs["int"] = [17, 41, 23, 25, 64, 33, 3, 24, 47, 15]

    def testFromStringAttribute(self):
        cl = VertexClustering.FromAttribute(self.graph, "string")
        self.assertTrue(cl.membership == [0, 0, 0, 1, 1, 2, 2, 2, 0, 1])

    def testFromIntAttribute(self):
        cl = VertexClustering.FromAttribute(self.graph, "int")
        self.assertTrue(cl.membership == list(range(10)))
        cl = VertexClustering.FromAttribute(self.graph, "int", 15)
        self.assertTrue(cl.membership == [0, 1, 0, 0, 2, 1, 3, 0, 4, 0])
        cl = VertexClustering.FromAttribute(self.graph, "int", [10, 20, 30])
        self.assertTrue(cl.membership == [0, 1, 2, 2, 1, 1, 3, 2, 1, 0])

    def testClusterGraph(self):
        cl = VertexClustering(self.graph, [0, 0, 0, 1, 1, 1, 2, 2, 2, 2])
        self.graph.delete_edges(self.graph.es.select(_between=([0, 1, 2], [3, 4, 5])))
        clg = cl.cluster_graph(dict(string="concat", int=max))

        self.assertTrue(sorted(clg.get_edgelist()) == [(0, 2), (1, 2)])
        self.assertTrue(not clg.is_directed())
        self.assertTrue(clg.vs["string"] == ["aaa", "bbc", "ccab"])
        self.assertTrue(clg.vs["int"] == [41, 64, 47])

        clg = cl.cluster_graph(dict(string="concat", int=max), False)
        self.assertTrue(
            sorted(clg.get_edgelist())
            == [(0, 0)] * 3
            + [(0, 2)] * 12
            + [(1, 1)] * 3
            + [(1, 2)] * 12
            + [(2, 2)] * 6
        )
        self.assertTrue(not clg.is_directed())
        self.assertTrue(clg.vs["string"] == ["aaa", "bbc", "ccab"])
        self.assertTrue(clg.vs["int"] == [41, 64, 47])

    def testSizesWithNone(self):
        cl = VertexClustering(self.graph, [0, 0, 0, None, 1, 1, 2, None, 2, None])
        self.assertTrue(cl.sizes() == [3, 2, 2])


class CoverTests(unittest.TestCase):
    def setUp(self):
        self.cl = Cover([(0, 1, 2, 3), (3, 4, 5, 6, 9), (), (8, 9)])

    def testCoverIndex(self):
        self.assertTrue(self.cl[0] == [0, 1, 2, 3])
        self.assertTrue(self.cl[1] == [3, 4, 5, 6, 9])
        self.assertTrue(self.cl[2] == [])
        self.assertTrue(self.cl[3] == [8, 9])

    def testCoverLength(self):
        self.assertTrue(len(self.cl) == 4)

    def testCoverSizes(self):
        self.assertTrue(self.cl.sizes() == [4, 5, 0, 2])
        self.assertTrue(self.cl.sizes(1, 3, 0) == [5, 2, 4])
        self.assertTrue(self.cl.size(1) == 5)
        self.assertTrue(self.cl.size(2) == 0)

    def testCoverHistogram(self):
        self.assertTrue(isinstance(self.cl.size_histogram(), Histogram))

    def testCoverConstructorWithN(self):
        self.assertTrue(self.cl.n == 10)
        cl = Cover(self.cl, n=15)
        self.assertTrue(cl.n == 15)
        cl = Cover(self.cl, n=1)
        self.assertTrue(cl.n == 10)


class CommunityTests(unittest.TestCase):
    def reindexMembership(self, cl):
        if hasattr(cl, "membership"):
            cl = cl.membership
        idgen = UniqueIdGenerator()
        return [idgen[i] for i in cl]

    def assertMembershipsEqual(self, observed, expected):
        if hasattr(observed, "membership"):
            observed = observed.membership
        if hasattr(expected, "membership"):
            expected = expected.membership
        self.assertEqual(
            self.reindexMembership(expected), self.reindexMembership(observed)
        )

    def testClauset(self):
        # Two cliques of size 5 with one connecting edge
        g = Graph.Full(5) + Graph.Full(5)
        g.add_edges([(0, 5)])
        cl = g.community_fastgreedy().as_clustering()
        self.assertMembershipsEqual(cl, [0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
        self.assertAlmostEqual(cl.q, 0.4523, places=3)

        # Lollipop, weighted
        g = Graph.Full(4) + Graph.Full(2)
        g.add_edges([(3, 4)])
        weights = [1, 1, 1, 1, 1, 1, 10, 10]
        cl = g.community_fastgreedy(weights).as_clustering()
        self.assertMembershipsEqual(cl, [0, 0, 0, 1, 1, 1])
        self.assertAlmostEqual(cl.q, 0.1708, places=3)

        # Same graph, different weights
        g.es["weight"] = [3] * g.ecount()
        cl = g.community_fastgreedy("weight").as_clustering()
        self.assertMembershipsEqual(cl, [0, 0, 0, 0, 1, 1])
        self.assertAlmostEqual(cl.q, 0.1796, places=3)

        # Disconnected graph
        g = Graph.Full(4) + Graph.Full(4) + Graph.Full(3) + Graph.Full(2)
        cl = g.community_fastgreedy().as_clustering()
        self.assertMembershipsEqual(cl, [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3])

        # Empty graph
        g = Graph(20)
        cl = g.community_fastgreedy().as_clustering()
        self.assertMembershipsEqual(cl, list(range(g.vcount())))

    def testEdgeBetweenness(self):
        # Full graph, no weights
        g = Graph.Full(5)
        cl = g.community_edge_betweenness().as_clustering()
        self.assertMembershipsEqual(cl, [0] * 5)

        # Full graph with weights
        g.es["weight"] = 1
        g[0, 1] = g[1, 2] = g[2, 0] = g[3, 4] = 10

        # We need to specify the desired cluster count explicitly; this is
        # because edge betweenness-based detection does not play well with
        # modularity-based cluster count selection (the edge weights have
        # different semantics) so we need to give igraph a hint
        cl = g.community_edge_betweenness(weights="weight").as_clustering(n=2)
        self.assertMembershipsEqual(cl, [0, 0, 0, 1, 1])
        self.assertAlmostEqual(cl.q, 0.2750, places=3)

    def testEigenvector(self):
        g = Graph.Full(5) + Graph.Full(5)
        g.add_edges([(0, 5)])
        cl = g.community_leading_eigenvector()
        self.assertMembershipsEqual(cl, [0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
        self.assertAlmostEqual(cl.q, 0.4523, places=3)
        cl = g.community_leading_eigenvector(2)
        self.assertMembershipsEqual(cl, [0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
        self.assertAlmostEqual(cl.q, 0.4523, places=3)

    def testInfomap(self):
        g = Graph.Famous("zachary")
        cl = g.community_infomap()
        self.assertAlmostEqual(cl.codelength, 4.60605, places=3)
        self.assertAlmostEqual(cl.q, 0.40203, places=3)
        self.assertMembershipsEqual(
            cl,
            [1, 1, 1, 1, 2, 2, 2, 1, 0, 1, 2, 1, 1, 1, 0, 0, 2, 1, 0, 1, 0, 1]
            + [0] * 12,
        )

        # Smoke testing with vertex and edge weights
        v_weights = [random.randint(1, 5) for _ in range(g.vcount())]
        e_weights = [random.randint(1, 5) for _ in range(g.ecount())]
        cl = g.community_infomap(edge_weights=e_weights)
        cl = g.community_infomap(vertex_weights=v_weights)
        cl = g.community_infomap(edge_weights=e_weights, vertex_weights=v_weights)

    def testLabelPropagation(self):
        # Nothing to test there really, since the algorithm is pretty
        # nondeterministic. We just do a few quick smoke tests.
        g = Graph.GRG(100, 0.2)
        cl = g.community_label_propagation()

        g = Graph([(0, 1), (1, 2), (2, 3)])
        g.es["weight"] = [2, 1, 2]
        g.vs["initial"] = [0, -1, -1, 1]
        cl = g.community_label_propagation("weight", "initial", [1, 0, 0, 1])
        self.assertMembershipsEqual(cl, [0, 0, 1, 1])
        cl = g.community_label_propagation(initial="initial", fixed=[1, 0, 0, 1])
        self.assertTrue(
            cl.membership == [0, 0, 1, 1]
            or cl.membership == [0, 1, 1, 1]
            or cl.membership == [0, 0, 0, 1]
        )

        g = Graph.GRG(100, 0.2)
        g.vs["initial"] = [
            0 if i == 0 else 1 if i == 99 else 2 if i == 49 else random.randint(0, 50)
            for i in range(g.vcount())
        ]
        g.vs["dont_move"] = [i in (0, 49, 99) for i in range(g.vcount())]
        cl = g.community_label_propagation(initial="initial", fixed="dont_move")

        # igraph is free to reorder the clusters so only co-membership will be
        # preserved, hence the next assertion
        self.assertTrue(
            cl.membership[0] != cl.membership[49]
            and cl.membership[49] != cl.membership[99]
        )
        self.assertTrue(x >= 0 and x <= 5 for x in cl.membership)

    def testMultilevel(self):
        # Example graph from the paper
        random.seed(42)
        g = Graph(16)
        g += [
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
            (1, 2),
            (1, 4),
            (1, 7),
            (2, 4),
            (2, 5),
            (2, 6),
            (3, 7),
            (4, 10),
            (5, 7),
            (5, 11),
            (6, 7),
            (6, 11),
            (8, 9),
            (8, 10),
            (8, 11),
            (8, 14),
            (8, 15),
            (9, 12),
            (9, 14),
            (10, 11),
            (10, 12),
            (10, 13),
            (10, 14),
            (11, 13),
        ]

        cls = g.community_multilevel(return_levels=True)
        self.assertTrue(len(cls) == 2)
        self.assertMembershipsEqual(
            cls[0], [1, 1, 1, 0, 1, 1, 0, 0, 2, 2, 2, 3, 2, 3, 2, 2]
        )
        self.assertMembershipsEqual(
            cls[1], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
        )
        self.assertAlmostEqual(cls[0].q, 0.346301, places=5)
        self.assertAlmostEqual(cls[1].q, 0.392219, places=5)

        cls = g.community_multilevel()
        self.assertTrue(len(cls.membership) == g.vcount())
        self.assertMembershipsEqual(
            cls, [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
        )
        self.assertAlmostEqual(cls.q, 0.392219, places=5)

    def testOptimalModularity(self):
        try:
            g = Graph.Famous("bull")

            cl = g.community_optimal_modularity()
            self.assertTrue(len(cl) == 2)
            self.assertMembershipsEqual(cl, [0, 0, 1, 0, 1])
            self.assertAlmostEqual(cl.q, 0.08, places=7)

            ws = [i % 5 for i in range(g.ecount())]
            cl = g.community_optimal_modularity(weights=ws)
            self.assertAlmostEqual(
                cl.q, g.modularity(cl.membership, weights=ws), places=7
            )

            g = Graph.Famous("zachary")
            cl = g.community_optimal_modularity()
            self.assertTrue(len(cl) == 4)
            self.assertMembershipsEqual(
                cl,
                [
                    0,
                    0,
                    0,
                    0,
                    1,
                    1,
                    1,
                    0,
                    2,
                    2,
                    1,
                    0,
                    0,
                    0,
                    2,
                    2,
                    1,
                    0,
                    2,
                    0,
                    2,
                    0,
                    2,
                    3,
                    3,
                    3,
                    2,
                    3,
                    3,
                    2,
                    2,
                    3,
                    2,
                    2,
                ],
            )
            self.assertAlmostEqual(cl.q, 0.4197896, places=7)

            ws = [2 + (i % 3) for i in range(g.ecount())]
            cl = g.community_optimal_modularity(weights=ws)
            self.assertAlmostEqual(
                cl.q, g.modularity(cl.membership, weights=ws), places=7
            )

        except NotImplementedError:
            # Well, meh
            pass

    def testSpinglass(self):
        g = Graph.Full(5) + Graph.Full(5) + Graph.Full(5)
        g += [(0, 5), (5, 10), (10, 0)]

        # Spinglass community detection is a bit unstable, so run it three times
        ok = False
        for i in range(3):
            cl = g.community_spinglass()
            if self.reindexMembership(cl) == [
                0,
                0,
                0,
                0,
                0,
                1,
                1,
                1,
                1,
                1,
                2,
                2,
                2,
                2,
                2,
            ]:
                ok = True
                break
        self.assertTrue(ok)

    def testWalktrap(self):
        g = Graph.Full(5) + Graph.Full(5) + Graph.Full(5)
        g += [(0, 5), (5, 10), (10, 0)]
        cl = g.community_walktrap().as_clustering()
        self.assertMembershipsEqual(cl, [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2])
        cl = g.community_walktrap(steps=3).as_clustering()
        self.assertMembershipsEqual(cl, [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2])

    def testLeiden(self):

        # Example from paper (Fig. C.1)
        high_weight = 3.0
        low_weight = 3.0 / 2.0
        edges = [
            (0, 1, high_weight),
            (2, 3, high_weight),
            (4, 2, high_weight),
            (3, 4, high_weight),
            (5, 6, high_weight),
            (7, 5, high_weight),
            (6, 7, high_weight),
            (0, 2, low_weight),
            (0, 3, low_weight),
            (0, 4, low_weight),
            (1, 5, low_weight),
            (1, 6, low_weight),
            (1, 7, low_weight),
        ]
        G = Graph.TupleList(edges, weights=True)

        import random

        random.seed(42)
        set_random_number_generator(random)
        # We don't find the optimal partition if we are greedy
        cl = G.community_leiden(
            "CPM", resolution_parameter=1, weights="weight", beta=0, n_iterations=-1
        )
        self.assertMembershipsEqual(cl, [0, 0, 1, 1, 1, 2, 2, 2])

        random.seed(42)
        set_random_number_generator(random)
        # We can find the optimal partition if we allow for non-decreasing moves
        # (The randomness is only present in the refinement, which is why we
        # start from all nodes in the same community: this should then be
        # refined).
        cl = G.community_leiden(
            "CPM",
            resolution_parameter=1,
            weights="weight",
            beta=5,
            n_iterations=-1,
            initial_membership=[0] * G.vcount(),
        )
        self.assertMembershipsEqual(cl, [0, 1, 0, 0, 0, 1, 1, 1])


class CohesiveBlocksTests(unittest.TestCase):
    def genericTests(self, cbs):
        self.assertTrue(isinstance(cbs, CohesiveBlocks))
        self.assertTrue(
            all(cbs.cohesion(i) == c for i, c in enumerate(cbs.cohesions()))
        )
        self.assertTrue(all(cbs.parent(i) == c for i, c in enumerate(cbs.parents())))
        self.assertTrue(
            all(cbs.max_cohesion(i) == c for i, c in enumerate(cbs.max_cohesions()))
        )

    def testCohesiveBlocks1(self):
        # Taken from the igraph R manual
        g = Graph.Full(4) + Graph(2) + [(3, 4), (4, 5), (4, 2)]
        g *= 3
        g += [(0, 6), (1, 7), (0, 12), (4, 0), (4, 1)]

        cbs = g.cohesive_blocks()
        self.genericTests(cbs)
        self.assertEqual(
            sorted(list(cbs)),
            [
                list(range(0, 5)),
                list(range(18)),
                [0, 1, 2, 3, 4, 6, 7, 8, 9, 10],
                list(range(6, 10)),
                list(range(12, 16)),
                list(range(12, 17)),
            ],
        )
        self.assertEqual(cbs.cohesions(), [1, 2, 2, 4, 3, 3])
        self.assertEqual(
            cbs.max_cohesions(), [4, 4, 4, 4, 4, 1, 3, 3, 3, 3, 2, 1, 3, 3, 3, 3, 2, 1]
        )
        self.assertEqual(cbs.parents(), [None, 0, 0, 1, 2, 1])

    def testCohesiveBlocks2(self):
        # Taken from the Moody-White paper
        g = Graph.Formula(
            "1-2:3:4:5:6, 2-3:4:5:7, 3-4:6:7, 4-5:6:7, "
            "5-6:7:21, 6-7, 7-8:11:14:19, 8-9:11:14, 9-10, "
            "10-12:13, 11-12:14, 12-16, 13-16, 14-15, 15-16, "
            "17-18:19:20, 18-20:21, 19-20:22:23, 20-21, "
            "21-22:23, 22-23"
        )

        cbs = g.cohesive_blocks()
        self.genericTests(cbs)

        expected_blocks = [
            list(range(7)),
            list(range(23)),
            list(range(7)) + list(range(16, 23)),
            list(range(6, 16)),
            [6, 7, 10, 13],
        ]
        observed_blocks = sorted(
            sorted(int(x) - 1 for x in g.vs[bl]["name"]) for bl in cbs
        )
        self.assertEqual(expected_blocks, observed_blocks)
        self.assertTrue(cbs.cohesions() == [1, 2, 2, 5, 3])
        self.assertTrue(cbs.parents() == [None, 0, 0, 1, 2])
        self.assertTrue(
            sorted(cbs.hierarchy().get_edgelist()) == [(0, 1), (0, 2), (1, 3), (2, 4)]
        )

    def testCohesiveBlockingErrors(self):
        g = Graph.GRG(100, 0.2)
        g.to_directed()
        self.assertRaises(InternalError, g.cohesive_blocks)


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.clusterings = [
            ([0, 0, 0, 1, 1, 1], [1, 1, 1, 0, 0, 0]),
            ([0, 0, 0, 1, 1, 1], [0, 0, 1, 1, 2, 2]),
            ([0, 0, 0, 0, 0, 0], [0, 1, 2, 3, 4, 5]),
            (
                [0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 2],
                [2, 0, 1, 0, 2, 0, 2, 0, 1, 0, 3, 1],
            ),
        ]

    def _testMethod(self, method, expected):
        for clusters, result in zip(self.clusterings, expected):
            self.assertAlmostEqual(
                compare_communities(method=method, *clusters), result, places=3
            )

    def testCompareVI(self):
        expected = [0, 0.8675, math.log(6)]
        self._testMethod(None, expected)
        self._testMethod("vi", expected)

    def testCompareNMI(self):
        expected = [1, 0.5158, 0]
        self._testMethod("nmi", expected)

    def testCompareSplitJoin(self):
        expected = [0, 3, 5, 11]
        self._testMethod("split_join", expected)
        l1 = [1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3]
        l2 = [3, 1, 2, 1, 3, 1, 3, 1, 2, 1, 4, 2]
        self.assertEqual(split_join_distance(l1, l2), (6, 5))

    def testCompareRand(self):
        expected = [1, 2 / 3.0, 0, 0.590909]
        self._testMethod("rand", expected)

    def testCompareAdjustedRand(self):
        expected = [1, 0.242424, 0, -0.04700353]
        self._testMethod("adjusted_rand", expected)

    def testRemoveNone(self):
        l1 = Clustering([1, 1, 1, None, None, 2, 2, 2, 2])
        l2 = Clustering([1, 1, 2, 2, None, 2, 3, 3, None])
        self.assertAlmostEqual(
            compare_communities(l1, l2, "nmi", remove_none=True), 0.5158, places=3
        )


def suite():
    decomposition_suite = unittest.defaultTestLoader.loadTestsFromTestCase(DecompositionTests)
    clustering_suite = unittest.defaultTestLoader.loadTestsFromTestCase(ClusteringTests)
    vertex_clustering_suite = unittest.defaultTestLoader.loadTestsFromTestCase(VertexClusteringTests)
    cover_suite = unittest.defaultTestLoader.loadTestsFromTestCase(CoverTests)
    community_suite = unittest.defaultTestLoader.loadTestsFromTestCase(CommunityTests)
    cohesive_blocks_suite = unittest.defaultTestLoader.loadTestsFromTestCase(CohesiveBlocksTests)
    comparison_suite = unittest.defaultTestLoader.loadTestsFromTestCase(ComparisonTests)
    return unittest.TestSuite(
        [
            decomposition_suite,
            clustering_suite,
            vertex_clustering_suite,
            cover_suite,
            community_suite,
            cohesive_blocks_suite,
            comparison_suite,
        ]
    )


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
