import gc
import sys
import unittest
import warnings

from contextlib import contextmanager
from functools import partial

from igraph import (
    ALL,
    Edge,
    EdgeSeq,
    Graph,
    IN,
    InternalError,
    is_degree_sequence,
    is_graphical,
    is_graphical_degree_sequence,
    Matrix,
    Vertex,
    VertexSeq
)
from igraph._igraph import EdgeSeq as _EdgeSeq, VertexSeq as _VertexSeq

from .utils import is_pypy

try:
    import numpy as np
except ImportError:
    np = None


class BasicTests(unittest.TestCase):
    def testGraphCreation(self):
        g = Graph()
        self.assertTrue(isinstance(g, Graph))
        self.assertTrue(g.vcount() == 0 and g.ecount() == 0 and not g.is_directed())

        g = Graph(3, [(0, 1), (1, 2), (2, 0)])
        self.assertTrue(
            g.vcount() == 3
            and g.ecount() == 3
            and not g.is_directed()
            and g.is_simple()
        )

        g = Graph(2, [(0, 1), (1, 2), (2, 3)], True)
        self.assertTrue(
            g.vcount() == 4 and g.ecount() == 3 and g.is_directed() and g.is_simple()
        )

        g = Graph([(0, 1), (1, 2), (2, 1)])
        self.assertTrue(
            g.vcount() == 3
            and g.ecount() == 3
            and not g.is_directed()
            and not g.is_simple()
        )

        g = Graph(((0, 1), (0, 0), (1, 2)))
        self.assertTrue(
            g.vcount() == 3
            and g.ecount() == 3
            and not g.is_directed()
            and not g.is_simple()
        )

        g = Graph(8, None)
        self.assertEqual(8, g.vcount())
        self.assertEqual(0, g.ecount())
        self.assertFalse(g.is_directed())

        g = Graph(edges=None)
        self.assertEqual(0, g.vcount())
        self.assertEqual(0, g.ecount())
        self.assertFalse(g.is_directed())

        self.assertRaises(TypeError, Graph, edgelist=[(1, 2)])

    @unittest.skipIf(np is None, "test case depends on NumPy")
    def testGraphCreationWithNumPy(self):
        # NumPy array with integers
        arr = np.array([(0, 1), (1, 2), (2, 3)])
        g = Graph(arr, directed=True)
        self.assertTrue(
            g.vcount() == 4 and g.ecount() == 3 and g.is_directed() and g.is_simple()
        )

        # Sliced NumPy array -- the sliced array is non-contiguous but we
        # automatically make it so
        arr = np.array([(0, 1), (10, 11), (1, 2), (11, 12), (2, 3), (12, 13)])
        g = Graph(arr[::2, :], directed=True)
        self.assertTrue(
            g.vcount() == 4 and g.ecount() == 3 and g.is_directed() and g.is_simple()
        )

        # 1D NumPy array -- should raise a TypeError because we need a 2D array
        arr = np.array([0, 1, 1, 2, 2, 3])
        self.assertRaises(TypeError, Graph, arr)

        # 3D NumPy array -- should raise a TypeError because we need a 2D array
        arr = np.array([([0, 1], [10, 11]), ([1, 2], [11, 12]), ([2, 3], [12, 13])])
        self.assertRaises(TypeError, Graph, arr)

        # NumPy array with strings -- should be a casting error
        arr = np.array([("a", "b"), ("c", "d"), ("e", "f")])
        self.assertRaises(ValueError, Graph, arr)

    def testAddVertex(self):
        g = Graph()

        vertex = g.add_vertex()
        self.assertTrue(g.vcount() == 1 and g.ecount() == 0)
        self.assertEqual(0, vertex.index)
        self.assertFalse("name" in g.vertex_attributes())

        vertex = g.add_vertex("foo")
        self.assertTrue(g.vcount() == 2 and g.ecount() == 0)
        self.assertEqual(1, vertex.index)
        self.assertTrue("name" in g.vertex_attributes())
        self.assertEqual(g.vs["name"], [None, "foo"])

        vertex = g.add_vertex(3)
        self.assertTrue(g.vcount() == 3 and g.ecount() == 0)
        self.assertEqual(2, vertex.index)
        self.assertTrue("name" in g.vertex_attributes())
        self.assertEqual(g.vs["name"], [None, "foo", 3])

        vertex = g.add_vertex(name="bar")
        self.assertTrue(g.vcount() == 4 and g.ecount() == 0)
        self.assertEqual(3, vertex.index)
        self.assertTrue("name" in g.vertex_attributes())
        self.assertEqual(g.vs["name"], [None, "foo", 3, "bar"])

        vertex = g.add_vertex(name="frob", spam="cheese", ham=42)
        self.assertTrue(g.vcount() == 5 and g.ecount() == 0)
        self.assertEqual(4, vertex.index)
        self.assertEqual(sorted(g.vertex_attributes()), ["ham", "name", "spam"])
        self.assertEqual(g.vs["spam"], [None] * 4 + ["cheese"])
        self.assertEqual(g.vs["ham"], [None] * 4 + [42])

    def testAddVertices(self):
        g = Graph()
        g.add_vertices(2)
        self.assertTrue(g.vcount() == 2 and g.ecount() == 0)

        g.add_vertices("spam")
        self.assertTrue(g.vcount() == 3 and g.ecount() == 0)
        self.assertEqual(g.vs[2]["name"], "spam")

        g.add_vertices(["bacon", "eggs"])
        self.assertTrue(g.vcount() == 5 and g.ecount() == 0)
        self.assertEqual(g.vs[2:]["name"], ["spam", "bacon", "eggs"])

        g.add_vertices(2, attributes={"color": ["k", "b"]})
        self.assertEqual(g.vs[2:]["name"], ["spam", "bacon", "eggs", None, None])
        self.assertEqual(g.vs[5:]["color"], ["k", "b"])

    def testDeleteVertices(self):
        g = Graph([(0, 1), (1, 2), (2, 3), (0, 2), (3, 4), (4, 5)])
        self.assertEqual(6, g.vcount())
        self.assertEqual(6, g.ecount())

        # Delete a single vertex
        g.delete_vertices(4)
        self.assertEqual(5, g.vcount())
        self.assertEqual(4, g.ecount())

        # Delete multiple vertices
        g.delete_vertices([1, 3])
        self.assertEqual(3, g.vcount())
        self.assertEqual(1, g.ecount())

        # Delete a vertex sequence
        g.delete_vertices(g.vs[:2])
        self.assertEqual(1, g.vcount())
        self.assertEqual(0, g.ecount())

        # Delete a single vertex object
        g.vs[0].delete()
        self.assertEqual(0, g.vcount())
        self.assertEqual(0, g.ecount())

        # Delete vertices by name
        g = Graph.Full(4)
        g.vs["name"] = ["spam", "bacon", "eggs", "ham"]
        self.assertEqual(4, g.vcount())
        g.delete_vertices("spam")
        self.assertEqual(3, g.vcount())
        g.delete_vertices(["bacon", "ham"])
        self.assertEqual(1, g.vcount())

        # Deleting a nonexistent vertex
        self.assertRaises(ValueError, g.delete_vertices, "no-such-vertex")
        self.assertRaises(InternalError, g.delete_vertices, 2)

        # Delete all vertices
        g.delete_vertices()
        self.assertEqual(0, g.vcount())

    def testAddEdge(self):
        g = Graph()
        g.add_vertices(["spam", "bacon", "eggs", "ham"])

        edge = g.add_edge(0, 1)
        self.assertEqual(g.vcount(), 4)
        self.assertEqual(g.get_edgelist(), [(0, 1)])
        self.assertEqual(0, edge.index)
        self.assertEqual((0, 1), edge.tuple)

        edge = g.add_edge(1, 2, foo="bar")
        self.assertEqual(g.vcount(), 4)
        self.assertEqual(g.get_edgelist(), [(0, 1), (1, 2)])
        self.assertEqual(1, edge.index)
        self.assertEqual((1, 2), edge.tuple)
        self.assertEqual("bar", edge["foo"])
        self.assertEqual([None, "bar"], g.es["foo"])

    def testAddEdges(self):
        g = Graph()
        g.add_vertices(["spam", "bacon", "eggs", "ham"])

        g.add_edges([(0, 1)])
        self.assertEqual(g.vcount(), 4)
        self.assertEqual(g.get_edgelist(), [(0, 1)])

        g.add_edges([(1, 2), (2, 3), (1, 3)])
        self.assertEqual(g.vcount(), 4)
        self.assertEqual(g.get_edgelist(), [(0, 1), (1, 2), (2, 3), (1, 3)])

        g.add_edges([("spam", "eggs"), ("spam", "ham")])
        self.assertEqual(g.vcount(), 4)
        self.assertEqual(
            g.get_edgelist(), [(0, 1), (1, 2), (2, 3), (1, 3), (0, 2), (0, 3)]
        )

        g.add_edges([(0, 0), (1, 1)], attributes={"color": ["k", "b"]})
        self.assertEqual(
            g.get_edgelist(),
            [
                (0, 1),
                (1, 2),
                (2, 3),
                (1, 3),
                (0, 2),
                (0, 3),
                (0, 0),
                (1, 1),
            ],
        )
        self.assertEqual(g.es["color"], [None, None, None, None, None, None, "k", "b"])

    def testDeleteEdges(self):
        g = Graph.Famous("petersen")
        g.vs["name"] = list("ABCDEFGHIJ")
        el = g.get_edgelist()

        self.assertEqual(15, g.ecount())

        # Deleting single edge
        g.delete_edges(14)
        el[14:] = []
        self.assertEqual(14, g.ecount())
        self.assertEqual(el, g.get_edgelist())

        # Deleting multiple edges
        g.delete_edges([2, 5, 7])
        el[7:8] = []
        el[5:6] = []
        el[2:3] = []
        self.assertEqual(11, g.ecount())
        self.assertEqual(el, g.get_edgelist())

        # Deleting edge object
        g.es[6].delete()
        el[6:7] = []
        self.assertEqual(10, g.ecount())
        self.assertEqual(el, g.get_edgelist())

        # Deleting edge sequence object
        g.es[1:4].delete()
        el[1:4] = []
        self.assertEqual(7, g.ecount())
        self.assertEqual(el, g.get_edgelist())

        # Deleting edges by IDs
        g.delete_edges([(2, 7), (5, 8)])
        el[4:5] = []
        el[1:2] = []
        self.assertEqual(5, g.ecount())
        self.assertEqual(el, g.get_edgelist())

        # Deleting edges by names
        g.delete_edges([("D", "I"), ("G", "I")])
        el[3:4] = []
        el[1:2] = []
        self.assertEqual(3, g.ecount())
        self.assertEqual(el, g.get_edgelist())

        # Deleting nonexistent edges
        self.assertRaises(ValueError, g.delete_edges, [(0, 2)])
        self.assertRaises(ValueError, g.delete_edges, [("A", "C")])
        self.assertRaises(ValueError, g.delete_edges, [(0, 15)])

        # Delete all edges
        g.delete_edges()
        self.assertEqual(0, g.ecount())

    def testClear(self):
        g = Graph.Famous("petersen")
        g["name"] = list("petersen")

        # Clearing the graph
        g.clear()

        self.assertEqual(0, g.vcount())
        self.assertEqual(0, g.ecount())
        self.assertEqual([], g.attributes())

    def testGraphGetEid(self):
        g = Graph.Famous("petersen")
        g.vs["name"] = list("ABCDEFGHIJ")
        edges_to_ids = dict((v, k) for k, v in enumerate(g.get_edgelist()))
        for (source, target), edge_id in edges_to_ids.items():
            source_name, target_name = g.vs[(source, target)]["name"]
            self.assertEqual(edge_id, g.get_eid(source, target))
            self.assertEqual(edge_id, g.get_eid(source_name, target_name))

        self.assertRaises(InternalError, g.get_eid, 0, 11)
        self.assertRaises(ValueError, g.get_eid, "A", "K")

    def testGraphGetEids(self):
        g = Graph.Famous("petersen")
        eids = g.get_eids(pairs=[(0, 1), (0, 5), (1, 6), (4, 9), (8, 6)])
        self.assertTrue(eids == [0, 2, 4, 9, 12])
        eids = g.get_eids(pairs=[(7, 9), (9, 6)])
        self.assertTrue(eids == [14, 13])
        self.assertRaises(InternalError, g.get_eids, pairs=[(0, 1), (0, 2)])
        self.assertRaises(TypeError, g.get_eids, pairs=None)

    def testAdjacency(self):
        g = Graph(4, [(0, 1), (1, 2), (2, 0), (2, 3)], directed=True)
        self.assertTrue(g.neighbors(2) == [0, 1, 3])
        self.assertTrue(g.predecessors(2) == [1])
        self.assertTrue(g.successors(2) == [0, 3])
        self.assertTrue(g.get_adjlist() == [[1], [2], [0, 3], []])
        self.assertTrue(g.get_adjlist(IN) == [[2], [0], [1], [2]])
        self.assertTrue(g.get_adjlist(ALL) == [[1, 2], [0, 2], [0, 1, 3], [2]])

    def testEdgeIncidence(self):
        g = Graph(4, [(0, 1), (1, 2), (2, 0), (2, 3)], directed=True)
        self.assertTrue(g.incident(2) == [2, 3])
        self.assertTrue(g.incident(2, IN) == [1])
        self.assertTrue(g.incident(2, ALL) == [2, 1, 3])
        self.assertTrue(g.get_inclist() == [[0], [1], [2, 3], []])
        self.assertTrue(g.get_inclist(IN) == [[2], [0], [1], [3]])
        self.assertTrue(g.get_inclist(ALL) == [[0, 2], [0, 1], [2, 1, 3], [3]])

    def testMultiplesLoops(self):
        g = Graph.Tree(7, 2)

        # has_multiple
        self.assertFalse(g.has_multiple())

        g.add_vertices(1)
        g.add_edges([(0, 1), (7, 7), (6, 6), (6, 6), (6, 6)])

        # is_loop
        self.assertTrue(
            g.is_loop()
            == [False, False, False, False, False, False, False, True, True, True, True]
        )
        self.assertTrue(g.is_loop(g.ecount() - 2))
        self.assertTrue(g.is_loop(list(range(6, 8))) == [False, True])

        # is_multiple
        self.assertTrue(
            g.is_multiple()
            == [
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                False,
                False,
                True,
                True,
            ]
        )

        # has_multiple
        self.assertTrue(g.has_multiple())

        # count_multiple
        self.assertTrue(g.count_multiple() == [2, 1, 1, 1, 1, 1, 2, 1, 3, 3, 3])
        self.assertTrue(g.count_multiple(g.ecount() - 1) == 3)
        self.assertTrue(g.count_multiple(list(range(2, 5))) == [1, 1, 1])

        # check if a mutual directed edge pair is reported as multiple
        g = Graph(2, [(0, 1), (1, 0)], directed=True)
        self.assertTrue(g.is_multiple() == [False, False])

    def testPickling(self):
        import pickle

        g = Graph([(0, 1), (1, 2)])
        g["data"] = "abcdef"
        g.vs["data"] = [3, 4, 5]
        g.es["data"] = ["A", "B"]
        g.custom_data = None
        pickled = pickle.dumps(g)

        g2 = pickle.loads(pickled)
        self.assertTrue(g["data"] == g2["data"])
        self.assertTrue(g.vs["data"] == g2.vs["data"])
        self.assertTrue(g.es["data"] == g2.es["data"])
        self.assertTrue(g.vcount() == g2.vcount())
        self.assertTrue(g.ecount() == g2.ecount())
        self.assertTrue(g.is_directed() == g2.is_directed())
        self.assertTrue(g2.custom_data == g.custom_data)

    def testHashing(self):
        g = Graph([(0, 1), (1, 2)])
        self.assertRaises(TypeError, hash, g)

    def testIteration(self):
        g = Graph()
        self.assertRaises(TypeError, iter, g)


