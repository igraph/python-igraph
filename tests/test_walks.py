import random
import unittest

from igraph import Graph, InternalError


class RandomWalkTests(unittest.TestCase):
    def setUp(self):
        random.seed(42)

    def validate_walk(self, g, walk, start, length, mode="out"):
        self.assertEqual(len(walk), length + 1)

        prev = None
        for vertex in walk:
            if prev is not None:
                self.assertTrue(vertex in g.neighbors(prev, mode=mode))
            else:
                self.assertEqual(start, vertex)
            prev = vertex

    def validate_edge_walk(self, g, walk, start, length, mode="out"):
        self.assertEqual(len(walk), length)

        prev_vertices = None
        for edgeid in walk:
            vertices = g.es[edgeid].tuple
            if prev_vertices is not None:
                self.assertTrue(
                    vertices[0] in prev_vertices or vertices[1] in prev_vertices
                )
            else:
                self.assertTrue(start in vertices)
            prev_vertices = vertices

    def testRandomWalkUndirected(self):
        g = Graph.GRG(100, 0.2)
        for _i in range(100):
            start = random.randint(0, g.vcount() - 1)
            length = random.randint(0, 10)
            walk = g.random_walk(start, length)
            self.validate_walk(g, walk, start, length)

    def testRandomWalkDirectedOut(self):
        g = Graph.Tree(121, 3, mode="out")
        mode = "out"
        for _i in range(100):
            start = 0
            length = random.randint(0, 4)
            walk = g.random_walk(start, length, mode)
            self.validate_walk(g, walk, start, length, mode)

    def testRandomWalkDirectedIn(self):
        g = Graph.Tree(121, 3, mode="out")
        mode = "in"
        for _i in range(100):
            start = random.randint(40, g.vcount() - 1)
            length = random.randint(0, 4)
            walk = g.random_walk(start, length, mode)
            self.validate_walk(g, walk, start, length, mode)

    def testRandomWalkDirectedAll(self):
        g = Graph.Tree(121, 3, mode="out")
        mode = "all"
        for _i in range(100):
            start = random.randint(0, g.vcount() - 1)
            length = random.randint(0, 10)
            walk = g.random_walk(start, length, mode)
            self.validate_walk(g, walk, start, length, mode)

    def testRandomWalkStuck(self):
        g = Graph.Ring(10, circular=False, directed=True)
        walk = g.random_walk(5, 20)
        self.assertEqual([5, 6, 7, 8, 9], walk)
        self.assertRaises(InternalError, g.random_walk, 5, 20, stuck="error")

    def testRandomWalkUndirectedVertices(self):
        g = Graph.GRG(100, 0.2)
        for _i in range(10):
            start = random.randint(0, g.vcount() - 1)
            length = random.randint(0, 10)
            walk = g.random_walk(start, length, return_type="vertices")
            self.validate_walk(g, walk, start, length)

    def testRandomWalkUndirectedEdges(self):
        g = Graph.GRG(100, 0.2)
        for _i in range(10):
            start = random.randint(0, g.vcount() - 1)
            length = random.randint(0, 10)
            walk = g.random_walk(start, length, return_type="edges")
            self.validate_edge_walk(g, walk, start, length)

    def testRandomWalkUndirectedBoth(self):
        g = Graph.GRG(100, 0.2)
        for _i in range(10):
            start = random.randint(0, g.vcount() - 1)
            length = random.randint(0, 10)
            walk_dic = g.random_walk(start, length, return_type="both")
            self.assertTrue("vertices" in walk_dic)
            self.assertTrue("edges" in walk_dic)
            self.validate_edge_walk(g, walk_dic["edges"], start, length)
            self.validate_walk(g, walk_dic["vertices"], start, length)

    def testRandomWalkUndirectedWeighted(self):
        g = Graph.GRG(100, 0.2)
        g.es["weight"] = [1.0 for i in range(g.ecount())]
        for _i in range(100):
            start = random.randint(0, g.vcount() - 1)
            length = random.randint(0, 10)
            walk = g.random_walk(start, length, weights="weight")
            self.validate_walk(g, walk, start, length)


def suite():
    random_walk_suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        RandomWalkTests
    )
    return unittest.TestSuite([random_walk_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
