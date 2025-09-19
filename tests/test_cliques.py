import unittest

from math import inf

from igraph import Graph

from .utils import temporary_file


class CliqueTests(unittest.TestCase):
    def setUp(self):
        self.g = Graph.Full(6)
        self.g.delete_edges([(0, 1), (0, 2), (3, 5)])

    def testCliques(self):
        tests = {
            (4, -1): [[1, 2, 3, 4], [1, 2, 4, 5]],
            (2, 2): [
                [0, 3],
                [0, 4],
                [0, 5],
                [1, 2],
                [1, 3],
                [1, 4],
                [1, 5],
                [2, 3],
                [2, 4],
                [2, 5],
                [3, 4],
                [4, 5],
            ],
            (-1, -1): [
                [0],
                [1],
                [2],
                [3],
                [4],
                [5],
                [0, 3],
                [0, 4],
                [0, 5],
                [1, 2],
                [1, 3],
                [1, 4],
                [1, 5],
                [2, 3],
                [2, 4],
                [2, 5],
                [3, 4],
                [4, 5],
                [0, 3, 4],
                [0, 4, 5],
                [1, 2, 3],
                [1, 2, 4],
                [1, 2, 5],
                [1, 3, 4],
                [1, 4, 5],
                [2, 3, 4],
                [2, 4, 5],
                [1, 2, 3, 4],
                [1, 2, 4, 5],
            ],
        }

        for (lo, hi), exp in tests.items():
            self.assertEqual(sorted(exp), sorted(map(sorted, self.g.cliques(lo, hi))))

        for (lo, hi), exp in tests.items():
            self.assertEqual(sorted(exp), sorted(map(sorted, self.g.cliques(lo, hi, max_results=inf))))

        for (lo, hi), exp in tests.items():
            observed = [sorted(cl) for cl in self.g.cliques(lo, hi, max_results=10)]
            for cl in observed:
                self.assertTrue(cl in exp)

        for (lo, hi), _ in tests.items():
            self.assertEqual([], self.g.cliques(lo, hi, max_results=0))

        for (lo, hi), _ in tests.items():
            with self.assertRaises(ValueError):
                self.g.cliques(lo, hi, max_results=-2)

    def testLargestCliques(self):
        self.assertEqual(
            sorted(map(sorted, self.g.largest_cliques())), [[1, 2, 3, 4], [1, 2, 4, 5]]
        )
        self.assertTrue(all(map(self.g.is_clique, self.g.largest_cliques())))

    def testMaximalCliques(self):
        self.assertEqual(
            sorted(map(sorted, self.g.maximal_cliques())),
            [[0, 3, 4], [0, 4, 5], [1, 2, 3, 4], [1, 2, 4, 5]],
        )
        self.assertTrue(all(map(self.g.is_clique, self.g.maximal_cliques())))
        self.assertEqual(
            sorted(map(sorted, self.g.maximal_cliques(min=4))),
            [[1, 2, 3, 4], [1, 2, 4, 5]],
        )
        self.assertEqual(
            sorted(map(sorted, self.g.maximal_cliques(max=3))), [[0, 3, 4], [0, 4, 5]]
        )

    def testMaximalCliquesFile(self):
        def read_cliques(fname):
            with open(fname) as fp:
                return sorted(sorted(int(item) for item in line.split()) for line in fp)

        with temporary_file() as fname:
            self.g.maximal_cliques(file=fname)
            self.assertEqual(
                [[0, 3, 4], [0, 4, 5], [1, 2, 3, 4], [1, 2, 4, 5]], read_cliques(fname)
            )

        with temporary_file() as fname:
            self.g.maximal_cliques(min=4, file=fname)
            self.assertEqual([[1, 2, 3, 4], [1, 2, 4, 5]], read_cliques(fname))

        with temporary_file() as fname:
            self.g.maximal_cliques(max=3, file=fname)
            self.assertEqual([[0, 3, 4], [0, 4, 5]], read_cliques(fname))

    def testCliqueNumber(self):
        self.assertEqual(self.g.clique_number(), 4)
        self.assertEqual(self.g.omega(), 4)