class DatatypeTests(unittest.TestCase):
    def testMatrix(self):
        m = Matrix([[1, 2, 3], [4, 5], [6, 7, 8]])
        self.assertTrue(m.shape == (3, 3))

        # Reading data
        self.assertTrue(m.data == [[1, 2, 3], [4, 5, 0], [6, 7, 8]])
        self.assertTrue(m[1, 1] == 5)
        self.assertTrue(m[0] == [1, 2, 3])
        self.assertTrue(m[0, :] == [1, 2, 3])
        self.assertTrue(m[:, 0] == [1, 4, 6])
        self.assertTrue(m[2, 0:2] == [6, 7])
        self.assertTrue(m[:, :].data == [[1, 2, 3], [4, 5, 0], [6, 7, 8]])
        self.assertTrue(m[:, 1:3].data == [[2, 3], [5, 0], [7, 8]])

        # Writing data
        m[1, 1] = 10
        self.assertTrue(m[1, 1] == 10)
        m[1] = (6, 5, 4)
        self.assertTrue(m[1] == [6, 5, 4])
        m[1:3] = [[4, 5, 6], (7, 8, 9)]
        self.assertTrue(m[1:3].data == [[4, 5, 6], [7, 8, 9]])

        # Minimums and maximums
        self.assertTrue(m.min() == 1)
        self.assertTrue(m.max() == 9)
        self.assertTrue(m.min(0) == [1, 2, 3])
        self.assertTrue(m.max(0) == [7, 8, 9])
        self.assertTrue(m.min(1) == [1, 4, 7])
        self.assertTrue(m.max(1) == [3, 6, 9])

        # Special constructors
        m = Matrix.Fill(2, (3, 3))
        self.assertTrue(m.min() == 2 and m.max() == 2 and m.shape == (3, 3))
        m = Matrix.Zero(5, 4)
        self.assertTrue(m.min() == 0 and m.max() == 0 and m.shape == (5, 4))
        m = Matrix.Identity(3)
        self.assertTrue(m.data == [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        m = Matrix.Identity(3, 2)
        self.assertTrue(m.data == [[1, 0], [0, 1], [0, 0]])

        # Conversion to string
        m = Matrix.Identity(3)
        self.assertTrue(str(m) == "[[1, 0, 0]\n [0, 1, 0]\n [0, 0, 1]]")
        self.assertTrue(repr(m) == "Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])")


class GraphDictListTests(unittest.TestCase):
    def setUp(self):
        self.vertices = [
            {"name": "Alice", "age": 48, "gender": "F"},
            {"name": "Bob", "age": 33, "gender": "M"},
            {"name": "Cecil", "age": 45, "gender": "F"},
            {"name": "David", "age": 34, "gender": "M"},
        ]
        self.edges = [
            {"source": "Alice", "target": "Bob", "friendship": 4, "advice": 4},
            {"source": "Cecil", "target": "Bob", "friendship": 5, "advice": 5},
            {"source": "Cecil", "target": "Alice", "friendship": 5, "advice": 5},
            {"source": "David", "target": "Alice", "friendship": 2, "advice": 4},
            {"source": "David", "target": "Bob", "friendship": 1, "advice": 2},
        ]

    def testGraphFromDictList(self):
        g = Graph.DictList(self.vertices, self.edges)
        self.checkIfOK(g, "name")
        g = Graph.DictList(self.vertices, self.edges, iterative=True)
        self.checkIfOK(g, "name")

    def testGraphFromDictIterator(self):
        g = Graph.DictList(iter(self.vertices), iter(self.edges))
        self.checkIfOK(g, "name")
        g = Graph.DictList(iter(self.vertices), iter(self.edges), iterative=True)
        self.checkIfOK(g, "name")

    def testGraphFromDictIteratorNoVertices(self):
        g = Graph.DictList(None, iter(self.edges))
        self.checkIfOK(g, "name", check_vertex_attrs=False)
        g = Graph.DictList(None, iter(self.edges), iterative=True)
        self.checkIfOK(g, "name", check_vertex_attrs=False)

    def testGraphFromDictListExtraVertexName(self):
        del self.vertices[2:]  # No data for "Cecil" and "David"
        g = Graph.DictList(self.vertices, self.edges)
        self.assertTrue(g.vcount() == 4 and g.ecount() == 5 and not g.is_directed())
        self.assertTrue(g.vs["name"] == ["Alice", "Bob", "Cecil", "David"])
        self.assertTrue(g.vs["age"] == [48, 33, None, None])
        self.assertTrue(g.vs["gender"] == ["F", "M", None, None])
        self.assertTrue(g.es["friendship"] == [4, 5, 5, 2, 1])
        self.assertTrue(g.es["advice"] == [4, 5, 5, 4, 2])
        self.assertTrue(g.get_edgelist() == [(0, 1), (1, 2), (0, 2), (0, 3), (1, 3)])

    def testGraphFromDictListAlternativeName(self):
        for vdata in self.vertices:
            vdata["name_alternative"] = vdata["name"]
            del vdata["name"]
        g = Graph.DictList(
            self.vertices, self.edges, vertex_name_attr="name_alternative"
        )
        self.checkIfOK(g, "name_alternative")
        g = Graph.DictList(
            self.vertices,
            self.edges,
            vertex_name_attr="name_alternative",
            iterative=True,
        )
        self.checkIfOK(g, "name_alternative")

    def checkIfOK(self, g, name_attr, check_vertex_attrs=True):
        self.assertTrue(g.vcount() == 4 and g.ecount() == 5 and not g.is_directed())
        self.assertTrue(g.get_edgelist() == [(0, 1), (1, 2), (0, 2), (0, 3), (1, 3)])
        self.assertTrue(g.vs[name_attr] == ["Alice", "Bob", "Cecil", "David"])
        if check_vertex_attrs:
            self.assertTrue(g.vs["age"] == [48, 33, 45, 34])
            self.assertTrue(g.vs["gender"] == ["F", "M", "F", "M"])
        self.assertTrue(g.es["friendship"] == [4, 5, 5, 2, 1])
        self.assertTrue(g.es["advice"] == [4, 5, 5, 4, 2])


class GraphTupleListTests(unittest.TestCase):
    def setUp(self):
        self.edges = [
            ("Alice", "Bob", 4, 4),
            ("Cecil", "Bob", 5, 5),
            ("Cecil", "Alice", 5, 5),
            ("David", "Alice", 2, 4),
            ("David", "Bob", 1, 2),
        ]

    def testGraphFromTupleList(self):
        g = Graph.TupleList(self.edges)
        self.checkIfOK(g, "name", ())

    def testGraphFromTupleListWithEdgeAttributes(self):
        g = Graph.TupleList(self.edges, edge_attrs=("friendship", "advice"))
        self.checkIfOK(g, "name", ("friendship", "advice"))
        g = Graph.TupleList(self.edges, edge_attrs=("friendship",))
        self.checkIfOK(g, "name", ("friendship",))
        g = Graph.TupleList(self.edges, edge_attrs="friendship")
        self.checkIfOK(g, "name", ("friendship",))

    def testGraphFromTupleListWithDifferentNameAttribute(self):
        g = Graph.TupleList(self.edges, vertex_name_attr="spam")
        self.checkIfOK(g, "spam", ())

    def testGraphFromTupleListWithWeights(self):
        g = Graph.TupleList(self.edges, weights=True)
        self.checkIfOK(g, "name", ("weight",))
        g = Graph.TupleList(self.edges, weights="friendship")
        self.checkIfOK(g, "name", ("friendship",))
        g = Graph.TupleList(self.edges, weights=False)
        self.checkIfOK(g, "name", ())
        self.assertRaises(
            ValueError,
            Graph.TupleList,
            [self.edges],
            weights=True,
            edge_attrs="friendship",
        )

    def testNoneForMissingAttributes(self):
        g = Graph.TupleList(self.edges, edge_attrs=("friendship", "advice", "spam"))
        self.checkIfOK(g, "name", ("friendship", "advice", "spam"))

    def checkIfOK(self, g, name_attr, edge_attrs):
        self.assertTrue(g.vcount() == 4 and g.ecount() == 5 and not g.is_directed())
        self.assertTrue(g.get_edgelist() == [(0, 1), (1, 2), (0, 2), (0, 3), (1, 3)])
        self.assertTrue(g.attributes() == [])
        self.assertTrue(g.vertex_attributes() == [name_attr])
        self.assertTrue(g.vs[name_attr] == ["Alice", "Bob", "Cecil", "David"])
        if edge_attrs:
            self.assertTrue(sorted(g.edge_attributes()) == sorted(edge_attrs))
            self.assertTrue(g.es[edge_attrs[0]] == [4, 5, 5, 2, 1])
            if len(edge_attrs) > 1:
                self.assertTrue(g.es[edge_attrs[1]] == [4, 5, 5, 4, 2])
            if len(edge_attrs) > 2:
                self.assertTrue(g.es[edge_attrs[2]] == [None] * 5)
        else:
            self.assertTrue(g.edge_attributes() == [])


class GraphListDictTests(unittest.TestCase):
    def setUp(self):
        self.eids = {
            0: [1],
            2: [1, 0],
            3: [0, 1],
        }
        self.edges = {
            "Alice": ["Bob"],
            "Cecil": ["Bob", "Alice"],
            "David": ["Alice", "Bob"],
        }

    def testEmptyGraphListDict(self):
        g = Graph.ListDict({})
        self.assertEqual(g.vcount(), 0)

    def testGraphFromListDict(self):
        g = Graph.ListDict(self.eids)
        self.checkIfOK(g, ())

    def testGraphFromListDictWithNames(self):
        g = Graph.ListDict(self.edges)
        self.checkIfOK(g, "name")

    def checkIfOK(self, g, name_attr):
        self.assertTrue(g.vcount() == 4 and g.ecount() == 5 and not g.is_directed())
        self.assertTrue(g.get_edgelist() == [(0, 1), (1, 2), (0, 2), (0, 3), (1, 3)])
        self.assertTrue(g.attributes() == [])
        if name_attr:
            self.assertTrue(g.vertex_attributes() == [name_attr])
            self.assertTrue(g.vs[name_attr] == ["Alice", "Bob", "Cecil", "David"])
        self.assertTrue(g.edge_attributes() == [])


class GraphDictDictTests(unittest.TestCase):
    def setUp(self):
        self.eids = {
            0: {1: {}},
            2: {1: {}, 0: {}},
            3: {0: {}, 1: {}},
        }
        self.edges = {
            "Alice": {"Bob": {}},
            "Cecil": {"Bob": {}, "Alice": {}},
            "David": {"Alice": {}, "Bob": {}},
        }
        self.eids_with_props = {
            0: {1: {"weight": 5.6, "additional": 'abc'}},
            2: {1: {"weight": 3.4}, 0: {"weight": 2}},
            3: {0: {"weight": 1}, 1: {"weight": 5.6}},
        }

    def testEmptyGraphDictDict(self):
        g = Graph.DictDict({})
        self.assertEqual(g.vcount(), 0)

    def testGraphFromDictDict(self):
        g = Graph.DictDict(self.eids)
        self.checkIfOK(g, ())

    def testGraphFromDictDict(self):
        g = Graph.DictDict(self.eids_with_props)
        self.checkIfOK(g, (), edge_attrs=["additional", "weight"])

    def testGraphFromDictDictWithNames(self):
        g = Graph.DictDict(self.edges)
        self.checkIfOK(g, "name")

    def checkIfOK(self, g, name_attr, edge_attrs=None):
        self.assertTrue(g.vcount() == 4 and g.ecount() == 5 and not g.is_directed())
        self.assertTrue(g.get_edgelist() == [(0, 1), (1, 2), (0, 2), (0, 3), (1, 3)])
        self.assertTrue(g.attributes() == [])
        if name_attr:
            self.assertTrue(g.vertex_attributes() == [name_attr])
            self.assertTrue(g.vs[name_attr] == ["Alice", "Bob", "Cecil", "David"])
        if edge_attrs is None:
            self.assertEqual(g.edge_attributes(), [])
        else:
            self.assertEqual(sorted(g.edge_attributes()), sorted(edge_attrs))


class DegreeSequenceTests(unittest.TestCase):
    def testIsDegreeSequence(self):
        # Catch and suppress warnings because is_degree_sequence() is now
        # deprecated
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertTrue(is_degree_sequence([]))
            self.assertTrue(is_degree_sequence([], []))
            self.assertTrue(is_degree_sequence([0]))
            self.assertTrue(is_degree_sequence([0], [0]))
            self.assertFalse(is_degree_sequence([1]))
            self.assertTrue(is_degree_sequence([1], [1]))
            self.assertTrue(is_degree_sequence([2]))
            self.assertFalse(is_degree_sequence([2, 1, 1, 1]))
            self.assertTrue(is_degree_sequence([2, 1, 1, 1], [1, 1, 1, 2]))
            self.assertFalse(is_degree_sequence([2, 1, -2]))
            self.assertFalse(is_degree_sequence([2, 1, 1, 1], [1, 1, 1, -2]))
            self.assertTrue(is_degree_sequence([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]))
            self.assertTrue(is_degree_sequence([3, 3, 3, 3, 3, 3, 3, 3, 3, 3], None))
            self.assertFalse(is_degree_sequence([3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]))
            self.assertTrue(
                is_degree_sequence(
                    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3], [4, 3, 2, 3, 4, 4, 2, 2, 4, 2]
                )
            )

    def testIsGraphicalSequence(self):
        # Catch and suppress warnings because is_graphical_degree_sequence() is now
        # deprecated
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertTrue(is_graphical_degree_sequence([]))
            self.assertTrue(is_graphical_degree_sequence([], []))
            self.assertTrue(is_graphical_degree_sequence([0]))
            self.assertTrue(is_graphical_degree_sequence([0], [0]))
            self.assertFalse(is_graphical_degree_sequence([1]))
            self.assertFalse(is_graphical_degree_sequence([1], [1]))
            self.assertFalse(is_graphical_degree_sequence([2]))
            self.assertFalse(is_graphical_degree_sequence([2, 1, 1, 1]))
            self.assertTrue(is_graphical_degree_sequence([2, 1, 1, 1], [1, 1, 1, 2]))
            self.assertFalse(is_graphical_degree_sequence([2, 1, -2]))
            self.assertFalse(is_graphical_degree_sequence([2, 1, 1, 1], [1, 1, 1, -2]))
            self.assertTrue(
                is_graphical_degree_sequence([3, 3, 3, 3, 3, 3, 3, 3, 3, 3])
            )
            self.assertTrue(
                is_graphical_degree_sequence([3, 3, 3, 3, 3, 3, 3, 3, 3, 3], None)
            )
            self.assertFalse(
                is_graphical_degree_sequence([3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3])
            )
            self.assertTrue(
                is_graphical_degree_sequence(
                    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3], [4, 3, 2, 3, 4, 4, 2, 2, 4, 2]
                )
            )
            self.assertTrue(is_graphical_degree_sequence([3, 3, 3, 3, 4]))

    def testIsGraphicalNonSimple(self):
        # Same as testIsDegreeSequence, but using is_graphical()
        is_degree_sequence = partial(is_graphical, loops=True, multiple=True)
        self.assertTrue(is_degree_sequence([]))
        self.assertTrue(is_degree_sequence([], []))
        self.assertTrue(is_degree_sequence([0]))
        self.assertTrue(is_degree_sequence([0], [0]))
        self.assertFalse(is_degree_sequence([1]))
        self.assertTrue(is_degree_sequence([1], [1]))
        self.assertTrue(is_degree_sequence([2]))
        self.assertFalse(is_degree_sequence([2, 1, 1, 1]))
        self.assertTrue(is_degree_sequence([2, 1, 1, 1], [1, 1, 1, 2]))
        self.assertFalse(is_degree_sequence([2, 1, -2]))
        self.assertFalse(is_degree_sequence([2, 1, 1, 1], [1, 1, 1, -2]))
        self.assertTrue(is_degree_sequence([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]))
        self.assertTrue(is_degree_sequence([3, 3, 3, 3, 3, 3, 3, 3, 3, 3], None))
        self.assertFalse(is_degree_sequence([3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]))
        self.assertTrue(
            is_degree_sequence(
                [3, 3, 3, 3, 3, 3, 3, 3, 3, 3], [4, 3, 2, 3, 4, 4, 2, 2, 4, 2]
            )
        )

    def testIsGraphicalSimple(self):
        # Same as testIsGraphicalDegreeSequence, but using is_graphical()
        is_graphical_degree_sequence = partial(
            is_graphical, loops=False, multiple=False
        )
        self.assertTrue(is_graphical_degree_sequence([]))
        self.assertTrue(is_graphical_degree_sequence([], []))
        self.assertTrue(is_graphical_degree_sequence([0]))
        self.assertTrue(is_graphical_degree_sequence([0], [0]))
        self.assertFalse(is_graphical_degree_sequence([1]))
        self.assertFalse(is_graphical_degree_sequence([1], [1]))
        self.assertFalse(is_graphical_degree_sequence([2]))
        self.assertFalse(is_graphical_degree_sequence([2, 1, 1, 1]))
        self.assertTrue(is_graphical_degree_sequence([2, 1, 1, 1], [1, 1, 1, 2]))
        self.assertFalse(is_graphical_degree_sequence([2, 1, -2]))
        self.assertFalse(is_graphical_degree_sequence([2, 1, 1, 1], [1, 1, 1, -2]))
        self.assertTrue(is_graphical_degree_sequence([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]))
        self.assertTrue(
            is_graphical_degree_sequence([3, 3, 3, 3, 3, 3, 3, 3, 3, 3], None)
        )
        self.assertFalse(
            is_graphical_degree_sequence([3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3])
        )
        self.assertTrue(
            is_graphical_degree_sequence(
                [3, 3, 3, 3, 3, 3, 3, 3, 3, 3], [4, 3, 2, 3, 4, 4, 2, 2, 4, 2]
            )
        )
        self.assertTrue(is_graphical_degree_sequence([3, 3, 3, 3, 4]))


