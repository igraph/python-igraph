import io
import unittest
import warnings

from igraph import *
from igraph.test.utils import temporary_file


try:
    import networkx as nx
except ImportError:
    nx = None


try:
    import graph_tool as gt
except ImportError:
    gt = None


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
        with temporary_file(pickle, "wb") as tmpfname:
            g = Graph.Read_Pickle(pickle)
            self.assertTrue(isinstance(g, Graph))
            self.assertTrue(g.vcount() == 3 and g.ecount() == 1 and not g.is_directed())
            g.write_pickle(tmpfname)

    @unittest.skipIf(nx is None, "test case depends on networkx")
    def testGraphNetworkx(self):
        # Undirected
        g = Graph.Ring(10)
        g["gattr"] = "graph_attribute"
        g.vs["vattr"] = list(range(g.vcount()))
        g.es["eattr"] = list(range(len(g.es)))

        # Go to networkx and back
        g_nx = g.to_networkx()
        g2 = Graph.from_networkx(g_nx)

        self.assertFalse(g2.is_directed())
        self.assertTrue(g2.is_simple())
        self.assertEqual(g.vcount(), g2.vcount())
        self.assertEqual(sorted(g.get_edgelist()), sorted(g2.get_edgelist()))

        # Test attributes
        self.assertEqual(g.attributes(), g2.attributes())
        self.assertEqual(sorted(["vattr", "_nx_name"]), sorted(g2.vertex_attributes()))
        for i, vertex in enumerate(g.vs):
            vertex2 = g2.vs[i]
            for an in vertex.attribute_names():
                if an == "vattr":
                    continue
                self.assertEqual(vertex.attributes()[an], vertex2.attributes()[an])
        self.assertEqual(g.edge_attributes(), g2.edge_attributes())
        for edge in g.es:
            eid = g2.get_eid(edge.source, edge.target)
            edge2 = g2.es[eid]
            for an in edge.attribute_names():
                self.assertEqual(edge.attributes()[an], edge2.attributes()[an])

        # Directed
        g = Graph.Ring(10, directed=True)

        # Go to networkx and back
        g_nx = g.to_networkx()
        g2 = Graph.from_networkx(g_nx)

        self.assertTrue(g2.is_directed())
        self.assertTrue(g2.is_simple())
        self.assertEqual(g.vcount(), g2.vcount())
        self.assertEqual(sorted(g.get_edgelist()), sorted(g2.get_edgelist()))

    @unittest.skipIf(nx is None, "test case depends on networkx")
    def testMultigraphNetworkx(self):
        # Undirected
        g = Graph.Ring(10)
        g.add_edge(0, 1)
        g["gattr"] = "graph_attribute"
        g.vs["vattr"] = list(range(g.vcount()))
        g.es["eattr"] = list(range(len(g.es)))

        # Go to networkx and back
        g_nx = g.to_networkx()
        g2 = Graph.from_networkx(g_nx)

        self.assertFalse(g2.is_directed())
        self.assertFalse(g2.is_simple())
        self.assertEqual(g.vcount(), g2.vcount())
        self.assertEqual(sorted(g.get_edgelist()), sorted(g2.get_edgelist()))

        # Test attributes
        self.assertEqual(g.attributes(), g2.attributes())
        self.assertEqual(sorted(["vattr", "_nx_name"]), sorted(g2.vertex_attributes()))
        self.assertEqual(g.edge_attributes(), g2.edge_attributes())
        # Testing parallel edges is a bit more tricky
        edge2_found = set()
        for edge in g.es:
            # Go through all parallel edges between these two vertices
            for edge2 in g2.es:
                if edge2 in edge2_found:
                    continue
                if edge.source != edge2.source:
                    continue
                if edge.target != edge2.target:
                    continue
                # Check all attributes between these two
                for an in edge.attribute_names():
                    if edge.attributes()[an] != edge2.attributes()[an]:
                        break
                else:
                    # Correspondence found
                    edge2_found.add(edge2)
                    break

            else:
                self.assertTrue(False)

        # Directed
        g = Graph.Ring(10, directed=True)
        g.add_edge(0, 1)

        # Go to networkx and back
        g_nx = g.to_networkx()
        g2 = Graph.from_networkx(g_nx)

        self.assertTrue(g2.is_directed())
        self.assertFalse(g2.is_simple())
        self.assertEqual(g.vcount(), g2.vcount())
        self.assertEqual(sorted(g.get_edgelist()), sorted(g2.get_edgelist()))

    @unittest.skipIf(gt is None, "test case depends on graph-tool")
    def testGraphGraphTool(self):
        # Undirected
        g = Graph.Ring(10)
        g["gattr"] = "graph_attribute"
        g.vs["vattr"] = list(range(g.vcount()))
        g.es["eattr"] = list(range(len(g.es)))

        # Go to graph-tool and back
        g_gt = g.to_graph_tool(
            graph_attributes={"gattr": "object"},
            vertex_attributes={"vattr": "int"},
            edge_attributes={"eattr": "int"},
        )
        g2 = Graph.from_graph_tool(g_gt)

        self.assertFalse(g2.is_directed())
        self.assertTrue(g2.is_simple())
        self.assertEqual(g.vcount(), g2.vcount())
        self.assertEqual(sorted(g.get_edgelist()), sorted(g2.get_edgelist()))

        # Test attributes
        self.assertEqual(g.attributes(), g2.attributes())
        self.assertEqual(g.vertex_attributes(), g2.vertex_attributes())
        for i, vertex in enumerate(g.vs):
            vertex2 = g2.vs[i]
            for an in vertex.attribute_names():
                self.assertEqual(vertex.attributes()[an], vertex2.attributes()[an])
        self.assertEqual(g.edge_attributes(), g2.edge_attributes())
        for edge in g.es:
            eid = g2.get_eid(edge.source, edge.target)
            edge2 = g2.es[eid]
            for an in edge.attribute_names():
                self.assertEqual(edge.attributes()[an], edge2.attributes()[an])

        # Directed
        g = Graph.Ring(10, directed=True)

        # Go to graph-tool and back
        g_gt = g.to_graph_tool()

        g2 = Graph.from_graph_tool(g_gt)

        self.assertTrue(g2.is_directed())
        self.assertTrue(g2.is_simple())
        self.assertEqual(g.vcount(), g2.vcount())
        self.assertEqual(sorted(g.get_edgelist()), sorted(g2.get_edgelist()))

    @unittest.skipIf(gt is None, "test case depends on graph-tool")
    def testMultigraphGraphTool(self):
        # Undirected
        g = Graph.Ring(10)
        g.add_edge(0, 1)
        g["gattr"] = "graph_attribute"
        g.vs["vattr"] = list(range(g.vcount()))
        g.es["eattr"] = list(range(len(g.es)))

        # Go to graph-tool and back
        g_gt = g.to_graph_tool(
            graph_attributes={"gattr": "object"},
            vertex_attributes={"vattr": "int"},
            edge_attributes={"eattr": "int"},
        )
        g2 = Graph.from_graph_tool(g_gt)

        self.assertFalse(g2.is_directed())
        self.assertFalse(g2.is_simple())
        self.assertEqual(g.vcount(), g2.vcount())
        self.assertEqual(sorted(g.get_edgelist()), sorted(g2.get_edgelist()))

        # Test attributes
        self.assertEqual(g.attributes(), g2.attributes())
        self.assertEqual(g.vertex_attributes(), g2.vertex_attributes())
        for i, vertex in enumerate(g.vs):
            vertex2 = g2.vs[i]
            for an in vertex.attribute_names():
                self.assertEqual(vertex.attributes()[an], vertex2.attributes()[an])
        self.assertEqual(g.edge_attributes(), g2.edge_attributes())
        # Testing parallel edges is a bit more tricky
        edge2_found = set()
        for edge in g.es:
            # Go through all parallel edges between these two vertices
            for edge2 in g2.es:
                if edge2 in edge2_found:
                    continue
                if edge.source != edge2.source:
                    continue
                if edge.target != edge2.target:
                    continue
                # Check all attributes between these two
                for an in edge.attribute_names():
                    if edge.attributes()[an] != edge2.attributes()[an]:
                        break
                else:
                    # Correspondence found
                    edge2_found.add(edge2)
                    break

            else:
                self.assertTrue(False)

        # Directed
        g = Graph.Ring(10, directed=True)
        g.add_edge(0, 1)

        # Go to graph-tool and back
        g_gt = g.to_graph_tool()
        g2 = Graph.from_graph_tool(g_gt)

        self.assertTrue(g2.is_directed())
        self.assertFalse(g2.is_simple())
        self.assertEqual(g.vcount(), g2.vcount())
        self.assertEqual(sorted(g.get_edgelist()), sorted(g2.get_edgelist()))


def suite():
    foreign_suite = unittest.makeSuite(ForeignTests)
    return unittest.TestSuite([foreign_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
