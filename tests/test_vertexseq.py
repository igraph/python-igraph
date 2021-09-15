# vim:ts=4 sw=4 sts=4:

import unittest

from igraph import *

from .utils import is_pypy

try:
    import numpy as np
except ImportError:
    np = None


class VertexTests(unittest.TestCase):
    def setUp(self):
        self.g = Graph.Full(10)

    def testHash(self):
        data = {}
        n = self.g.vcount()
        for i in range(n):
            code1 = hash(self.g.vs[i])
            code2 = hash(self.g.vs[i])
            self.assertEqual(code1, code2)
            data[self.g.vs[i]] = i

        for i in range(n):
            self.assertEqual(i, data[self.g.vs[i]])

    def testRichCompare(self):
        g2 = Graph.Full(10)
        for i in range(self.g.vcount()):
            for j in range(self.g.vcount()):
                self.assertEqual(i == j, self.g.vs[i] == self.g.vs[j])
                self.assertEqual(i != j, self.g.vs[i] != self.g.vs[j])
                self.assertEqual(i < j, self.g.vs[i] < self.g.vs[j])
                self.assertEqual(i > j, self.g.vs[i] > self.g.vs[j])
                self.assertEqual(i <= j, self.g.vs[i] <= self.g.vs[j])
                self.assertEqual(i >= j, self.g.vs[i] >= self.g.vs[j])
                self.assertFalse(self.g.vs[i] == g2.vs[j])
                self.assertFalse(self.g.vs[i] != g2.vs[j])
                self.assertFalse(self.g.vs[i] < g2.vs[j])
                self.assertFalse(self.g.vs[i] > g2.vs[j])
                self.assertFalse(self.g.vs[i] <= g2.vs[j])
                self.assertFalse(self.g.vs[i] >= g2.vs[j])
                self.assertFalse(self.g.es[i] == self.g.vs[j])

    def testUpdateAttributes(self):
        v = self.g.vs[0]

        v.update_attributes(a=2)
        self.assertEqual(v["a"], 2)

        v.update_attributes([("a", 3), ("b", 4)], c=5, d=6)
        self.assertEqual(v.attributes(), dict(a=3, b=4, c=5, d=6))

        v.update_attributes(dict(b=44, c=55))
        self.assertEqual(v.attributes(), dict(a=3, b=44, c=55, d=6))

    def testPhantomVertex(self):
        v = self.g.vs[9]
        v.delete()

        # v is now a phantom vertex; try to freak igraph out now :)
        self.assertRaises(ValueError, v.update_attributes, a=2)
        self.assertRaises(ValueError, v.__getitem__, "a")
        self.assertRaises(ValueError, v.__setitem__, "a", 4)
        self.assertRaises(ValueError, v.__delitem__, "a")
        self.assertRaises(ValueError, v.attributes)

    def testIncident(self):
        g = Graph.Famous("petersen")
        g.to_directed()

        method_table = {"all": "all_edges", "in": "in_edges", "out": "out_edges"}

        for i in range(g.vcount()):
            vertex = g.vs[i]
            for mode, method_name in list(method_table.items()):
                method = getattr(vertex, method_name)
                self.assertEqual(
                    g.incident(i, mode=mode),
                    [edge.index for edge in vertex.incident(mode=mode)],
                )
                self.assertEqual(
                    g.incident(i, mode=mode), [edge.index for edge in method()]
                )

    def testNeighbors(self):
        g = Graph.Famous("petersen")
        g.to_directed()

        for i in range(g.vcount()):
            vertex = g.vs[i]
            for mode in "all in out".split():
                self.assertEqual(
                    g.neighbors(i, mode=mode),
                    [edge.index for edge in vertex.neighbors(mode=mode)],
                )

    @unittest.skipIf(is_pypy, "skipped on PyPy because we do not have access to docstrings")
    def testProxyMethods(self):
        # We only test with connected graphs because disconnected graphs might
        # print a warning when shortest_paths() is invoked on them and we want
        # to avoid that in the test output.
        while True:
            g = Graph.GRG(10, 0.6)
            if g.is_connected():
                break

        v = g.vs[0]

        # - neighbors(), predecessors() and succesors() are ignored because they
        #   return vertex lists while the methods in Graph return vertex index
        #   lists.
        # - incident(), all_edges(), in_edges() and out_edges() are ignored
        #   because it returns an edge list while the methods in Graph return
        #   edge indices.
        # - pagerank() and personalized_pagerank() are ignored because of numerical
        #   inaccuracies
        # - delete() is ignored because it mutates the graph
        ignore = (
            "neighbors predecessors successors pagerank personalized_pagerank"
            " delete incident all_edges in_edges out_edges"
        )
        ignore = set(ignore.split())

        # Methods not listed here are expected to return an int or a float
        return_types = {"get_shortest_paths": list, "shortest_paths": list}

        for name in Vertex.__dict__:
            if name in ignore:
                continue

            func = getattr(v, name)
            docstr = func.__doc__

            if not docstr.startswith("Proxy method"):
                continue

            result = func()
            self.assertEqual(
                getattr(g, name)(v.index),
                result,
                msg=("Vertex.%s proxy method misbehaved" % name),
            )

            return_type = return_types.get(name, (int, float))
            self.assertTrue(
                isinstance(result, return_type),
                msg=("Vertex.%s proxy method did not return %s" % (name, return_type)),
            )