class InheritedGraph(Graph):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.init_called = True

    def __new__(cls, *args, **kwds):
        result = Graph.__new__(cls)
        result.new_called = True
        return result

    @classmethod
    def Adjacency(cls, *args, **kwds):
        result = super().Adjacency(*args, **kwds)
        result.adjacency_called = True
        return result


class InheritedGraphWithEarlyMethodCallInInit(Graph):
    def __init__(self, *args, **kwds):
        self.call_result = self.degree()
        super().__init__(*args, **kwds)
        self.init_called = True


class InheritedGraphWithEarlyMethodCallInNew(Graph):
    def __new__(cls, *args, **kwds):
        instance = super().__new__(cls, *args, **kwds)
        instance.call_result = instance.degree()
        return instance


class InheritedGraphThatReturnsNonGraphFromNew(Graph):
    def __new__(cls, *args, **kwds):
        super().__new__(cls, *args, **kwds)
        return 42


class InheritanceTests(unittest.TestCase):
    def testInitCalledProperly(self):
        g = InheritedGraph()
        self.assertTrue(isinstance(g, InheritedGraph))
        self.assertTrue(getattr(g, "init_called", False))

    def testNewCalledProperly(self):
        g = InheritedGraph()
        self.assertTrue(isinstance(g, InheritedGraph))
        self.assertTrue(getattr(g, "new_called", False))

    def testInitCalledProperlyWithClassMethod(self):
        g = InheritedGraph.Tree(3, 2)
        self.assertTrue(isinstance(g, InheritedGraph))
        self.assertTrue(getattr(g, "init_called", False))

    def testNewCalledProperlyWithClassMethod(self):
        g = InheritedGraph.Tree(3, 2)
        self.assertTrue(isinstance(g, InheritedGraph))
        self.assertTrue(getattr(g, "new_called", False))

    def testCallingClassMethodInSuperclass(self):
        g = InheritedGraph.Adjacency([[0, 1, 1], [1, 0, 0], [1, 0, 0]])
        self.assertTrue(isinstance(g, InheritedGraph))
        self.assertTrue(getattr(g, "adjacency_called", True))

    def testCallingInstanceMethodTooEarly(self):
        # Creating an InheritedGraphWithEarlyMethodCallInInit instance should
        # not crash the runtime
        g = InheritedGraphWithEarlyMethodCallInInit([(0, 1), (1, 2), (2, 3)])
        self.assertEqual(4, g.vcount())
        self.assertEqual([1, 2, 2, 1], g.degree())
        self.assertEqual([], g.call_result)

        # Creating an InheritedGraphWithEarlyMethodCallInNew instance should
        # not crash the runtime either
        g = InheritedGraphWithEarlyMethodCallInNew([(0, 1), (1, 2), (2, 3)])
        self.assertEqual(4, g.vcount())
        self.assertEqual([1, 2, 2, 1], g.degree())
        self.assertEqual([], g.call_result)

    def testInheritedGraphThatReturnsSomethingElseFromNew(self):
        g = InheritedGraphThatReturnsNonGraphFromNew([(0, 1)], directed=True)
        self.assertEqual(42, g)


