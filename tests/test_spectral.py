# vim:set ts=4 sw=4 sts=4 et:
import unittest

from igraph import Graph


class SpectralTests(unittest.TestCase):
    def assertAlmostEqualMatrix(self, mat1, mat2, eps=1e-7):
        self.assertTrue(
            all(abs(obs - exp) < eps for obs, exp in zip(sum(mat1, []), sum(mat2, [])))
        )

    def testLaplacian(self):
        g = Graph.Full(3)
        g.es["weight"] = [1, 2, 3]
        self.assertTrue(g.laplacian() == [[2, -1, -1], [-1, 2, -1], [-1, -1, 2]])
        self.assertAlmostEqualMatrix(
            g.laplacian(normalized=True),
            [[1, -0.5, -0.5], [-0.5, 1, -0.5], [-0.5, -0.5, 1]],
        )
        self.assertAlmostEqualMatrix(
            g.laplacian(normalized="symmetric"),
            [[1, -0.5, -0.5], [-0.5, 1, -0.5], [-0.5, -0.5, 1]],
        )
        self.assertAlmostEqualMatrix(
            g.laplacian(normalized="left"),
            [[1, -0.5, -0.5], [-0.5, 1, -0.5], [-0.5, -0.5, 1]],
        )
        self.assertAlmostEqualMatrix(
            g.laplacian(normalized="right"),
            [[1, -0.5, -0.5], [-0.5, 1, -0.5], [-0.5, -0.5, 1]],
        )

        mx0 = [
            [1.0, -1 / (12 ** 0.5), -2 / (15 ** 0.5)],
            [-1 / (12 ** 0.5), 1.0, -3 / (20 ** 0.5)],
            [-2 / (15 ** 0.5), -3 / (20 ** 0.5), 1.0],
        ]
        self.assertAlmostEqualMatrix(g.laplacian("weight", True), mx0)

        g = Graph.Tree(5, 2)
        g.add_vertices(1)
        self.assertTrue(
            g.laplacian()
            == [
                [2, -1, -1, 0, 0, 0],
                [-1, 3, 0, -1, -1, 0],
                [-1, 0, 1, 0, 0, 0],
                [0, -1, 0, 1, 0, 0],
                [0, -1, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0],
            ]
        )

        g = Graph.Formula("A --> B --> C --> D --> E --> A, A --> C")
        self.assertAlmostEqualMatrix(
            g.laplacian(mode="out"),
            [[2, -1, -1, 0, 0], [0, 1, -1, 0, 0], [0, 0, 1, -1, 0], [0, 0, 0, 1, -1], [-1, 0, 0, 0, 1]]
        )
        self.assertAlmostEqualMatrix(
            g.laplacian(mode="in"),
            [[1, -1, -1, 0, 0], [0, 1, -1, 0, 0], [0, 0, 2, -1, 0], [0, 0, 0, 1, -1], [-1, 0, 0, 0, 1]]
        )
        self.assertAlmostEqualMatrix(
            g.laplacian(mode="out", normalized="left"),
            [[1, -0.5, -0.5, 0, 0], [0, 1, -1, 0, 0], [0, 0, 1, -1, 0], [0, 0, 0, 1, -1], [-1, 0, 0, 0, 1]]
        )
        self.assertAlmostEqualMatrix(
            g.laplacian(mode="in", normalized="right"),
            [[1, -1, -0.5, 0, 0], [0, 1, -0.5, 0, 0], [0, 0, 1, -1, 0], [0, 0, 0, 1, -1], [-1, 0, 0, 0, 1]]
        )


def suite():
    spectral_suite = unittest.defaultTestLoader.loadTestsFromTestCase(SpectralTests)
    return unittest.TestSuite([spectral_suite])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