class VertexSeqTests(unittest.TestCase):
    def setUp(self):
        self.g = Graph.Full(10)
        self.g.vs["test"] = list(range(10))
        self.g.vs["name"] = list("ABCDEFGHIJ")

    def testCreation(self):
        self.assertTrue(len(VertexSeq(self.g)) == 10)
        self.assertTrue(len(VertexSeq(self.g, 2)) == 1)
        self.assertTrue(len(VertexSeq(self.g, [1, 2, 3])) == 3)
        self.assertTrue(VertexSeq(self.g, [1, 2, 3]).indices == [1, 2, 3])
        self.assertRaises(ValueError, VertexSeq, self.g, 12)
        self.assertRaises(ValueError, VertexSeq, self.g, [12])
        self.assertTrue(self.g.vs.graph == self.g)

    def testIndexing(self):
        n = self.g.vcount()
        for i in range(n):
            self.assertEqual(i, self.g.vs[i].index)
            self.assertEqual(n - i - 1, self.g.vs[-i - 1].index)
        self.assertRaises(IndexError, self.g.vs.__getitem__, n)
        self.assertRaises(IndexError, self.g.vs.__getitem__, -n - 1)
        self.assertRaises(TypeError, self.g.vs.__getitem__, 1.5)

    @unittest.skipIf(np is None, "test case depends on NumPy")
    def testNumPyIndexing(self):
        n = self.g.vcount()
        for i in range(self.g.vcount()):
            arr = np.array([i])
            self.assertEqual(i, self.g.vs[arr[0]].index)
            arr = np.array([-i - 1])
            self.assertEqual(n - i - 1, self.g.vs[arr[0]].index)

        arr = np.array([n])
        self.assertRaises(IndexError, self.g.vs.__getitem__, arr[0])

        arr = np.array([-n - 1])
        self.assertRaises(IndexError, self.g.vs.__getitem__, arr[0])

        arr = np.array([1.5])
        self.assertRaises(TypeError, self.g.vs.__getitem__, arr[0])

        ind = [1, 3, 5, 8, 3, 2]
        arr = np.array(ind)
        self.assertEqual(ind, [vertex.index for vertex in self.g.vs[arr.tolist()]])
        self.assertEqual(ind, [vertex.index for vertex in self.g.vs[list(arr)]])

    def testPartialAttributeAssignment(self):
        only_even = self.g.vs.select(lambda v: (v.index % 2 == 0))
        only_even["test"] = [0] * len(only_even)
        self.assertTrue(self.g.vs["test"] == [0, 1, 0, 3, 0, 5, 0, 7, 0, 9])
        only_even["test2"] = list(range(5))
        self.assertTrue(
            self.g.vs["test2"] == [0, None, 1, None, 2, None, 3, None, 4, None]
        )

    def testSequenceReusing(self):
        if "test" in self.g.vertex_attributes():
            del self.g.vs["test"]

        self.g.vs["test"] = ["A", "B", "C"]
        self.assertTrue(
            self.g.vs["test"] == ["A", "B", "C", "A", "B", "C", "A", "B", "C", "A"]
        )
        self.g.vs["test"] = "ABC"
        self.assertTrue(self.g.vs["test"] == ["ABC"] * 10)

        only_even = self.g.vs.select(lambda v: (v.index % 2 == 0))
        only_even["test"] = ["D", "E"]
        self.assertTrue(
            self.g.vs["test"]
            == ["D", "ABC", "E", "ABC", "D", "ABC", "E", "ABC", "D", "ABC"]
        )
        del self.g.vs["test"]
        only_even["test"] = ["D", "E"]
        self.assertTrue(
            self.g.vs["test"] == ["D", None, "E", None, "D", None, "E", None, "D", None]
        )

    def testAllSequence(self):
        self.assertTrue(len(self.g.vs) == 10)
        self.assertTrue(self.g.vs["test"] == list(range(10)))

    def testEmptySequence(self):
        empty_vs = self.g.vs.select(None)
        self.assertTrue(len(empty_vs) == 0)
        self.assertRaises(IndexError, empty_vs.__getitem__, 0)
        self.assertRaises(KeyError, empty_vs.__getitem__, "nonexistent")
        self.assertTrue(empty_vs["test"] == [])
        empty_vs = self.g.vs[[]]
        self.assertTrue(len(empty_vs) == 0)
        empty_vs = self.g.vs[()]
        self.assertTrue(len(empty_vs) == 0)

    def testCallableFilteringFind(self):
        vertex = self.g.vs.find(lambda v: (v.index % 2 == 1))
        self.assertTrue(vertex.index == 1)
        self.assertRaises(IndexError, self.g.vs.find, lambda v: (v.index % 2 == 3))

    def testCallableFilteringSelect(self):
        only_even = self.g.vs.select(lambda v: (v.index % 2 == 0))
        self.assertTrue(len(only_even) == 5)
        self.assertRaises(KeyError, only_even.__getitem__, "nonexistent")
        self.assertTrue(only_even["test"] == [0, 2, 4, 6, 8])

    def testChainedCallableFilteringSelect(self):
        only_div_six = self.g.vs.select(
            lambda v: (v.index % 2 == 0), lambda v: (v.index % 3 == 0)
        )
        self.assertTrue(len(only_div_six) == 2)
        self.assertTrue(only_div_six["test"] == [0, 6])

        only_div_six = self.g.vs.select(lambda v: (v.index % 2 == 0)).select(
            lambda v: (v.index % 3 == 0)
        )
        self.assertTrue(len(only_div_six) == 2)
        self.assertTrue(only_div_six["test"] == [0, 6])

    def testIntegerFilteringFind(self):
        self.assertEqual(self.g.vs.find(3).index, 3)
        self.assertEqual(self.g.vs.select(2, 3, 4, 2).find(3).index, 2)
        self.assertRaises(IndexError, self.g.vs.find, 17)

    def testIntegerFilteringSelect(self):
        subset = self.g.vs.select(2, 3, 4, 2)
        self.assertEqual(len(subset), 4)
        self.assertEqual(subset["test"], [2, 3, 4, 2])
        self.assertRaises(TypeError, self.g.vs.select, 2, 3, 4, 2, None)

        subset = self.g.vs[2, 3, 4, 2]
        self.assertTrue(len(subset) == 4)
        self.assertTrue(subset["test"] == [2, 3, 4, 2])

    def testStringFilteringFind(self):
        self.assertEqual(self.g.vs.find("D").index, 3)
        self.assertEqual(self.g.vs.select(2, 3, 4, 2).find("C").index, 2)
        self.assertRaises(ValueError, self.g.vs.select(2, 3, 4, 2).find, "F")
        self.assertRaises(ValueError, self.g.vs.find, "NoSuchName")

    def testIterableFilteringSelect(self):
        subset = self.g.vs.select(list(range(5, 8)))
        self.assertTrue(len(subset) == 3)
        self.assertTrue(subset["test"] == [5, 6, 7])

    def testSliceFilteringSelect(self):
        subset = self.g.vs.select(slice(5, 8))
        self.assertTrue(len(subset) == 3)
        self.assertTrue(subset["test"] == [5, 6, 7])
        subset = self.g.vs[5:16:2]
        self.assertTrue(len(subset) == 3)
        self.assertTrue(subset["test"] == [5, 7, 9])

    def testKeywordFilteringSelect(self):
        g = Graph.Barabasi(10000)
        g.vs["degree"] = g.degree()
        g.vs["parity"] = [i % 2 for i in range(g.vcount())]
        l = len(g.vs(degree_gt=30))
        self.assertTrue(l < 1000)
        self.assertTrue(len(g.vs(degree_gt=30, parity=0)) <= 500)
        del g.vs["degree"]
        self.assertTrue(len(g.vs(_degree_gt=30)) == l)

    def testIndexAndKeywordFilteringFind(self):
        self.assertRaises(ValueError, self.g.vs.find, 2, name="G")
        self.assertRaises(ValueError, self.g.vs.find, 2, test=4)
        self.assertTrue(self.g.vs.find(2, name="C") == self.g.vs[2])
        self.assertTrue(self.g.vs.find(2, test=2) == self.g.vs[2])

    def testIndexOutOfBoundsSelect(self):
        g = Graph.Full(3)
        self.assertRaises(ValueError, g.vs.select, 4)
        self.assertRaises(ValueError, g.vs.select, 4, 5)
        self.assertRaises(ValueError, g.vs.select, (4, 5))
        self.assertRaises(ValueError, g.vs.select, 2, -1)
        self.assertRaises(ValueError, g.vs.select, (2, -1))
        self.assertRaises(ValueError, g.vs.__getitem__, (0, 1000000))

    def testGraphMethodProxying(self):
        g = Graph.Barabasi(100)
        vs = g.vs(1, 3, 5, 7, 9)
        self.assertEqual(vs.degree(), g.degree(vs))
        self.assertEqual(g.degree(vs), g.degree(vs.indices))
        for v, d in zip(vs, vs.degree()):
            self.assertEqual(v.degree(), d)

    def testBug73(self):
        # This is a regression test for igraph/python-igraph#73
        g = Graph()
        g.add_vertices(3)
        g.vs[0]["name"] = 1
        g.vs[1]["name"] = "h"
        g.vs[2]["name"] = 17

        self.assertEqual(1, g.vs.find("h").index)
        self.assertEqual(1, g.vs.find(1).index)
        self.assertEqual(0, g.vs.find(name=1).index)
        self.assertEqual(2, g.vs.find(name=17).index)

    def testBug367(self):
        # This is a regression test for igraph/python-igraph#367
        g = Graph()
        g.add_vertices([1, 2, 5])
        self.assertEqual([1, 2, 5], g.vs["name"])
        self.assertEqual(2, g.vs.find(name=5).index)


def suite():
    vertex_suite = unittest.makeSuite(VertexTests)
    vs_suite = unittest.makeSuite(VertexSeqTests)
    return unittest.TestSuite([vertex_suite, vs_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
