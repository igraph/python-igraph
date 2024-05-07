import os
import unittest


from igraph import Graph, plot, VertexClustering, Layout

from ...utils import overridden_configuration

# FIXME: find a better way to do this that works for both direct call and module
# import e.g. tox
try:
    from .utils import find_image_comparison
except ImportError:
    from utils import find_image_comparison

try:
    import matplotlib as mpl

    mpl.use("agg")
    import matplotlib.pyplot as plt
except ImportError:
    mpl = None
    plt = None

image_comparison = find_image_comparison()


class GraphTestRunner(unittest.TestCase):
    def setUp(self):
        if mpl is None or plt is None:
            raise unittest.SkipTest("matplotlib not found, skipping tests")

    @property
    def layout_small_ring(self):
        coords = [
            [1.015318095035966, 0.03435580194714975],
            [0.29010409851547664, 1.0184451153265959],
            [-0.8699239050738742, 0.6328259400443561],
            [-0.8616466426732888, -0.5895891303732176],
            [0.30349699041342515, -0.9594640169691343],
        ]
        return coords

    @image_comparison(baseline_images=["graph_basic"], remove_text=True)
    def test_basic(self):
        plt.close("all")
        g = Graph.Ring(5)
        fig, ax = plt.subplots()
        plot(g, target=ax, layout=self.layout_small_ring)

    @image_comparison(baseline_images=["graph_labels"], remove_text=True)
    def test_labels(self):
        plt.close("all")
        g = Graph.Ring(5)
        fig, ax = plt.subplots(figsize=(3, 3))
        plot(
            g, target=ax, layout=self.layout_small_ring,
            vertex_label=['1', '2', '3', '4', '5'],
            vertex_label_color='white',
            vertex_label_size=16,
        )

    @image_comparison(baseline_images=["graph_layout_attribute"], remove_text=True)
    def test_layout_attribute(self):
        plt.close("all")
        g = Graph.Ring(5)
        g["layout"] = Layout([(x, x) for x in range(g.vcount())])
        fig, ax = plt.subplots()
        plot(g, target=ax)

    @image_comparison(baseline_images=["graph_directed"], remove_text=True)
    def test_directed(self):
        plt.close("all")
        g = Graph.Ring(5, directed=True)
        fig, ax = plt.subplots()
        plot(g, target=ax, layout=self.layout_small_ring)

    @image_comparison(baseline_images=["graph_directed_curved_loops"], remove_text=True)
    def test_directed_curved_loops(self):
        plt.close("all")
        g = Graph.Ring(5, directed=True)
        g.add_edge(0, 0)
        g.add_edge(0, 0)
        g.add_edge(2, 2)
        fig, ax = plt.subplots()
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        plot(
            g,
            target=ax,
            layout=self.layout_small_ring,
            edge_curved=[0] * 4 + [0.3],
            edge_loop_size=[0] * 5 + [30, 50, 40],
        )

    @image_comparison(baseline_images=["graph_mark_groups_directed"], remove_text=True)
    def test_mark_groups(self):
        plt.close("all")
        g = Graph.Ring(5, directed=True)
        fig, ax = plt.subplots()
        plot(g, target=ax, mark_groups=True, layout=self.layout_small_ring)

    @image_comparison(
        baseline_images=["graph_mark_groups_squares_directed"], remove_text=True
    )
    def test_mark_groups_squares(self):
        plt.close("all")
        g = Graph.Ring(5, directed=True)
        fig, ax = plt.subplots()
        plot(
            g,
            target=ax,
            mark_groups=True,
            vertex_shape="s",
            layout=self.layout_small_ring,
        )

    @image_comparison(baseline_images=["graph_edit_children"], remove_text=True)
    def test_edit_children(self):
        plt.close("all")
        g = Graph.Ring(5)
        fig, ax = plt.subplots()
        plot(g, target=ax, vertex_shape="o", layout=self.layout_small_ring)
        graph_artist = ax.get_children()[0]

        dots = graph_artist.get_vertices()
        dots.set_facecolors(["blue"] + list(dots.get_facecolors()[1:]))
        dots.set_sizes([20] + list(dots.get_sizes()[1:]))

        lines = graph_artist.get_edges()
        lines.set_edgecolor("green")

    @image_comparison(baseline_images=["graph_basic"], remove_text=True)
    def test_gh_587(self):
        plt.close("all")
        g = Graph.Ring(5)
        with overridden_configuration("plotting.backend", "matplotlib"):
            plot(g, target="graph_basic.png", layout=self.layout_small_ring)
            os.unlink("graph_basic.png")

    @image_comparison(baseline_images=["graph_with_curved_edges"])
    def test_graph_with_curved_edges(self):
        plt.close("all")
        g = Graph.Ring(24, directed=True, mutual=True)
        fig, ax = plt.subplots()
        lo = g.layout("circle")
        lo.scale(3)
        plot(
            g,
            target=ax,
            layout=lo,
            vertex_size=15,
            edge_arrow_size=5,
            edge_arrow_width=5,
        )
        ax.set_aspect(1.0)

    @image_comparison(baseline_images=["multigraph_with_curved_edges_undirected"])
    def test_graph_with_curved_edges_undirected(self):
        plt.close("all")
        g = Graph.Ring(24, directed=False)
        g.add_edges([(0, 1), (1, 2)])
        fig, ax = plt.subplots()
        lo = g.layout("circle")
        lo.scale(3)
        plot(
            g,
            target=ax,
            layout=lo,
            vertex_size=15,
            edge_arrow_size=5,
            edge_arrow_width=5,
        )
        ax.set_aspect(1.0)

    @image_comparison(baseline_images=["graph_null"])
    def test_null_graph(self):
        plt.close("all")
        g = Graph()
        fig, ax = plt.subplots()
        plot(g, target=ax)
        ax.set_aspect(1.0)


