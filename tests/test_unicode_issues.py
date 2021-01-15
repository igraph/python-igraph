import unittest
from igraph import Graph


class UnicodeTests(unittest.TestCase):
    def testBug128(self):
        y = [1, 4, 9]
        g = Graph(n=len(y), directed=True, vertex_attrs={"y": y})
        self.assertEqual(3, g.vcount())
        g.add_vertices(1)
        # Bug #128 would prevent us from reaching the next statement
        # because an exception would have been thrown here
        self.assertEqual(4, g.vcount())


def suite():
    generator_suite = unittest.makeSuite(UnicodeTests)
    return unittest.TestSuite([generator_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