class IndependentVertexSetTests(unittest.TestCase):
    def setUp(self):
        self.g1 = Graph.Tree(5, 2, "undirected")
        self.g2 = Graph.Tree(10, 2, "undirected")

    def testIndependentVertexSets(self):
        tests = {
            (4, -1): [],
            (2, 2): [(0, 3), (0, 4), (1, 2), (2, 3), (2, 4), (3, 4)],
            (-1, -1): [
                (0,),
                (1,),
                (2,),
                (3,),
                (4,),
                (0, 3),
                (0, 4),
                (1, 2),
                (2, 3),
                (2, 4),
                (3, 4),
                (0, 3, 4),
                (2, 3, 4),
            ],
        }
        for (lo, hi), exp in tests.items():
            self.assertEqual(exp, self.g1.independent_vertex_sets(lo, hi))

    def testLargestIndependentVertexSets(self):
        self.assertEqual(
            self.g1.largest_independent_vertex_sets(), [(0, 3, 4), (2, 3, 4)]
        )
        self.assertTrue(
            all(
                map(
                    self.g1.is_independent_vertex_set,
                    self.g1.largest_independent_vertex_sets(),
                )
            )
        )

    def testMaximalIndependentVertexSets(self):
        self.assertEqual(
            self.g2.maximal_independent_vertex_sets(),
            [
                (0, 3, 4, 5, 6),
                (0, 3, 5, 6, 9),
                (0, 4, 5, 6, 7, 8),
                (0, 5, 6, 7, 8, 9),
                (1, 2, 7, 8, 9),
                (1, 5, 6, 7, 8, 9),
                (2, 3, 4),
                (2, 3, 9),
                (2, 4, 7, 8),
            ],
        )
        self.assertTrue(
            all(
                map(
                    self.g2.is_independent_vertex_set,
                    self.g2.maximal_independent_vertex_sets(),
                )
            )
        )

    def testIndependenceNumber(self):
        self.assertEqual(self.g2.independence_number(), 6)
        self.assertEqual(self.g2.alpha(), 6)


class CliqueBenchmark:
    """This is a benchmark, not a real test case. You can run it
    using:

    >>> from igraph.test.cliques import CliqueBenchmark
    >>> CliqueBenchmark().run()
    """

    def __init__(self):
        from time import time
        import gc

        self.time = time
        self.gc_collect = gc.collect

    def run(self):
        self.printIntro()
        self.testRandom()
        self.testMoonMoser()
        self.testGRG()

    def printIntro(self):
        print("n = number of vertices")
        print("#cliques = number of maximal cliques found")
        print("t1 = time required to determine the clique number")
        print("t2 = time required to determine and save all maximal cliques")
        print()

    def timeit(self, g):
        start = self.time()
        g.clique_number()
        mid = self.time()
        cl = g.maximal_cliques()
        end = self.time()
        self.gc_collect()
        return len(cl), mid - start, end - mid

    def testRandom(self):
        np = {
            100: [0.6, 0.7],
            300: [0.1, 0.2, 0.3, 0.4],
            500: [0.1, 0.2, 0.3],
            700: [0.1, 0.2],
            1000: [0.1, 0.2],
            10000: [0.001, 0.003, 0.005, 0.01, 0.02],
        }

        print()
        print("Erdos-Renyi random graphs")
        print("       n        p #cliques        t1        t2")
        for n in sorted(np.keys()):
            for p in np[n]:
                g = Graph.Erdos_Renyi(n, p)
                result = self.timeit(g)
                print("%8d %8.3f %8d %8.4fs %8.4fs" % tuple([n, p] + list(result)))

    def testMoonMoser(self):
        ns = [15, 27, 33]

        print()
        print("Moon-Moser graphs")
        print("       n exp_clqs #cliques        t1        t2")
        for n in ns:
            n3 = n // 3
            types = list(range(n3)) * 3
            el = [
                (i, j)
                for i in range(n)
                for j in range(i + 1, n)
                if types[i] != types[j]
            ]
            g = Graph(n, el)
            result = self.timeit(g)
            print(
                "%8d %8d %8d %8.4fs %8.4fs" % tuple([n, (3 ** (n / 3))] + list(result))
            )

    def testGRG(self):
        ns = [100, 1000, 5000, 10000, 25000, 50000]

        print()
        print("Geometric random graphs")
        print("       n        d #cliques        t1        t2")
        for n in ns:
            d = 2.0 / (n**0.5)
            g = Graph.GRG(n, d)
            result = self.timeit(g)
            print("%8d %8.3f %8d %8.4fs %8.4fs" % tuple([n, d] + list(result)))


def suite():
    clique_suite = unittest.defaultTestLoader.loadTestsFromTestCase(CliqueTests)
    indvset_suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        IndependentVertexSetTests
    )
    return unittest.TestSuite([clique_suite, indvset_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
