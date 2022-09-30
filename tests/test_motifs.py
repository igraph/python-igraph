import unittest

from igraph import Graph


class MotifTests(unittest.TestCase):
    def setUp(self):
        self.g = Graph.Erdos_Renyi(100, 0.2, directed=True)

    def testDyads(self):
        # @note: this test is not exhaustive, it only checks whether the
        # L{DyadCensus} objects "understand" attribute and item accessors
        dc = self.g.dyad_census()
        accessors = ["mut", "mutual", "asym", "asymm", "asymmetric", "null"]
        for a in accessors:
            self.assertTrue(isinstance(getattr(dc, a), int))
            self.assertTrue(isinstance(dc[a], int))
        self.assertTrue(isinstance(list(dc), list))
        self.assertTrue(isinstance(tuple(dc), tuple))
        self.assertTrue(len(list(dc)) == 3)
        self.assertTrue(len(tuple(dc)) == 3)

    def testTriads(self):
        # @note: this test is not exhaustive, it only checks whether the
        # L{TriadCensus} objects "understand" attribute and item accessors
        tc = self.g.triad_census()
        accessors = ["003", "012", "021d", "030C"]
        for a in accessors:
            self.assertTrue(isinstance(getattr(tc, "t" + a), int))
            self.assertTrue(isinstance(tc[a], int))
        self.assertTrue(isinstance(list(tc), list))
        self.assertTrue(isinstance(tuple(tc), tuple))
        self.assertTrue(len(list(tc)) == 16)
        self.assertTrue(len(tuple(tc)) == 16)


class TrianglesTests(unittest.TestCase):
    def testListTriangles(self):
        g = Graph.Famous("petersen")
        self.assertEqual([], g.list_triangles())

        g = Graph([(0, 1), (1, 2), (2, 0), (1, 3), (3, 2), (4, 2), (4, 3)])
        observed = g.list_triangles()
        self.assertTrue(all(isinstance(x, tuple) for x in observed))
        observed = sorted(sorted(tri) for tri in observed)
        expected = [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
        self.assertEqual(observed, expected)

        g = Graph.GRG(100, 0.2)
        tri = Graph.Full(3)
        observed = sorted(sorted(tri) for tri in g.list_triangles())
        expected = sorted(x for x in g.get_subisomorphisms_vf2(tri) if x == sorted(x))
        self.assertEqual(observed, expected)


def suite():
    motif_suite = unittest.defaultTestLoader.loadTestsFromTestCase(MotifTests)
    triangles_suite = unittest.defaultTestLoader.loadTestsFromTestCase(TrianglesTests)
    return unittest.TestSuite([motif_suite, triangles_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
