import unittest
from math import hypot
from igraph import Graph, Layout, BoundingBox, InternalError
from igraph import umap_compute_weights


class LayoutTests(unittest.TestCase):
    def testConstructor(self):
        layout = Layout([(0, 0, 1), (0, 1, 0), (1, 0, 0)])
        self.assertEqual(layout.dim, 3)
        layout = Layout([(0, 0, 1), (0, 1, 0), (1, 0, 0)], 3)
        self.assertEqual(layout.dim, 3)
        self.assertRaises(ValueError, Layout, [(0, 1), (1, 0)], 3)

    def testIndexing(self):
        layout = Layout([(0, 0, 1), (0, 1, 0), (1, 0, 0), (2, 1, 3)])
        self.assertEqual(len(layout), 4)
        self.assertEqual(layout[1], [0, 1, 0])
        self.assertEqual(layout[3], [2, 1, 3])

        row = layout[2]
        row[2] = 1
        self.assertEqual(layout[2], [1, 0, 1])

        del layout[1]
        self.assertEqual(len(layout), 3)

    def testScaling(self):
        layout = Layout([(0, 0, 1), (0, 1, 0), (1, 0, 0), (2, 1, 3)])
        layout.scale(1.5)
        self.assertEqual(
            layout.coords,
            [[0.0, 0.0, 1.5], [0.0, 1.5, 0.0], [1.5, 0.0, 0.0], [3.0, 1.5, 4.5]],
        )

        layout = Layout([(0, 0, 1), (0, 1, 0), (1, 0, 0), (2, 1, 3)])
        layout.scale(1, 1, 3)
        self.assertEqual(layout.coords, [[0, 0, 3], [0, 1, 0], [1, 0, 0], [2, 1, 9]])

        layout = Layout([(0, 0, 1), (0, 1, 0), (1, 0, 0), (2, 1, 3)])
        layout.scale((2, 2, 1))
        self.assertEqual(layout.coords, [[0, 0, 1], [0, 2, 0], [2, 0, 0], [4, 2, 3]])

        self.assertRaises(ValueError, layout.scale, 2, 3)

    def testTranslation(self):
        layout = Layout([(0, 0, 1), (0, 1, 0), (1, 0, 0), (2, 1, 3)])
        layout2 = layout.copy()

        layout.translate(1, 3, 2)
        self.assertEqual(layout.coords, [[1, 3, 3], [1, 4, 2], [2, 3, 2], [3, 4, 5]])

        layout.translate((-1, -3, -2))
        self.assertEqual(layout.coords, layout2.coords)

        self.assertRaises(ValueError, layout.translate, v=[3])

    def testCentroid(self):
        layout = Layout([(0, 0, 1), (0, 1, 0), (1, 0, 0), (2, 1, 3)])
        centroid = layout.centroid()
        self.assertEqual(len(centroid), 3)
        self.assertAlmostEqual(centroid[0], 0.75)
        self.assertAlmostEqual(centroid[1], 0.5)
        self.assertAlmostEqual(centroid[2], 1.0)

    def testBoundaries(self):
        layout = Layout([(0, 0, 1), (0, 1, 0), (1, 0, 0), (2, 1, 3)])
        self.assertEqual(layout.boundaries(), ([0, 0, 0], [2, 1, 3]))
        self.assertEqual(layout.boundaries(1), ([-1, -1, -1], [3, 2, 4]))

        layout = Layout([])
        self.assertRaises(ValueError, layout.boundaries)
        layout = Layout([], dim=3)
        self.assertRaises(ValueError, layout.boundaries)

    def testBoundingBox(self):
        layout = Layout([(0, 1), (2, 7)])
        self.assertEqual(layout.bounding_box(), BoundingBox(0, 1, 2, 7))
        self.assertEqual(layout.bounding_box(1), BoundingBox(-1, 0, 3, 8))
        layout = Layout([])
        self.assertEqual(layout.bounding_box(), BoundingBox(0, 0, 0, 0))

    def testCenter(self):
        layout = Layout([(-2, 0), (-2, -2), (0, -2), (0, 0)])
        layout.center()
        self.assertEqual(layout.coords, [[-1, 1], [-1, -1], [1, -1], [1, 1]])
        layout.center(5, 5)
        self.assertEqual(layout.coords, [[4, 6], [4, 4], [6, 4], [6, 6]])
        self.assertRaises(ValueError, layout.center, 3)
        self.assertRaises(TypeError, layout.center, p=6)

    def testFitInto(self):
        layout = Layout([(-2, 0), (-2, -2), (0, -2), (0, 0)])
        layout.fit_into(BoundingBox(5, 5, 8, 10), keep_aspect_ratio=False)
        self.assertEqual(layout.coords, [[5, 10], [5, 5], [8, 5], [8, 10]])
        layout = Layout([(-2, 0), (-2, -2), (0, -2), (0, 0)])
        layout.fit_into(BoundingBox(5, 5, 8, 10))
        self.assertEqual(layout.coords, [[5, 9], [5, 6], [8, 6], [8, 9]])

        layout = Layout([(-1, -1, -1), (0, 0, 0), (1, 1, 1), (2, 2, 0), (3, 3, -1)])
        layout.fit_into((0, 0, 0, 8, 8, 4))
        self.assertEqual(
            layout.coords, [[0, 0, 0], [2, 2, 2], [4, 4, 4], [6, 6, 2], [8, 8, 0]]
        )

        layout = Layout([])
        layout.fit_into((6, 7, 8, 11))
        self.assertEqual(layout.coords, [])

    def testToPolar(self):
        layout = Layout([(0, 0), (-1, 1), (0, 1), (1, 1)])
        layout.to_radial(min_angle=180, max_angle=0, max_radius=2)
        exp = [[0.0, 0.0], [-2.0, 0.0], [0.0, 2.0], [2, 0.0]]
        for idx in range(4):
            self.assertAlmostEqual(layout.coords[idx][0], exp[idx][0], places=3)
            self.assertAlmostEqual(layout.coords[idx][1], exp[idx][1], places=3)

    def testTransform(self):
        def tr(coord, dx, dy):
            return coord[0] + dx, coord[1] + dy

        layout = Layout([(1, 2), (3, 4)])
        layout.transform(tr, 2, -1)
        self.assertEqual(layout.coords, [[3, 1], [5, 3]])


