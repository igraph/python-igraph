import unittest


from igraph import Graph, plot, VertexClustering

# FIXME: find a better way to do this that works for both direct call and module
# import e.g. tox
try:
    from .utils import find_image_comparison
except ImportError:
    from utils import find_image_comparison

try:
    import plotly
except ImportError:
    plotly = None

if plotly is not None:
    from plotly import graph_objects as go

image_comparison = find_image_comparison()


class GraphTestRunner(unittest.TestCase):
    def setUp(self):
        if plotly is None:
            raise unittest.SkipTest("plotly not found, skipping tests")

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

    @image_comparison(baseline_images=["graph_basic"])
    def test_basic(self):
        g = Graph.Ring(5)
        fig = go.Figure()
        plot(g, target=fig, layout=self.layout_small_ring)
        return fig

    @image_comparison(baseline_images=["graph_directed"])
    def test_directed(self):
        g = Graph.Ring(5, directed=True)
        fig = go.Figure()
        plot(g, target=fig, layout=self.layout_small_ring)
        return fig

    @image_comparison(baseline_images=["graph_mark_groups_directed"])
    def test_mark_groups(self):
        g = Graph.Ring(5, directed=True)
        fig = go.Figure()
        plot(g, target=fig, mark_groups=True, layout=self.layout_small_ring)
        return fig

    @image_comparison(baseline_images=["graph_mark_groups_squares_directed"])
    def test_mark_groups_squares(self):
        g = Graph.Ring(5, directed=True)
        fig = go.Figure()
        plot(
            g,
            target=fig,
            mark_groups=True,
            vertex_shape="square",
            layout=self.layout_small_ring,
        )
        return fig

    @image_comparison(baseline_images=["graph_edit_children"])
    def test_graph_edit_children(self):
        g = Graph.Ring(5)
        fig = go.Figure()
        plot(g, target=fig, vertex_shape="circle", layout=self.layout_small_ring)
        # FIXME
        # dot = ax.get_children()[0]
        # dot.set_facecolor("blue")
        # dot.radius *= 0.5
        return fig

    @image_comparison(baseline_images=["graph_null"])
    def test_null_graph(self):
        g = Graph()
        fig = go.Figure()
        plot(g, target=fig)
        return fig


class ClusteringTestRunner(unittest.TestCase):
    def setUp(self):
        if plotly is None:
            raise unittest.SkipTest("plotly not found, skipping tests")

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

    @image_comparison(baseline_images=["clustering_directed"])
    def test_clustering_directed_small(self):
        g = Graph.Ring(5, directed=True)
        clu = VertexClustering(g, [0] * 5)
        fig = go.Figure()
        plot(clu, target=fig, mark_groups=True, layout=self.layout_small_ring)
        return fig

    @image_comparison(baseline_images=["clustering_directed_large"])
    def test_clustering_directed_large(self):
        g = Graph.Ring(50, directed=True)
        clu = VertexClustering(g, [0] * 3 + [1] * 17 + [2] * 30)
        fig = go.Figure()
        plot(clu, layout=self.layout_large_ring, target=fig, mark_groups=True)
        return fig


def suite():
    graph = unittest.defaultTestLoader.loadTestsFromTestCase(GraphTestRunner)
    clustering = unittest.defaultTestLoader.loadTestsFromTestCase(ClusteringTestRunner)
    return unittest.TestSuite(
        [
            graph,
            clustering,
        ]
    )


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