@contextmanager
def assert_reference_not_leaked(case, *args):
    gc.collect()
    refs_before = [sys.getrefcount(obj) for obj in args]
    try:
        yield
    finally:
        gc.collect()
        refs_after = [sys.getrefcount(obj) for obj in args]
        case.assertListEqual(refs_before, refs_after)


@unittest.skipIf(is_pypy, "reference counts are not relevant for PyPy")
class ReferenceCountTests(unittest.TestCase):
    def testEdgeReferenceCounting(self):
        with assert_reference_not_leaked(self, Edge, EdgeSeq, _EdgeSeq):
            g = Graph.Tree(3, 2)
            edge = g.es[1]
            del edge, g

    def testEdgeSeqReferenceCounting(self):
        with assert_reference_not_leaked(self, Edge, EdgeSeq, _EdgeSeq):
            g = Graph.Tree(3, 2)
            es = g.es
            es2 = EdgeSeq(g)
            del es, es2, g

    def testGraphReferenceCounting(self):
        with assert_reference_not_leaked(self, Graph, InheritedGraph):
            g = Graph.Tree(3, 2)
            self.assertTrue(gc.is_tracked(g))
            del g

    def testInheritedGraphReferenceCounting(self):
        with assert_reference_not_leaked(self, Graph, InheritedGraph):
            g = InheritedGraph.Tree(3, 2)
            self.assertTrue(gc.is_tracked(g))
            del g
    
    def testVertexReferenceCounting(self):
        with assert_reference_not_leaked(self, Vertex, VertexSeq, _VertexSeq):
            g = Graph.Tree(3, 2)
            vertex = g.vs[2]
            del vertex, g
    
    def testVertexSeqReferenceCounting(self):
        with assert_reference_not_leaked(self, Vertex, VertexSeq, _VertexSeq):
            g = Graph.Tree(3, 2)
            vs = g.vs
            vs2 = VertexSeq(g)
            del vs2, vs, g