class ClusteringTestRunner(unittest.TestCase):
    def setUp(self):
        if mpl is None or plt is None:
            raise unittest.SkipTest("matplotlib not found, skipping tests")

    @property
    def layout_small_ring(self):
        coords = [
            [1.015318095035966, 0.03435580194714975],
            [0.29010409851547664, 1.0184451153265959],
            [-0.8699239050738742, 0.6328259400443561],
            [-0.8616466426732888, -0.5895891303732176],
            [0.30349699041342515, -0.9594640169691343],
        ]
        return coords

    @property
    def layout_large_ring(self):
        coords = [
            (2.5, 0.0),
            (2.4802867532861947, 0.31333308391076065),
            (2.4214579028215777, 0.621724717912137),
            (2.324441214720628, 0.9203113817116949),
            (2.190766700109659, 1.2043841852542883),
            (2.0225424859373686, 1.469463130731183),
            (1.822421568553529, 1.7113677648217218),
            (1.5935599743717241, 1.926283106939473),
            (1.3395669874474914, 2.110819813755038),
            (1.0644482289126818, 2.262067631165049),
            (0.7725424859373686, 2.3776412907378837),
            (0.4684532864643113, 2.4557181268217216),
            (0.15697629882328326, 2.495066821070679),
            (-0.1569762988232835, 2.495066821070679),
            (-0.46845328646431206, 2.4557181268217216),
            (-0.7725424859373689, 2.3776412907378837),
            (-1.0644482289126818, 2.2620676311650487),
            (-1.3395669874474923, 2.1108198137550374),
            (-1.5935599743717244, 1.926283106939473),
            (-1.8224215685535292, 1.7113677648217211),
            (-2.022542485937368, 1.4694631307311832),
            (-2.190766700109659, 1.204384185254288),
            (-2.3244412147206286, 0.9203113817116944),
            (-2.4214579028215777, 0.621724717912137),
            (-2.4802867532861947, 0.3133330839107602),
            (-2.5, -8.040613248383183e-16),
            (-2.4802867532861947, -0.3133330839107607),
            (-2.4214579028215777, -0.6217247179121376),
            (-2.324441214720628, -0.9203113817116958),
            (-2.1907667001096587, -1.2043841852542885),
            (-2.022542485937368, -1.4694631307311834),
            (-1.822421568553529, -1.7113677648217218),
            (-1.5935599743717237, -1.9262831069394735),
            (-1.339566987447491, -2.1108198137550382),
            (-1.0644482289126804, -2.2620676311650496),
            (-0.7725424859373689, -2.3776412907378837),
            (-0.46845328646431156, -2.4557181268217216),
            (-0.156976298823283, -2.495066821070679),
            (0.1569762988232843, -2.495066821070679),
            (0.46845328646431283, -2.4557181268217216),
            (0.7725424859373681, -2.377641290737884),
            (1.0644482289126815, -2.262067631165049),
            (1.3395669874474918, -2.1108198137550374),
            (1.593559974371725, -1.9262831069394726),
            (1.8224215685535297, -1.7113677648217207),
            (2.0225424859373695, -1.4694631307311814),
            (2.190766700109659, -1.2043841852542883),
            (2.3244412147206286, -0.9203113817116947),
            (2.421457902821578, -0.6217247179121362),
            (2.4802867532861947, -0.3133330839107595),
        ]
        return coords

    @image_comparison(baseline_images=["clustering_directed"], remove_text=True)
    def test_clustering_directed_small(self):
        plt.close("all")
        g = Graph.Ring(5, directed=True)
        clu = VertexClustering(g, [0] * 5)
        fig, ax = plt.subplots()
        plot(clu, target=ax, mark_groups=True, layout=self.layout_small_ring)

    @image_comparison(baseline_images=["clustering_directed_large"], remove_text=True)
    def test_clustering_directed_large(self):
        plt.close("all")
        g = Graph.Ring(50, directed=True)
        clu = VertexClustering(g, [0] * 3 + [1] * 17 + [2] * 30)
        fig, ax = plt.subplots()
        plot(
            clu,
            vertex_size=17,
            edge_arrow_size=5,
            edge_arrow_width=5,
            layout=self.layout_large_ring,
            target=ax,
            mark_groups=True,
        )


def suite():
    graph = unittest.defaultTestLoader.loadTestsFromTestCase(GraphTestRunner)
    clustering = unittest.defaultTestLoader.loadTestsFromTestCase(ClusteringTestRunner)
    return unittest.TestSuite([graph, clustering])


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
