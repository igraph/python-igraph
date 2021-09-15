# vim:ts=4 sw=4 sts=4:

import unittest

from igraph import *

from .utils import is_pypy

try:
    import numpy as np
except ImportError:
    np = None


class EdgeTests(unittest.TestCase):
    def setUp(self):
        self.g = Graph.Full(10)

    def testHash(self):
        data = {}
        n = self.g.ecount()
        for i in range(n):
            code1 = hash(self.g.es[i])
            code2 = hash(self.g.es[i])
            self.assertEqual(code1, code2)
            data[self.g.es[i]] = i

        for i in range(n):
            self.assertEqual(i, data[self.g.es[i]])

    def testRichCompare(self):
        idxs = [2, 5, 9, 13, 42]
        g2 = Graph.Full(10)
        for i in idxs:
            for j in idxs:
                self.assertEqual(i == j, self.g.es[i] == self.g.es[j])
                self.assertEqual(i != j, self.g.es[i] != self.g.es[j])
                self.assertEqual(i < j, self.g.es[i] < self.g.es[j])
                self.assertEqual(i > j, self.g.es[i] > self.g.es[j])
                self.assertEqual(i <= j, self.g.es[i] <= self.g.es[j])
                self.assertEqual(i >= j, self.g.es[i] >= self.g.es[j])
                self.assertFalse(self.g.es[i] == g2.es[j])
                self.assertFalse(self.g.es[i] != g2.es[j])
                self.assertFalse(self.g.es[i] < g2.es[j])
                self.assertFalse(self.g.es[i] > g2.es[j])
                self.assertFalse(self.g.es[i] <= g2.es[j])
                self.assertFalse(self.g.es[i] >= g2.es[j])

        self.assertFalse(self.g.es[2] == self.g.vs[2])

    def testRepr(self):
        output = repr(self.g.es[0])
        self.assertEqual(output, "igraph.Edge(%r, 0, {})" % self.g)

        self.g.es["weight"] = list(range(10, 0, -1))
        output = repr(self.g.es[3])
        self.assertEqual(output, "igraph.Edge(%r, 3, {'weight': 7})" % self.g)

    def testUpdateAttributes(self):
        e = self.g.es[0]

        e.update_attributes(a=2)
        self.assertEqual(e["a"], 2)

        e.update_attributes([("a", 3), ("b", 4)], c=5, d=6)
        self.assertEqual(e.attributes(), dict(a=3, b=4, c=5, d=6))

        e.update_attributes(dict(b=44, c=55))
        self.assertEqual(e.attributes(), dict(a=3, b=44, c=55, d=6))

    def testPhantomEdge(self):
        e = self.g.es[self.g.ecount() - 1]
        e.delete()

        # v is now a phantom edge; try to freak igraph out now :)
        self.assertRaises(ValueError, e.update_attributes, a=2)
        self.assertRaises(ValueError, e.__getitem__, "a")
        self.assertRaises(ValueError, e.__setitem__, "a", 4)
        self.assertRaises(ValueError, e.__delitem__, "a")
        self.assertRaises(ValueError, e.attributes)
        self.assertRaises(ValueError, getattr, e, "source")
        self.assertRaises(ValueError, getattr, e, "source_vertex")
        self.assertRaises(ValueError, getattr, e, "target")
        self.assertRaises(ValueError, getattr, e, "target_vertex")
        self.assertRaises(ValueError, getattr, e, "tuple")
        self.assertRaises(ValueError, getattr, e, "vertex_tuple")

    @unittest.skipIf(is_pypy, "skipped on PyPy because we do not have access to docstrings")
    def testProxyMethods(self):
        g = Graph.GRG(10, 0.5)
        e = g.es[0]

        # - delete() is ignored because it mutates the graph
        ignore = "delete"
        ignore = set(ignore.split())

        # Methods not listed here are expected to return an int or a float
        return_types = {}

        for name in Edge.__dict__:
            if name in ignore:
                continue

            func = getattr(e, name)
            docstr = func.__doc__

            if not docstr.startswith("Proxy method"):
                continue

            result = func()
            self.assertEqual(
                getattr(g, name)(e.index),
                result,
                msg=("Edge.%s proxy method misbehaved" % name),
            )

            return_type = return_types.get(name, (int, float))
            self.assertTrue(
                isinstance(result, return_type),
                msg=("Edge.%s proxy method did not return %s" % (name, return_type)),
            )