def suite():
    basic_suite = unittest.defaultTestLoader.loadTestsFromTestCase(BasicTests)
    datatype_suite = unittest.defaultTestLoader.loadTestsFromTestCase(DatatypeTests)
    graph_dict_list_suite = unittest.defaultTestLoader.loadTestsFromTestCase(GraphDictListTests)
    graph_tuple_list_suite = unittest.defaultTestLoader.loadTestsFromTestCase(GraphTupleListTests)
    graph_list_dict_suite = unittest.defaultTestLoader.loadTestsFromTestCase(GraphListDictTests)
    graph_dict_dict_suite = unittest.defaultTestLoader.loadTestsFromTestCase(GraphDictDictTests)
    degree_sequence_suite = unittest.defaultTestLoader.loadTestsFromTestCase(DegreeSequenceTests)
    inheritance_suite = unittest.defaultTestLoader.loadTestsFromTestCase(InheritanceTests)
    refcount_suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReferenceCountTests)
    return unittest.TestSuite(
        [
            basic_suite,
            datatype_suite,
            graph_dict_list_suite,
            graph_tuple_list_suite,
            graph_list_dict_suite,
            graph_dict_dict_suite,
            degree_sequence_suite,
            inheritance_suite,
            refcount_suite
        ]
    )


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
