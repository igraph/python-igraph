import io
import unittest
import warnings

from igraph import *

from .utils import temporary_file, skipIf

try:
    import pandas as pd
except ImportError:
    pd = None


class ForeignTests(unittest.TestCase):
    def testDIMACS(self):
        with temporary_file(
            """\
        c
        c        This is a simple example file to demonstrate the
        c     DIMACS input file format for minimum-cost flow problems.
        c
        c problem line :
        p max 4 5
        c
        c node descriptor lines :
        n 1 s
        n 4 t
        c
        c arc descriptor lines :
        a 1 2 4
        a 1 3 2
        a 2 3 2
        a 2 4 3
        a 3 4 5
        """
        ) as tmpfname:
            graph = Graph.Read_DIMACS(tmpfname, False)
            self.assertTrue(isinstance(graph, Graph))
            self.assertTrue(graph.vcount() == 4 and graph.ecount() == 5)
            self.assertTrue(graph["source"] == 0 and graph["target"] == 3)
            self.assertTrue(graph.es["capacity"] == [4, 2, 2, 3, 5])
            graph.write_dimacs(tmpfname)

    def testDL(self):
        with temporary_file(
            """\
        dl n=5
        format = fullmatrix
        labels embedded
        data:
        larry david lin pat russ
        Larry 0 1 1 1 0
        david 1 0 0 0 1
        Lin 1 0 0 1 0
        Pat 1 0 1 0 1
        russ 0 1 0 1 0
        """
        ) as tmpfname:
            g = Graph.Read_DL(tmpfname)
            self.assertTrue(isinstance(g, Graph))
            self.assertTrue(g.vcount() == 5 and g.ecount() == 12)
            self.assertTrue(g.is_directed())
            self.assertTrue(
                sorted(g.get_edgelist())
                == [
                    (0, 1),
                    (0, 2),
                    (0, 3),
                    (1, 0),
                    (1, 4),
                    (2, 0),
                    (2, 3),
                    (3, 0),
                    (3, 2),
                    (3, 4),
                    (4, 1),
                    (4, 3),
                ]
            )

        with temporary_file(
            """\
        dl n=5
        format = fullmatrix
        labels:
        barry,david
        lin,pat
        russ
        data:
        0 1 1 1 0
        1 0 0 0 1
        1 0 0 1 0
        1 0 1 0 1
        0 1 0 1 0
        """
        ) as tmpfname:
            g = Graph.Read_DL(tmpfname)
            self.assertTrue(isinstance(g, Graph))
            self.assertTrue(g.vcount() == 5 and g.ecount() == 12)
            self.assertTrue(g.is_directed())
            self.assertTrue(
                sorted(g.get_edgelist())
                == [
                    (0, 1),
                    (0, 2),
                    (0, 3),
                    (1, 0),
                    (1, 4),
                    (2, 0),
                    (2, 3),
                    (3, 0),
                    (3, 2),
                    (3, 4),
                    (4, 1),
                    (4, 3),
                ]
            )

        with temporary_file(
            """\
        DL n=5
        format = edgelist1
        labels:
        george, sally, jim, billy, jane
        labels embedded:
        data:
        george sally 2
        george jim 3
        sally jim 4
        billy george 5
        jane jim 6
        """
        ) as tmpfname:
            g = Graph.Read_DL(tmpfname, False)
            self.assertTrue(isinstance(g, Graph))
            self.assertTrue(g.vcount() == 5 and g.ecount() == 5)
            self.assertTrue(not g.is_directed())
            self.assertTrue(
                sorted(g.get_edgelist()) == [(0, 1), (0, 2), (0, 3), (1, 2), (2, 4)]
            )

    def _testNCOLOrLGL(self, func, fname, can_be_reopened=True):
        g = func(fname, names=False, weights=False, directed=False)
        self.assertTrue(isinstance(g, Graph))
        self.assertTrue(g.vcount() == 4 and g.ecount() == 5)
        self.assertTrue(not g.is_directed())
        self.assertTrue(
            sorted(g.get_edgelist()) == [(0, 1), (0, 2), (1, 1), (1, 3), (2, 3)]
        )
        self.assertTrue(
            "name" not in g.vertex_attributes() and "weight" not in g.edge_attributes()
        )
        if not can_be_reopened:
            return

        g = func(fname, names=False, directed=False)
        self.assertTrue(
            "name" not in g.vertex_attributes() and "weight" in g.edge_attributes()
        )
        self.assertTrue(g.es["weight"] == [1, 2, 0, 3, 0])

        g = func(fname, directed=False)
        self.assertTrue(
            "name" in g.vertex_attributes() and "weight" in g.edge_attributes()
        )
        self.assertTrue(g.vs["name"] == ["eggs", "spam", "ham", "bacon"])
        self.assertTrue(g.es["weight"] == [1, 2, 0, 3, 0])

    def testNCOL(self):
        with temporary_file(
            """\
        eggs spam 1
        ham eggs 2
        ham bacon
        bacon spam 3
        spam spam"""
        ) as tmpfname:
            self._testNCOLOrLGL(func=Graph.Read_Ncol, fname=tmpfname)

        with temporary_file(
            """\
        eggs spam
        ham eggs
        ham bacon
        bacon spam
        spam spam"""
        ) as tmpfname:
            g = Graph.Read_Ncol(tmpfname)
            self.assertTrue(
                "name" in g.vertex_attributes() and "weight" not in g.edge_attributes()
            )

    def testLGL(self):
        with temporary_file(
            """\
        # eggs
        spam 1
        # ham
        eggs 2
        bacon
        # bacon
        spam 3
        # spam
        spam"""
        ) as tmpfname:
            self._testNCOLOrLGL(func=Graph.Read_Lgl, fname=tmpfname)

        with temporary_file(
            """\
        # eggs
        spam
        # ham
        eggs
        bacon
        # bacon
        spam
        # spam
        spam"""
        ) as tmpfname:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                g = Graph.Read_Lgl(tmpfname)
            self.assertTrue(
                "name" in g.vertex_attributes() and "weight" not in g.edge_attributes()
            )

        # This is not an LGL file; we are testing error handling here
        with temporary_file(
            """\
        1 2
        1 3
        """
        ) as tmpfname:
            with self.assertRaises(InternalError):
                Graph.Read_Lgl(tmpfname)

    def testLGLWithIOModule(self):
        with temporary_file(
            """\
        # eggs
        spam 1
        # ham
        eggs 2
        bacon
        # bacon
        spam 3
        # spam
        spam"""
        ) as tmpfname:
            with io.open(tmpfname, "r") as fp:
                self._testNCOLOrLGL(
                    func=Graph.Read_Lgl, fname=fp, can_be_reopened=False
                )

    def testAdjacency(self):
        with temporary_file(
            """\
        # Test comment line
        0 1 1 0 0 0
        1 0 1 0 0 0
        1 1 0 0 0 0
        0 0 0 0 2 2
        0 0 0 2 0 2
        0 0 0 2 2 0
        """
        ) as tmpfname:
            g = Graph.Read_Adjacency(tmpfname)
            self.assertTrue(isinstance(g, Graph))
            self.assertTrue(
                g.vcount() == 6
                and g.ecount() == 18
                and g.is_directed()
                and "weight" not in g.edge_attributes()
            )
            g = Graph.Read_Adjacency(tmpfname, attribute="weight")
            self.assertTrue(isinstance(g, Graph))
            self.assertTrue(
                g.vcount() == 6
                and g.ecount() == 12
                and g.is_directed()
                and g.es["weight"] == [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2]
            )

            g.write_adjacency(tmpfname)

    def testGraphML(self):
        with temporary_file(
            """\
            <?xml version="1.0" encoding="UTF-8"?>
            <graphml xmlns="http://graphml.graphdrawing.org/xmlns"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
                    http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
            <!-- Created by igraph -->
            <key id="v_name" for="node" attr.name="name" attr.type="string"/>
            <graph id="G" edgedefault="undirected">
                <node id="n0">
                <data key="v_name">a</data>
                </node>
                <node id="n1">
                <data key="v_name">b</data>
                </node>
                <node id="n2">
                <data key="v_name">c</data>
                </node>
                <node id="n3">
                <data key="v_name">d</data>
                </node>
                <node id="n4">
                <data key="v_name">e</data>
                </node>
                <node id="n5">
                <data key="v_name">f</data>
                </node>
                <edge source="n0" target="n1">
                </edge>
                <edge source="n0" target="n2">
                </edge>
                <edge source="n0" target="n3">
                </edge>
                <edge source="n1" target="n2">
                </edge>
                <edge source="n3" target="n4">
                </edge>
                <edge source="n3" target="n5">
                </edge>
                <edge source="n4" target="n5">
                </edge>
            </graph>
            </graphml>
        """
        ) as tmpfname:
            try:
                g = Graph.Read_GraphML(tmpfname)
            except NotImplementedError as e:
                self.skipTest(str(e))

            self.assertTrue(isinstance(g, Graph))
            self.assertEqual(g.vcount(), 6)
            self.assertEqual(g.ecount(), 7)
            self.assertFalse(g.is_directed())
            self.assertTrue("name" in g.vertex_attributes())

            g.write_graphml(tmpfname)

    def testPickle(self):
        pickle = [
            128,
            2,
            99,
            105,
            103,
            114,
            97,
            112,
            104,
            10,
            71,
            114,
            97,
            112,
            104,
            10,
            113,
            1,
            40,
            75,
            3,
            93,
            113,
            2,
            75,
            1,
            75,
            2,
            134,
            113,
            3,
            97,
            137,
            125,
            125,
            125,
            116,
            82,
            113,
            4,
            125,
            98,
            46,
        ]
        if sys.version_info > (3, 0):
            pickle = bytes(pickle)
        else:
            pickle = "".join(map(chr, pickle))
        with temporary_file(pickle, "wb", binary=True) as tmpfname:
            g = Graph.Read_Pickle(pickle)
            self.assertTrue(isinstance(g, Graph))
            self.assertTrue(g.vcount() == 3 and g.ecount() == 1 and not g.is_directed())
            g.write_pickle(tmpfname)

    @skipIf(pd is None, "test case depends on Pandas")
    def testVertexDataFrames(self):
        g = Graph([(0, 1), (0, 2), (0, 3), (1, 2), (2, 4)])

        # No vertex names, no attributes
        df = g.get_vertex_dataframe()
        self.assertEqual(df.shape, (5, 0))
        self.assertEqual(list(df.index), [0, 1, 2, 3, 4])

        # Vertex names, no attributes
        g.vs["name"] = ["eggs", "spam", "ham", "bacon", "yello"]
        df = g.get_vertex_dataframe()
        self.assertEqual(df.shape, (5, 1))
        self.assertEqual(list(df.index), [0, 1, 2, 3, 4])
        self.assertEqual(list(df["name"]), g.vs["name"])
        self.assertEqual(list(df.columns), ["name"])

        # Vertex names and attributes (common case)
        g.vs["weight"] = [0, 5, 1, 4, 42]
        df = g.get_vertex_dataframe()
        self.assertEqual(df.shape, (5, 2))
        self.assertEqual(list(df.index), [0, 1, 2, 3, 4])
        self.assertEqual(list(df["name"]), g.vs["name"])
        self.assertEqual(set(df.columns), set(["name", "weight"]))
        self.assertEqual(list(df["weight"]), g.vs["weight"])

        # No vertex names, with attributes (common case)
        g = Graph([(0, 1), (0, 2), (0, 3), (1, 2), (2, 4)])
        g.vs["weight"] = [0, 5, 1, 4, 42]
        df = g.get_vertex_dataframe()
        self.assertEqual(df.shape, (5, 1))
        self.assertEqual(list(df.index), [0, 1, 2, 3, 4])
        self.assertEqual(list(df.columns), ["weight"])
        self.assertEqual(list(df["weight"]), g.vs["weight"])

    @skipIf(pd is None, "test case depends on Pandas")
    def testEdgeDataFrames(self):
        g = Graph([(0, 1), (0, 2), (0, 3), (1, 2), (2, 4)])

        # No edge names, no attributes
        df = g.get_edge_dataframe()
        self.assertEqual(df.shape, (5, 2))
        self.assertEqual(list(df.index), [0, 1, 2, 3, 4])
        self.assertEqual(list(df.columns), ["source", "target"])

        # Edge names, no attributes
        g.es["name"] = ["my", "list", "of", "five", "edges"]
        df = g.get_edge_dataframe()
        self.assertEqual(df.shape, (5, 3))
        self.assertEqual(list(df.index), [0, 1, 2, 3, 4])
        self.assertEqual(list(df["name"]), g.es["name"])
        self.assertEqual(set(df.columns), set(["source", "target", "name"]))

        # No edge names, with attributes
        g = Graph([(0, 1), (0, 2), (0, 3), (1, 2), (2, 4)])
        g.es["weight"] = [6, -0.4, 0, 1, 3]
        df = g.get_edge_dataframe()
        self.assertEqual(df.shape, (5, 3))
        self.assertEqual(list(df.index), [0, 1, 2, 3, 4])
        self.assertEqual(set(df.columns), set(["source", "target", "weight"]))
        self.assertEqual(list(df["weight"]), g.es["weight"])

        # Edge names, with weird attributes
        g.es["name"] = ["my", "list", "of", "five", "edges"]
        g.es["weight"] = [6, -0.4, 0, 1, 3]
        g.es["source"] = ["this", "is", "a", "little", "tricky"]
        df = g.get_edge_dataframe()
        self.assertEqual(df.shape, (5, 5))
        self.assertEqual(list(df.index), [0, 1, 2, 3, 4])
        self.assertEqual(
            set(df.columns), set(["source", "target", "name", "source", "weight"])
        )
        self.assertEqual(list(df["name"]), g.es["name"])
        self.assertEqual(list(df["weight"]), g.es["weight"])

        i = 2 + list(df.columns[2:]).index("source")
        self.assertEqual(list(df.iloc[:, i]), g.es["source"])


def suite():
    foreign_suite = unittest.makeSuite(ForeignTests)
    return unittest.TestSuite([foreign_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