class EdgeSeqTests(unittest.TestCase):
    def assert_edges_unique_in(self, es):
        pairs = sorted(e.tuple for e in es)
        self.assertEqual(pairs, sorted(set(pairs)))

    def setUp(self):
        self.g = Graph.Full(10)
        self.g.es["test"] = list(range(45))

    def testCreation(self):
        self.assertTrue(len(EdgeSeq(self.g)) == 45)
        self.assertTrue(len(EdgeSeq(self.g, 2)) == 1)
        self.assertTrue(len(EdgeSeq(self.g, [1, 2, 3])) == 3)
        self.assertTrue(EdgeSeq(self.g, [1, 2, 3]).indices == [1, 2, 3])
        self.assertRaises(ValueError, EdgeSeq, self.g, 112)
        self.assertRaises(ValueError, EdgeSeq, self.g, [112])
        self.assertTrue(self.g.es.graph == self.g)

    def testIndexing(self):
        n = self.g.ecount()
        for i in range(n):
            self.assertEqual(i, self.g.es[i].index)
            self.assertEqual(n - i - 1, self.g.es[-i - 1].index)
        self.assertRaises(IndexError, self.g.es.__getitem__, n)
        self.assertRaises(IndexError, self.g.es.__getitem__, -n - 1)
        self.assertRaises(TypeError, self.g.es.__getitem__, 1.5)

    @unittest.skipIf(np is None, "test case depends on NumPy")
    def testNumPyIndexing(self):
        n = self.g.ecount()
        for i in range(n):
            arr = np.array([i])
            self.assertEqual(i, self.g.es[arr[0]].index)

        arr = np.array([n])
        self.assertRaises(IndexError, self.g.es.__getitem__, arr[0])

        arr = np.array([-n - 1])
        self.assertRaises(IndexError, self.g.es.__getitem__, arr[0])

        arr = np.array([1.5])
        self.assertRaises(TypeError, self.g.es.__getitem__, arr[0])

        ind = [1, 3, 5, 8, 3, 2]
        arr = np.array(ind)
        self.assertEqual(ind, [edge.index for edge in self.g.es[arr.tolist()]])
        self.assertEqual(ind, [edge.index for edge in self.g.es[list(arr)]])

    def testPartialAttributeAssignment(self):
        only_even = self.g.es.select(lambda e: (e.index % 2 == 0))

        only_even["test"] = [0] * len(only_even)
        expected = [[0, i][i % 2] for i in range(self.g.ecount())]
        self.assertTrue(self.g.es["test"] == expected)

        only_even["test2"] = list(range(23))
        expected = [[i // 2, None][i % 2] for i in range(self.g.ecount())]
        self.assertTrue(self.g.es["test2"] == expected)

    def testSequenceReusing(self):
        if "test" in self.g.edge_attributes():
            del self.g.es["test"]

        self.g.es["test"] = ["A", "B", "C"]
        self.assertTrue(self.g.es["test"] == ["A", "B", "C"] * 15)
        self.g.es["test"] = "ABC"
        self.assertTrue(self.g.es["test"] == ["ABC"] * 45)

        only_even = self.g.es.select(lambda e: (e.index % 2 == 0))
        only_even["test"] = ["D", "E"]
        expected = ["D", "ABC", "E", "ABC"] * 12
        expected = expected[0:45]
        self.assertTrue(self.g.es["test"] == expected)
        del self.g.es["test"]
        only_even["test"] = ["D", "E"]
        expected = ["D", None, "E", None] * 12
        expected = expected[0:45]
        self.assertTrue(self.g.es["test"] == expected)

    def testAllSequence(self):
        self.assertTrue(len(self.g.es) == 45)
        self.assertTrue(self.g.es["test"] == list(range(45)))

    def testEmptySequence(self):
        empty_es = self.g.es.select(None)
        self.assertTrue(len(empty_es) == 0)
        self.assertRaises(IndexError, empty_es.__getitem__, 0)
        self.assertRaises(KeyError, empty_es.__getitem__, "nonexistent")
        self.assertTrue(empty_es["test"] == [])
        empty_es = self.g.es[[]]
        self.assertTrue(len(empty_es) == 0)
        empty_es = self.g.es[()]
        self.assertTrue(len(empty_es) == 0)

    def testCallableFilteringFind(self):
        edge = self.g.es.find(lambda e: (e.index % 2 == 1))
        self.assertTrue(edge.index == 1)
        self.assertRaises(IndexError, self.g.es.find, lambda e: (e.index % 2 == 3))

    def testCallableFilteringSelect(self):
        only_even = self.g.es.select(lambda e: (e.index % 2 == 0))
        self.assertTrue(len(only_even) == 23)
        self.assertRaises(KeyError, only_even.__getitem__, "nonexistent")
        self.assertTrue(only_even["test"] == [i * 2 for i in range(23)])

    def testChainedCallableFilteringSelect(self):
        only_div_six = self.g.es.select(
            lambda e: (e.index % 2 == 0), lambda e: (e.index % 3 == 0)
        )
        self.assertTrue(len(only_div_six) == 8)
        self.assertTrue(only_div_six["test"] == [0, 6, 12, 18, 24, 30, 36, 42])

        only_div_six = self.g.es.select(lambda e: (e.index % 2 == 0)).select(
            lambda e: (e.index % 3 == 0)
        )
        self.assertTrue(len(only_div_six) == 8)
        self.assertTrue(only_div_six["test"] == [0, 6, 12, 18, 24, 30, 36, 42])

    def testIntegerFilteringFind(self):
        self.assertEqual(self.g.es.find(3).index, 3)
        self.assertEqual(self.g.es.select(2, 3, 4, 2).find(3).index, 2)
        self.assertRaises(IndexError, self.g.es.find, 178)

    def testIntegerFilteringSelect(self):
        subset = self.g.es.select(2, 3, 4, 2)
        self.assertTrue(len(subset) == 4)
        self.assertTrue(subset["test"] == [2, 3, 4, 2])
        self.assertRaises(TypeError, self.g.es.select, 2, 3, 4, 2, None)

        subset = self.g.es[2, 3, 4, 2]
        self.assertTrue(len(subset) == 4)
        self.assertTrue(subset["test"] == [2, 3, 4, 2])

    def testIterableFilteringSelect(self):
        subset = self.g.es.select(list(range(5, 8)))
        self.assertTrue(len(subset) == 3)
        self.assertTrue(subset["test"] == [5, 6, 7])

    def testSliceFilteringSelect(self):
        subset = self.g.es.select(slice(5, 8))
        self.assertTrue(len(subset) == 3)
        self.assertTrue(subset["test"] == [5, 6, 7])
        subset = self.g.es[40:56:2]
        self.assertTrue(len(subset) == 3)
        self.assertTrue(subset["test"] == [40, 42, 44])

    def testKeywordFilteringSelect(self):
        g = Graph.Barabasi(1000, 2)
        g.es["betweenness"] = g.edge_betweenness()
        g.es["parity"] = [i % 2 for i in range(g.ecount())]
        self.assertTrue(len(g.es(betweenness_gt=10)) < 2000)
        self.assertTrue(len(g.es(betweenness_gt=10, parity=0)) < 2000)

    def testSourceTargetFiltering(self):
        g = Graph.Barabasi(1000, 2, directed=True)
        es1 = set(e.source for e in g.es.select(_target_in=[2, 4]))
        es2 = set(v1 for v1, v2 in g.get_edgelist() if v2 in [2, 4])
        self.assertTrue(es1 == es2)

    def testWithinFiltering(self):
        g = Graph.Lattice([10, 10])
        vs = [0, 1, 2, 10, 11, 12, 20, 21, 22]
        vs2 = (0, 1, 10, 11)

        es1 = g.es.select(_within=vs)
        es2 = g.es.select(_within=VertexSeq(g, vs))

        for es in [es1, es2]:
            self.assertTrue(len(es) == 12)
            self.assertTrue(all(e.source in vs and e.target in vs for e in es))
            self.assert_edges_unique_in(es)

            es_filtered = es.select(_within=vs2)
            self.assertTrue(len(es_filtered) == 4)
            self.assertTrue(
                all(e.source in vs2 and e.target in vs2 for e in es_filtered)
            )
            self.assert_edges_unique_in(es_filtered)

    def testBetweenFiltering(self):
        g = Graph.Lattice([10, 10])
        vs1, vs2 = [10, 11, 12], [20, 21, 22]

        es1 = g.es.select(_between=(vs1, vs2))
        es2 = g.es.select(_between=(VertexSeq(g, vs1), VertexSeq(g, vs2)))

        for es in [es1, es2]:
            self.assertTrue(len(es) == 3)
            self.assertTrue(
                all(
                    (e.source in vs1 and e.target in vs2)
                    or (e.target in vs1 and e.source in vs2)
                    for e in es
                )
            )
            self.assert_edges_unique_in(es)

    def testIncidentFiltering(self):
        g = Graph.Lattice([10, 10], circular=False)
        vs = (0, 1, 10, 11)
        vs2 = (11, 0, 24)
        vs3 = sorted(set(vs).intersection(set(vs2)))

        es = g.es.select(_incident=vs)
        self.assertEqual(8, len(es))
        self.assertTrue(all((e.source in vs or e.target in vs) for e in es))
        self.assert_edges_unique_in(es)

        es_filtered = es.select(_incident=vs2)
        self.assertEqual(6, len(es_filtered))
        self.assertTrue(all((e.source in vs3 or e.target in vs3) for e in es_filtered))
        self.assert_edges_unique_in(es_filtered)

    def testIncidentFilteringByNames(self):
        g = Graph.Lattice([10, 10], circular=False)
        vs = (0, 1, 10, 11)
        g.vs[vs]["name"] = ["A", "B", "C", "D"]

        vs2 = (11, 0, 24)
        g.vs[24]["name"] = "X"

        vs3 = sorted(set(vs).intersection(set(vs2)))

        es = g.es.select(_incident=("A", "B", "C", "D"))
        self.assertEqual(8, len(es))
        self.assertTrue(all((e.source in vs or e.target in vs) for e in es))
        self.assert_edges_unique_in(es)

        es_filtered = es.select(_incident=("D", "A", "X"))
        self.assertEqual(6, len(es_filtered))
        self.assertTrue(all((e.source in vs3 or e.target in vs3) for e in es_filtered))
        self.assert_edges_unique_in(es_filtered)

        es_filtered = es_filtered.select(_from="A")
        self.assertEqual(2, len(es_filtered))
        self.assertTrue(all((e.source == 0 or e.target == 0) for e in es_filtered))
        self.assert_edges_unique_in(es_filtered)

    def testSourceAndTargetFilteringForUndirectedGraphs(self):
        g = Graph.Lattice([10, 10], circular=False)
        vs = (0, 1, 10, 11)
        vs2 = (11, 0, 24)
        vs3 = sorted(set(vs).intersection(set(vs2)))

        es = g.es.select(_from=vs)
        self.assertEqual(8, len(es))
        self.assertTrue(all((e.source in vs or e.target in vs) for e in es))
        self.assert_edges_unique_in(es)

        es_filtered = es.select(_to_in=vs2)
        self.assertEqual(6, len(es_filtered))
        self.assertTrue(all((e.source in vs3 or e.target in vs3) for e in es_filtered))
        self.assert_edges_unique_in(es_filtered)

        es_filtered = es_filtered.select(_from_eq=0)
        self.assertEqual(2, len(es_filtered))
        self.assertTrue(all((e.source == 0 or e.target == 0) for e in es_filtered))
        self.assert_edges_unique_in(es_filtered)

    def testIndexOutOfBoundsSelect(self):
        g = Graph.Full(3)
        self.assertRaises(ValueError, g.es.select, 4)
        self.assertRaises(ValueError, g.es.select, 4, 5)
        self.assertRaises(ValueError, g.es.select, (4, 5))
        self.assertRaises(ValueError, g.es.select, 2, -1)
        self.assertRaises(ValueError, g.es.select, (2, -1))
        self.assertRaises(ValueError, g.es.__getitem__, (0, 1000000))

    def testIndexAndKeywordFilteringFind(self):
        self.assertRaises(ValueError, self.g.es.find, 2, test=4)
        self.assertTrue(self.g.es.find(2, test=2) == self.g.es[2])

    def testGraphMethodProxying(self):
        idxs = [1, 3, 5, 7, 9]
        g = Graph.Barabasi(100)
        es = g.es(*idxs)
        ebs = g.edge_betweenness()
        self.assertEqual([ebs[i] for i in idxs], es.edge_betweenness())

        idxs = [1, 3]
        g = Graph([(0, 1), (1, 2), (2, 0), (1, 0)], directed=True)
        es = g.es(*idxs)
        mutual = g.is_mutual(es)
        self.assertEqual(mutual, es.is_mutual())
        for e, m in zip(es, mutual):
            self.assertEqual(e.is_mutual(), m)

    def testIsAll(self):
        g = Graph.Full(5)
        self.assertTrue(g.es.is_all())
        self.assertFalse(g.es.select(1, 2, 3).is_all())
        self.assertFalse(g.es.select(_within=[1, 2, 3]).is_all())


def suite():
    edge_suite = unittest.makeSuite(EdgeTests)
    es_suite = unittest.makeSuite(EdgeSeqTests)
    return unittest.TestSuite([edge_suite, es_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
