import unittest
from igraph import *


class IteratorTests(unittest.TestCase):
    def testBFS(self):
        g = Graph.Tree(10, 2)
        vs, layers, ps = g.bfs(0)
        self.assertEqual(vs, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(ps, [0, 0, 0, 1, 1, 2, 2, 3, 3, 4])

    def testBFSIter(self):
        g = Graph.Tree(10, 2)
        vs = [v.index for v in g.bfsiter(0)]
        self.assertEqual(vs, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        vs = [(v.index, d, p) for v, d, p in g.bfsiter(0, advanced=True)]
        vs = [(v, d, p.index) for v, d, p in vs if p is not None]
        self.assertEqual(
            vs,
            [
                (1, 1, 0),
                (2, 1, 0),
                (3, 2, 1),
                (4, 2, 1),
                (5, 2, 2),
                (6, 2, 2),
                (7, 3, 3),
                (8, 3, 3),
                (9, 3, 4),
            ],
        )

    def testDFS(self):
        g = Graph.Tree(10, 2)
        vs, ps = g.dfs(0)
        self.assertEqual(vs, [0, 2, 6, 5, 1, 4, 9, 3, 8, 7])
        self.assertEqual(ps, [0, 0, 2, 2, 0, 1, 4, 1, 3, 3])

    def testDFSIter(self):
        g = Graph.Tree(10, 2)
        vs = [v.index for v in g.dfsiter(0)]
        self.assertEqual(vs, [0, 1, 3, 7, 8, 4, 9, 2, 5, 6])
        vs = [(v.index, d, p) for v, d, p in g.dfsiter(0, advanced=True)]
        vs = [(v, d, p.index) for v, d, p in vs if p is not None]
        self.assertEqual(
            vs,
            [
                (1, 1, 0),
                (3, 2, 1),
                (7, 3, 3),
                (8, 3, 3),
                (4, 2, 1),
                (9, 3, 4),
                (2, 1, 0),
                (5, 2, 2),
                (6, 2, 2),
            ],
        )


def suite():
    iterator_suite = unittest.makeSuite(IteratorTests)
    return unittest.TestSuite([iterator_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