class LayoutAlgorithmTests(unittest.TestCase):
    def testAuto(self):
        def layout_test(graph, test_with_dims=(2, 3)):
            lo = graph.layout("auto")
            self.assertTrue(isinstance(lo, Layout))
            self.assertEqual(len(lo[0]), 2)
            for dim in test_with_dims:
                lo = graph.layout("auto", dim=dim)
                self.assertTrue(isinstance(lo, Layout))
                self.assertEqual(len(lo[0]), dim)
            return lo

        g = Graph.Barabasi(10)
        layout_test(g)

        g = Graph.GRG(101, 0.2)
        del g.vs["x"]
        del g.vs["y"]
        layout_test(g)

        g = Graph.Full(10) * 2
        layout_test(g)

        g["layout"] = "graphopt"
        layout_test(g, test_with_dims=())

        g.vs["x"] = list(range(20))
        g.vs["y"] = list(range(20, 40))
        layout_test(g, test_with_dims=())

        del g["layout"]
        lo = layout_test(g, test_with_dims=(2,))
        self.assertEqual(
            [tuple(item) for item in lo],
            list(zip(list(range(20)), list(range(20, 40)))),
        )

        g.vs["z"] = list(range(40, 60))
        lo = layout_test(g)
        self.assertEqual(
            [tuple(item) for item in lo],
            list(zip(list(range(20)), list(range(20, 40)), list(range(40, 60)))),
        )

    def testCircle(self):
        def test_is_proper_circular_layout(graph, layout):
            xs, ys = list(zip(*layout))
            n = graph.vcount()
            self.assertEqual(n, len(xs))
            self.assertEqual(n, len(ys))
            self.assertAlmostEqual(0, sum(xs))
            self.assertAlmostEqual(0, sum(ys))
            for x, y in zip(xs, ys):
                self.assertAlmostEqual(1, x**2 + y**2)

        g = Graph.Ring(8)
        layout = g.layout("circle")
        test_is_proper_circular_layout(g, g.layout("circle"))

        order = [0, 2, 4, 6, 1, 3, 5, 7]
        ordered_layout = g.layout("circle", order=order)
        test_is_proper_circular_layout(g, g.layout("circle"))
        for v, w in enumerate(order):
            self.assertAlmostEqual(layout[v][0], ordered_layout[w][0])
            self.assertAlmostEqual(layout[v][1], ordered_layout[w][1])

    def testDavidsonHarel(self):
        # Quick smoke testing only
        g = Graph.Barabasi(100)
        lo = g.layout("dh")
        self.assertTrue(isinstance(lo, Layout))

    def testFruchtermanReingold(self):
        g = Graph.Barabasi(100)

        lo = g.layout("fr")
        self.assertTrue(isinstance(lo, Layout))

        lo = g.layout("fr", miny=list(range(100)))
        self.assertTrue(isinstance(lo, Layout))
        self.assertTrue(all(lo[i][1] >= i for i in range(100)))

        lo = g.layout("fr", miny=list(range(100)), maxy=list(range(100)))
        self.assertTrue(isinstance(lo, Layout))
        self.assertTrue(all(lo[i][1] == i for i in range(100)))

        lo = g.layout(
            "fr", miny=[2] * 100, maxy=[3] * 100, minx=[4] * 100, maxx=[6] * 100
        )
        self.assertTrue(isinstance(lo, Layout))
        bbox = lo.bounding_box()
        self.assertTrue(bbox.top >= 2)
        self.assertTrue(bbox.bottom <= 3)
        self.assertTrue(bbox.left >= 4)
        self.assertTrue(bbox.right <= 6)

    def testFruchtermanReingoldGrid(self):
        g = Graph.Barabasi(100)
        for grid_opt in ["grid", "nogrid", "auto", True, False]:
            lo = g.layout("fr", miny=list(range(100)), grid=grid_opt)
            self.assertTrue(isinstance(lo, Layout))
            self.assertTrue(all(lo[i][1] >= i for i in range(100)))

    def testKamadaKawai(self):
        g = Graph.Barabasi(100)

        lo = g.layout(
            "kk", miny=[2] * 100, maxy=[3] * 100, minx=[4] * 100, maxx=[6] * 100
        )

        self.assertTrue(isinstance(lo, Layout))
        bbox = lo.bounding_box()
        self.assertTrue(bbox.top >= 2)
        self.assertTrue(bbox.bottom <= 3)
        self.assertTrue(bbox.left >= 4)
        self.assertTrue(bbox.right <= 6)

        lo = g.layout(
            "kk",
            miny=[2] * 100,
            maxy=[3] * 100,
            minx=[4] * 100,
            maxx=[6] * 100,
            weights=range(10, g.ecount() + 10),
        )

        self.assertTrue(isinstance(lo, Layout))
        bbox = lo.bounding_box()
        self.assertTrue(bbox.top >= 2)
        self.assertTrue(bbox.bottom <= 3)
        self.assertTrue(bbox.left >= 4)
        self.assertTrue(bbox.right <= 6)

    def testMDS(self):
        g = Graph.Tree(10, 2)
        lo = g.layout("mds")
        self.assertTrue(isinstance(lo, Layout))

        dists = g.distances()
        lo = g.layout("mds", dists)
        self.assertTrue(isinstance(lo, Layout))

        g += Graph.Tree(10, 2)
        lo = g.layout("mds")
        self.assertTrue(isinstance(lo, Layout))

    def testUMAP(self):
        g = Graph()

        self.assertRaises(
            InternalError,
            g.layout_umap,
            min_dist=-0.01,
        )

        self.assertRaises(
            ValueError,
            g.layout_umap,
            epochs=-1,
        )

        self.assertRaises(
            ValueError,
            g.layout_umap,
            dim=1,
        )

        # Empty graph
        lo = g.layout_umap()
        self.assertTrue(isinstance(lo, Layout))
        self.assertEqual(lo.coords, [])

        # Singleton graph
        g = Graph(n=1)
        lo = g.layout_umap()
        self.assertEqual(lo.coords, [[0, 0]])

        # Graph with two articulation points
        edges = [
            0,
            1,
            0,
            2,
            0,
            3,
            1,
            2,
            1,
            3,
            2,
            3,
            3,
            4,
            4,
            5,
            5,
            6,
            6,
            7,
            7,
            8,
            6,
            8,
            7,
            9,
            6,
            9,
            8,
            9,
            7,
            10,
            8,
            10,
            9,
            10,
            10,
            11,
            9,
            11,
            8,
            11,
            7,
            11,
        ]
        edges = list(zip(edges[::2], edges[1::2]))
        dist = [
            0.1,
            0.09,
            0.12,
            0.09,
            0.1,
            0.1,
            0.9,
            0.9,
            0.9,
            0.2,
            0.1,
            0.1,
            0.1,
            0.1,
            0.1,
            0.08,
            0.05,
            0.1,
            0.08,
            0.12,
            0.09,
            0.11,
        ]
        g = Graph(edges)
        lo = g.layout_umap(dist=dist, epochs=500)
        self.assertTrue(isinstance(lo, Layout))

        # One should get two clusters in this case
        x, y = list(zip(*lo.coords))
        xmax, ymax, xmin, ymin = max(x), max(y), min(x), min(y)
        distmax = max(xmax - xmin, ymax - ymin)
        for iclu in range(0, 8, 7):
            xclu = sum(x[iclu : iclu + 4]) / 4
            yclu = sum(y[iclu : iclu + 4]) / 4
            for i in range(4):
                dx = x[iclu + i] - xclu
                dy = y[iclu + i] - yclu
                dxy = hypot(dx, dy)
                # Distance from each cluster's center should be relatively small
                self.assertLess(dxy, 0.2 * distmax)

        # Test single epoch with seed
        lo_adj = g.layout_umap(dist=dist, epochs=1, seed=lo)
        self.assertTrue(isinstance(lo_adj, Layout))

        # Same but inputting the coordinates
        lo_adj = g.layout_umap(dist=dist, epochs=1, seed=lo.coords)
        self.assertTrue(isinstance(lo_adj, Layout))

    def testUMAPComputeWeights(self):
        edges = [0, 1, 0, 2, 1, 2, 1, 3, 2, 3, 2, 0]
        edges = list(zip(edges[::2], edges[1::2]))
        dist = [1, 1.5, 1.8, 2.0, 3.4, 0.5]
        # NOTE: you need a directed graph to make sense of the symmetryzation
        g = Graph(edges, directed=True)
        weights = umap_compute_weights(g, dist)
        self.assertEqual(
            weights, [1.0, 1.0, 1.0, 1.1253517471925912e-07, 6.14421235332821e-06, 0.0]
        )

    def testLGL(self):
        g = Graph.Barabasi(100)
        lo = g.layout("lgl")
        self.assertTrue(isinstance(lo, Layout))

        lo = g.layout("lgl", root=5)
        self.assertTrue(isinstance(lo, Layout))

    def testReingoldTilford(self):
        g = Graph.Barabasi(100)
        lo = g.layout("rt")
        ys = [coord[1] for coord in lo]
        root = ys.index(0.0)
        self.assertEqual(ys, g.distances(root)[0])
        g = Graph.Barabasi(100) + Graph.Barabasi(50)
        lo = g.layout("rt", root=[0, 100])
        self.assertEqual(lo[100][1] - lo[0][1], 0)
        lo = g.layout("rt", root=[0, 100], rootlevel=[2, 10])
        self.assertEqual(lo[100][1] - lo[0][1], 8)

        # test named vertices
        g.vs["name"] = [f"v{i}" for i in range(g.vcount())]
        lo = g.layout("rt", root=["v0", "v100"])
        self.assertEqual(lo[100][1] - lo[0][1], 0)

    def testBipartite(self):
        g = Graph.Full_Bipartite(3, 2)

        lo = g.layout("bipartite")
        ys = [coord[1] for coord in lo]
        self.assertEqual([1, 1, 1, 0, 0], ys)

        lo = g.layout("bipartite", vgap=3)
        ys = [coord[1] for coord in lo]
        self.assertEqual([3, 3, 3, 0, 0], ys)

        lo = g.layout("bipartite", hgap=5)
        self.assertEqual({0, 5, 10}, {coord[0] for coord in lo if coord[1] == 1})
        self.assertEqual({2.5, 7.5}, {coord[0] for coord in lo if coord[1] == 0})

    def testDRL(self):
        # Regression test for bug #1091891
        g = Graph.Ring(10, circular=False) + 1
        lo = g.layout("drl")
        self.assertTrue(isinstance(lo, Layout))


def suite():
    layout_suite = unittest.defaultTestLoader.loadTestsFromTestCase(LayoutTests)
    layout_algorithm_suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        LayoutAlgorithmTests
    )
    return unittest.TestSuite([layout_suite, layout_algorithm_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
