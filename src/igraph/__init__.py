"""
IGraph library.
"""


__license__ = """
Copyright (C) 2006- The igraph development team

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc.,  51 Franklin Street, Fifth Floor, Boston, MA
02110-1301 USA
"""

from igraph._igraph import (
    ADJ_DIRECTED,
    ADJ_LOWER,
    ADJ_MAX,
    ADJ_MIN,
    ADJ_PLUS,
    ADJ_UNDIRECTED,
    ADJ_UPPER,
    ALL,
    ARPACKOptions,
    BFSIter,
    BLISS_F,
    BLISS_FL,
    BLISS_FLM,
    BLISS_FM,
    BLISS_FS,
    BLISS_FSM,
    DFSIter,
    Edge,
    EdgeSeq as _EdgeSeq,
    GET_ADJACENCY_BOTH,
    GET_ADJACENCY_LOWER,
    GET_ADJACENCY_UPPER,
    GraphBase,
    IN,
    InternalError,
    OUT,
    REWIRING_SIMPLE,
    REWIRING_SIMPLE_LOOPS,
    STAR_IN,
    STAR_MUTUAL,
    STAR_OUT,
    STAR_UNDIRECTED,
    STRONG,
    TRANSITIVITY_NAN,
    TRANSITIVITY_ZERO,
    TREE_IN,
    TREE_OUT,
    TREE_UNDIRECTED,
    Vertex,
    VertexSeq as _VertexSeq,
    WEAK,
    arpack_options as default_arpack_options,
    community_to_membership,
    convex_hull,
    is_degree_sequence,
    is_graphical,
    is_graphical_degree_sequence,
    set_progress_handler,
    set_random_number_generator,
    set_status_handler,
    __igraph_version__,
)
from igraph.community import (
    _community_fastgreedy,
    _community_infomap,
    _community_leading_eigenvector_naive,
    _community_leading_eigenvector,
    _community_label_propagation,
    _community_multilevel,
    _community_optimal_modularity,
    _community_edge_betweenness,
    _community_spinglass,
    _community_walktrap,
    _k_core,
    _community_leiden,
)
from igraph.clustering import (
    Clustering,
    VertexClustering,
    Dendrogram,
    VertexDendrogram,
    Cover,
    VertexCover,
    CohesiveBlocks,
    compare_communities,
    split_join_distance,
)
from igraph.cut import Cut, Flow
from igraph.configuration import Configuration, init as init_configuration
from igraph.drawing import (
    BoundingBox,
    CairoGraphDrawer,
    DefaultGraphDrawer,
    MatplotlibGraphDrawer,
    Plot,
    Point,
    Rectangle,
    plot,
)
from igraph.drawing.colors import (
    Palette,
    GradientPalette,
    AdvancedGradientPalette,
    RainbowPalette,
    PrecalculatedPalette,
    ClusterColoringPalette,
    color_name_to_rgb,
    color_name_to_rgba,
    hsv_to_rgb,
    hsva_to_rgba,
    hsl_to_rgb,
    hsla_to_rgba,
    rgb_to_hsv,
    rgba_to_hsva,
    rgb_to_hsl,
    rgba_to_hsla,
    palettes,
    known_colors,
)
from igraph.drawing.graph import __plot__ as _graph_plot
from igraph.drawing.utils import autocurve
from igraph.datatypes import Matrix, DyadCensus, TriadCensus, UniqueIdGenerator
from igraph.formula import construct_graph_from_formula
from igraph.io.files import (
    _construct_graph_from_graphmlz_file,
    _construct_graph_from_dimacs_file,
    _construct_graph_from_pickle_file,
    _construct_graph_from_picklez_file,
    _construct_graph_from_adjacency_file,
    _construct_graph_from_file,
    _write_graph_to_adjacency_file,
    _write_graph_to_dimacs_file,
    _write_graph_to_graphmlz_file,
    _write_graph_to_pickle_file,
    _write_graph_to_picklez_file,
    _write_graph_to_file,
)
from igraph.io.objects import (
    _construct_graph_from_dict_list,
    _export_graph_to_dict_list,
    _construct_graph_from_tuple_list,
    _export_graph_to_tuple_list,
    _construct_graph_from_list_dict,
    _export_graph_to_list_dict,
    _construct_graph_from_dict_dict,
    _export_graph_to_dict_dict,
    _construct_graph_from_dataframe,
    _export_vertex_dataframe,
    _export_edge_dataframe,
)
from igraph.io.adjacency import (
    _construct_graph_from_adjacency,
    _construct_graph_from_weighted_adjacency,
)
from igraph.io.libraries import (
    _construct_graph_from_networkx,
    _export_graph_to_networkx,
    _construct_graph_from_graph_tool,
    _export_graph_to_graph_tool,
)
from igraph.io.random import (
    _construct_random_geometric_graph,
)
from igraph.io.bipartite import (
    _construct_bipartite_graph,
    _construct_incidence_bipartite_graph,
    _construct_full_bipartite_graph,
    _construct_random_bipartite_graph,
)
from igraph.io.images import _write_graph_to_svg
from igraph.layout import Layout
from igraph.matching import Matching
from igraph.operators import (
    disjoint_union,
    union,
    intersection,
    operator_method_registry as _operator_method_registry,
)
from igraph.seq import EdgeSeq, VertexSeq
from igraph.statistics import (
    FittedPowerLaw,
    Histogram,
    RunningMean,
    mean,
    median,
    percentile,
    quantile,
    power_law_fit,
)
from igraph.summary import GraphSummary, summary
from igraph.utils import (
    dbl_epsilon,
    multidict,
    named_temporary_file,
    numpy_to_contiguous_memoryview,
    rescale,
    safemin,
    safemax,
)
from igraph.version import __version__, __version_info__

import os
import sys
import operator

from collections import defaultdict
from shutil import copyfileobj
from warnings import warn


def deprecated(message):
    """Prints a warning message related to the deprecation of some igraph
    feature."""
    warn(message, DeprecationWarning, stacklevel=3)


class Graph(GraphBase):
    """Generic graph.

    This class is built on top of L{GraphBase}, so the order of the
    methods in the generated API documentation is a little bit obscure:
    inherited methods come after the ones implemented directly in the
    subclass. L{Graph} provides many functions that L{GraphBase} does not,
    mostly because these functions are not speed critical and they were
    easier to implement in Python than in pure C. An example is the
    attribute handling in the constructor: the constructor of L{Graph}
    accepts three dictionaries corresponding to the graph, vertex and edge
    attributes while the constructor of L{GraphBase} does not. This extension
    was needed to make L{Graph} serializable through the C{pickle} module.
    L{Graph} also overrides some functions from L{GraphBase} to provide a
    more convenient interface; e.g., layout functions return a L{Layout}
    instance from L{Graph} instead of a list of coordinate pairs.

    Graphs can also be indexed by strings or pairs of vertex indices or vertex
    names.  When a graph is indexed by a string, the operation translates to
    the retrieval, creation, modification or deletion of a graph attribute:

      >>> g = Graph.Full(3)
      >>> g["name"] = "Triangle graph"
      >>> g["name"]
      'Triangle graph'
      >>> del g["name"]

    When a graph is indexed by a pair of vertex indices or names, the graph
    itself is treated as an adjacency matrix and the corresponding cell of
    the matrix is returned:

      >>> g = Graph.Full(3)
      >>> g.vs["name"] = ["A", "B", "C"]
      >>> g[1, 2]
      1
      >>> g["A", "B"]
      1
      >>> g["A", "B"] = 0
      >>> g.ecount()
      2

    Assigning values different from zero or one to the adjacency matrix will
    be translated to one, unless the graph is weighted, in which case the
    numbers will be treated as weights:

      >>> g.is_weighted()
      False
      >>> g["A", "B"] = 2
      >>> g["A", "B"]
      1
      >>> g.es["weight"] = 1.0
      >>> g.is_weighted()
      True
      >>> g["A", "B"] = 2
      >>> g["A", "B"]
      2
      >>> g.es["weight"]
      [1.0, 1.0, 2]
    """

    # Some useful aliases
    omega = GraphBase.clique_number
    alpha = GraphBase.independence_number
    shell_index = GraphBase.coreness
    cut_vertices = GraphBase.articulation_points
    blocks = GraphBase.biconnected_components
    evcent = GraphBase.eigenvector_centrality
    vertex_disjoint_paths = GraphBase.vertex_connectivity
    edge_disjoint_paths = GraphBase.edge_connectivity
    cohesion = GraphBase.vertex_connectivity
    adhesion = GraphBase.edge_connectivity

    # Compatibility aliases
    shortest_paths_dijkstra = GraphBase.shortest_paths
    subgraph = GraphBase.induced_subgraph

    def __init__(self, *args, **kwds):
        """__init__(n=0, edges=None, directed=False, graph_attrs=None,
        vertex_attrs=None, edge_attrs=None)

        Constructs a graph from scratch.

        @keyword n: the number of vertices. Can be omitted, the default is
          zero. Note that if the edge list contains vertices with indexes
          larger than or equal to M{m}, then the number of vertices will
          be adjusted accordingly.
        @keyword edges: the edge list where every list item is a pair of
          integers. If any of the integers is larger than M{n-1}, the number
          of vertices is adjusted accordingly. C{None} means no edges.
        @keyword directed: whether the graph should be directed
        @keyword graph_attrs: the attributes of the graph as a dictionary.
        @keyword vertex_attrs: the attributes of the vertices as a dictionary.
          Every dictionary value must be an iterable with exactly M{n} items.
        @keyword edge_attrs: the attributes of the edges as a dictionary. Every
          dictionary value must be an iterable with exactly M{m} items where
          M{m} is the number of edges.
        """
        # Pop the special __ptr keyword argument
        ptr = kwds.pop("__ptr", None)

        # Set up default values for the parameters. This should match the order
        # in *args
        kwd_order = (
            "n",
            "edges",
            "directed",
            "graph_attrs",
            "vertex_attrs",
            "edge_attrs",
        )
        params = [0, [], False, {}, {}, {}]

        # Is there any keyword argument in kwds that we don't know? If so,
        # freak out.
        unknown_kwds = set(kwds.keys())
        unknown_kwds.difference_update(kwd_order)
        if unknown_kwds:
            raise TypeError(
                "{0}.__init__ got an unexpected keyword argument {1!r}".format(
                    self.__class__.__name__, unknown_kwds.pop()
                )
            )

        # If the first argument is a list or any other iterable, assume that
        # the number of vertices were omitted
        args = list(args)
        if len(args) > 0 and hasattr(args[0], "__iter__"):
            args.insert(0, params[0])

        # Override default parameters from args
        params[: len(args)] = args

        # Override default parameters from keywords
        for idx, k in enumerate(kwd_order):
            if k in kwds:
                params[idx] = kwds[k]

        # Now, translate the params list to argument names
        nverts, edges, directed, graph_attrs, vertex_attrs, edge_attrs = params

        # When the number of vertices is None, assume that the user meant zero
        if nverts is None:
            nverts = 0

        # When 'edges' is None, assume that the user meant an empty list
        if edges is None:
            edges = []

        # When 'edges' is a NumPy array or matrix, convert it into a memoryview
        # as the lower-level C API works with memoryviews only
        try:
            from numpy import ndarray, matrix

            if isinstance(edges, (ndarray, matrix)):
                edges = numpy_to_contiguous_memoryview(edges)
        except ImportError:
            pass

        # Initialize the graph
        if ptr:
            GraphBase.__init__(self, __ptr=ptr)
        else:
            GraphBase.__init__(self, nverts, edges, directed)

        # Set the graph attributes
        for key, value in graph_attrs.items():
            if isinstance(key, int):
                key = str(key)
            self[key] = value
        # Set the vertex attributes
        for key, value in vertex_attrs.items():
            if isinstance(key, int):
                key = str(key)
            self.vs[key] = value
        # Set the edge attributes
        for key, value in edge_attrs.items():
            if isinstance(key, int):
                key = str(key)
            self.es[key] = value

    def add_edge(self, source, target, **kwds):
        """Adds a single edge to the graph.

        Keyword arguments (except the source and target arguments) will be
        assigned to the edge as attributes.

        The performance cost of adding a single edge or several edges
        to a graph is similar. Thus, when adding several edges, a single
        C{add_edges()} call is more efficient than multiple C{add_edge()} calls.

        @param source: the source vertex of the edge or its name.
        @param target: the target vertex of the edge or its name.

        @return: the newly added edge as an L{Edge} object. Use
            C{add_edges([(source, target)])} if you don't need the L{Edge}
            object and want to avoid the overhead of creating it.
        """
        eid = self.ecount()
        self.add_edges([(source, target)])
        edge = self.es[eid]
        for key, value in kwds.items():
            edge[key] = value
        return edge

    def add_edges(self, es, attributes=None):
        """Adds some edges to the graph.

        @param es: the list of edges to be added. Every edge is represented
          with a tuple containing the vertex IDs or names of the two
          endpoints. Vertices are enumerated from zero.
        @param attributes: dict of sequences, all of length equal to the
          number of edges to be added, containing the attributes of the new
          edges.
        """
        eid = self.ecount()
        res = GraphBase.add_edges(self, es)
        n = self.ecount() - eid
        if (attributes is not None) and (n > 0):
            for key, val in list(attributes.items()):
                self.es[eid:][key] = val
        return res

    def add_vertex(self, name=None, **kwds):
        """Adds a single vertex to the graph. Keyword arguments will be assigned
        as vertex attributes. Note that C{name} as a keyword argument is treated
        specially; if a graph has C{name} as a vertex attribute, it allows one
        to refer to vertices by their names in most places where igraph expects
        a vertex ID.

        @return: the newly added vertex as a L{Vertex} object. Use
            C{add_vertices(1)} if you don't need the L{Vertex} object and want
            to avoid the overhead of creating t.
        """
        vid = self.vcount()
        self.add_vertices(1)
        vertex = self.vs[vid]
        for key, value in kwds.items():
            vertex[key] = value
        if name is not None:
            vertex["name"] = name
        return vertex

    def add_vertices(self, n, attributes=None):
        """Adds some vertices to the graph.

        Note that if C{n} is a sequence of strings, indicating the names of the
        new vertices, and attributes has a key C{name}, the two conflict. In
        that case the attribute will be applied.

        @param n: the number of vertices to be added, or the name of a single
          vertex to be added, or a sequence of strings, each corresponding to the
          name of a vertex to be added. Names will be assigned to the C{name}
          vertex attribute.
        @param attributes: dict of sequences, all of length equal to the
          number of vertices to be added, containing the attributes of the new
          vertices. If n is a string (so a single vertex is added), then the
          values of this dict are the attributes themselves, but if n=1 then
          they have to be lists of length 1.
        """
        if isinstance(n, str):
            # Adding a single vertex with a name
            m = self.vcount()
            result = GraphBase.add_vertices(self, 1)
            self.vs[m]["name"] = n
            if attributes is not None:
                for key, val in list(attributes.items()):
                    self.vs[m][key] = val
        elif hasattr(n, "__iter__"):
            m = self.vcount()
            if not hasattr(n, "__len__"):
                names = list(n)
            else:
                names = n
            result = GraphBase.add_vertices(self, len(names))
            if len(names) > 0:
                self.vs[m:]["name"] = names
                if attributes is not None:
                    for key, val in list(attributes.items()):
                        self.vs[m:][key] = val
        else:
            result = GraphBase.add_vertices(self, n)
            if (attributes is not None) and (n > 0):
                m = self.vcount() - n
                for key, val in list(attributes.items()):
                    self.vs[m:][key] = val
        return result

    def as_directed(self, *args, **kwds):
        """Returns a directed copy of this graph. Arguments are passed on
        to L{to_directed()} that is invoked on the copy.
        """
        copy = self.copy()
        copy.to_directed(*args, **kwds)
        return copy

    def as_undirected(self, *args, **kwds):
        """Returns an undirected copy of this graph. Arguments are passed on
        to L{to_undirected()} that is invoked on the copy.
        """
        copy = self.copy()
        copy.to_undirected(*args, **kwds)
        return copy

    def delete_edges(self, *args, **kwds):
        """Deletes some edges from the graph.

        The set of edges to be deleted is determined by the positional and
        keyword arguments. If the function is called without any arguments,
        all edges are deleted. If any keyword argument is present, or the
        first positional argument is callable, an edge sequence is derived by
        calling L{EdgeSeq.select} with the same positional and keyword
        arguments. Edges in the derived edge sequence will be removed.
        Otherwise the first positional argument is considered as follows:

          - C{None} - deletes all edges (deprecated since 0.8.3)
          - a single integer - deletes the edge with the given ID
          - a list of integers - deletes the edges denoted by the given IDs
          - a list of 2-tuples - deletes the edges denoted by the given
            source-target vertex pairs. When multiple edges are present
            between a given source-target vertex pair, only one is removed.

        @deprecated: C{delete_edges(None)} has been replaced by
        C{delete_edges()} - with no arguments - since igraph 0.8.3.
        """
        if len(args) == 0 and len(kwds) == 0:
            return GraphBase.delete_edges(self)

        if len(kwds) > 0 or (callable(args[0]) and not isinstance(args[0], EdgeSeq)):
            edge_seq = self.es(*args, **kwds)
        else:
            edge_seq = args[0]
        return GraphBase.delete_edges(self, edge_seq)

    def indegree(self, *args, **kwds):
        """Returns the in-degrees in a list.

        See L{degree} for possible arguments.
        """
        kwds["mode"] = IN
        return self.degree(*args, **kwds)

    def outdegree(self, *args, **kwds):
        """Returns the out-degrees in a list.

        See L{degree} for possible arguments.
        """
        kwds["mode"] = OUT
        return self.degree(*args, **kwds)

    def all_st_cuts(self, source, target):
        """\
        Returns all the cuts between the source and target vertices in a
        directed graph.

        This function lists all edge-cuts between a source and a target vertex.
        Every cut is listed exactly once.

        @param source: the source vertex ID
        @param target: the target vertex ID
        @return: a list of L{Cut} objects.

        @newfield ref: Reference
        @ref: JS Provan and DR Shier: A paradigm for listing (s,t)-cuts in
          graphs. Algorithmica 15, 351--372, 1996.
        """
        return [
            Cut(self, cut=cut, partition=part)
            for cut, part in zip(*GraphBase.all_st_cuts(self, source, target))
        ]

    def all_st_mincuts(self, source, target, capacity=None):
        """\
        Returns all the mincuts between the source and target vertices in a
        directed graph.

        This function lists all minimum edge-cuts between a source and a target
        vertex.

        @param source: the source vertex ID
        @param target: the target vertex ID
        @param capacity: the edge capacities (weights). If C{None}, all
          edges have equal weight. May also be an attribute name.
        @return: a list of L{Cut} objects.

        @newfield ref: Reference
        @ref: JS Provan and DR Shier: A paradigm for listing (s,t)-cuts in
          graphs. Algorithmica 15, 351--372, 1996.
        """
        value, cuts, parts = GraphBase.all_st_mincuts(self, source, target, capacity)
        return [
            Cut(self, value, cut=cut, partition=part) for cut, part in zip(cuts, parts)
        ]

    def biconnected_components(self, return_articulation_points=False):
        """\
        Calculates the biconnected components of the graph.

        @param return_articulation_points: whether to return the articulation
          points as well
        @return: a L{VertexCover} object describing the biconnected components,
          and optionally the list of articulation points as well
        """
        if return_articulation_points:
            trees, aps = GraphBase.biconnected_components(self, True)
        else:
            trees = GraphBase.biconnected_components(self, False)

        clusters = []
        if trees:
            edgelist = self.get_edgelist()
            for tree in trees:
                cluster = set()
                for edge_id in tree:
                    cluster.update(edgelist[edge_id])
                clusters.append(sorted(cluster))

        clustering = VertexCover(self, clusters)

        if return_articulation_points:
            return clustering, aps
        else:
            return clustering

    blocks = biconnected_components

    def clear(self):
        """Clears the graph, deleting all vertices, edges, and attributes.

        @see: L{delete_vertices} and L{delete_edges}.
        """
        self.delete_vertices()
        for attr in self.attributes():
            del self[attr]

    def cohesive_blocks(self):
        """Calculates the cohesive block structure of the graph.

        Cohesive blocking is a method of determining hierarchical subsets of graph
        vertices based on their structural cohesion (i.e. vertex connectivity).
        For a given graph G, a subset of its vertices S is said to be maximally
        k-cohesive if there is no superset of S with vertex connectivity greater
        than or equal to k. Cohesive blocking is a process through which, given a
        k-cohesive set of vertices, maximally l-cohesive subsets are recursively
        identified with l > k. Thus a hierarchy of vertex subsets is obtained in
        the end, with the entire graph G at its root.

        @return: an instance of L{CohesiveBlocks}. See the documentation of
          L{CohesiveBlocks} for more information.
        @see: L{CohesiveBlocks}
        """
        return CohesiveBlocks(self, *GraphBase.cohesive_blocks(self))

    def clusters(self, mode="strong"):
        """Calculates the (strong or weak) clusters (connected components) for
        a given graph.

        @param mode: must be either C{"strong"} or C{"weak"}, depending on the
          clusters being sought. Optional, defaults to C{"strong"}.
        @return: a L{VertexClustering} object"""
        return VertexClustering(self, GraphBase.clusters(self, mode))

    components = clusters

    def degree_distribution(self, bin_width=1, *args, **kwds):
        """Calculates the degree distribution of the graph.

        Unknown keyword arguments are directly passed to L{degree()}.

        @param bin_width: the bin width of the histogram
        @return: a histogram representing the degree distribution of the
          graph.
        """
        result = Histogram(bin_width, self.degree(*args, **kwds))
        return result

    def dyad_census(self, *args, **kwds):
        """Calculates the dyad census of the graph.

        Dyad census means classifying each pair of vertices of a directed
        graph into three categories: mutual (there is an edge from I{a} to
        I{b} and also from I{b} to I{a}), asymmetric (there is an edge
        from I{a} to I{b} or from I{b} to I{a} but not the other way round)
        and null (there is no connection between I{a} and I{b}).

        @return: a L{DyadCensus} object.
        @newfield ref: Reference
        @ref: Holland, P.W. and Leinhardt, S.  (1970).  A Method for Detecting
          Structure in Sociometric Data.  American Journal of Sociology, 70,
          492-513.
        """
        return DyadCensus(GraphBase.dyad_census(self, *args, **kwds))

    def get_adjacency(
        self, type=GET_ADJACENCY_BOTH, attribute=None, default=0, eids=False
    ):
        """Returns the adjacency matrix of a graph.

        @param type: either C{GET_ADJACENCY_LOWER} (uses the lower
          triangle of the matrix) or C{GET_ADJACENCY_UPPER}
          (uses the upper triangle) or C{GET_ADJACENCY_BOTH}
          (uses both parts). Ignored for directed graphs.
        @param attribute: if C{None}, returns the ordinary adjacency
          matrix. When the name of a valid edge attribute is given
          here, the matrix returned will contain the default value
          at the places where there is no edge or the value of the
          given attribute where there is an edge. Multiple edges are
          not supported, the value written in the matrix in this case
          will be unpredictable. This parameter is ignored if
          I{eids} is C{True}
        @param default: the default value written to the cells in the
          case of adjacency matrices with attributes.
        @param eids: specifies whether the edge IDs should be returned
          in the adjacency matrix. Since zero is a valid edge ID, the
          cells in the matrix that correspond to unconnected vertex
          pairs will contain -1 instead of 0 if I{eids} is C{True}.
          If I{eids} is C{False}, the number of edges will be returned
          in the matrix for each vertex pair.
        @return: the adjacency matrix as a L{Matrix}.
        """
        if (
            type != GET_ADJACENCY_LOWER
            and type != GET_ADJACENCY_UPPER
            and type != GET_ADJACENCY_BOTH
        ):
            # Maybe it was called with the first argument as the attribute name
            type, attribute = attribute, type
            if type is None:
                type = GET_ADJACENCY_BOTH

        if eids:
            result = Matrix(GraphBase.get_adjacency(self, type, eids))
            result -= 1
            return result

        if attribute is None:
            return Matrix(GraphBase.get_adjacency(self, type))

        if attribute not in self.es.attribute_names():
            raise ValueError("Attribute does not exist")

        data = [[default] * self.vcount() for _ in range(self.vcount())]

        if self.is_directed():
            for edge in self.es:
                data[edge.source][edge.target] = edge[attribute]
            return Matrix(data)

        if type == GET_ADJACENCY_BOTH:
            for edge in self.es:
                source, target = edge.tuple
                data[source][target] = edge[attribute]
                data[target][source] = edge[attribute]
        elif type == GET_ADJACENCY_UPPER:
            for edge in self.es:
                data[min(edge.tuple)][max(edge.tuple)] = edge[attribute]
        else:
            for edge in self.es:
                data[max(edge.tuple)][min(edge.tuple)] = edge[attribute]

        return Matrix(data)

    def get_adjacency_sparse(self, attribute=None):
        """Returns the adjacency matrix of a graph as a SciPy CSR matrix.

        @param attribute: if C{None}, returns the ordinary adjacency
          matrix. When the name of a valid edge attribute is given
          here, the matrix returned will contain the default value
          at the places where there is no edge or the value of the
          given attribute where there is an edge.
        @return: the adjacency matrix as a C{scipy.sparse.csr_matrix}.
        """
        try:
            from scipy import sparse
        except ImportError:
            raise ImportError("You should install scipy in order to use this function")

        edges = self.get_edgelist()
        if attribute is None:
            weights = [1] * len(edges)
        else:
            if attribute not in self.es.attribute_names():
                raise ValueError("Attribute does not exist")

            weights = self.es[attribute]

        N = self.vcount()
        mtx = sparse.csr_matrix((weights, list(zip(*edges))), shape=(N, N))

        if not self.is_directed():
            mtx = mtx + sparse.triu(mtx, 1).T + sparse.tril(mtx, -1).T
        return mtx

    def get_adjlist(self, mode="out"):
        """Returns the adjacency list representation of the graph.

        The adjacency list representation is a list of lists. Each item of the
        outer list belongs to a single vertex of the graph. The inner list
        contains the neighbors of the given vertex.

        @param mode: if C{\"out\"}, returns the successors of the vertex. If
          C{\"in\"}, returns the predecessors of the vertex. If C{\"all"\"}, both
          the predecessors and the successors will be returned. Ignored
          for undirected graphs.
        """
        return [self.neighbors(idx, mode) for idx in range(self.vcount())]

    def get_all_simple_paths(self, v, to=None, cutoff=-1, mode="out"):
        """Calculates all the simple paths from a given node to some other nodes
        (or all of them) in a graph.

        A path is simple if its vertices are unique, i.e. no vertex is visited
        more than once.

        Note that potentially there are exponentially many paths between two
        vertices of a graph, especially if your graph is lattice-like. In this
        case, you may run out of memory when using this function.

        @param v: the source for the calculated paths
        @param to: a vertex selector describing the destination for the calculated
          paths. This can be a single vertex ID, a list of vertex IDs, a single
          vertex name, a list of vertex names or a L{VertexSeq} object. C{None}
          means all the vertices.
        @param cutoff: maximum length of path that is considered. If negative,
          paths of all lengths are considered.
        @param mode: the directionality of the paths. C{\"in\"} means to calculate
          incoming paths, C{\"out\"} means to calculate outgoing paths, C{\"all\"} means
          to calculate both ones.
        @return: all of the simple paths from the given node to every other
          reachable node in the graph in a list. Note that in case of mode=C{\"in\"},
          the vertices in a path are returned in reversed order!
        """
        paths = self._get_all_simple_paths(v, to, cutoff, mode)
        prev = 0
        result = []
        for index, item in enumerate(paths):
            if item < 0:
                result.append(paths[prev:index])
                prev = index + 1
        return result

    def get_inclist(self, mode="out"):
        """Returns the incidence list representation of the graph.

        The incidence list representation is a list of lists. Each
        item of the outer list belongs to a single vertex of the graph.
        The inner list contains the IDs of the incident edges of the
        given vertex.

        @param mode: if C{\"out\"}, returns the successors of the vertex. If
          C{\"in\"}, returns the predecessors of the vertex. If C{\"all\"}, both
          the predecessors and the successors will be returned. Ignored
          for undirected graphs.
        """
        return [self.incident(idx, mode) for idx in range(self.vcount())]

    def gomory_hu_tree(self, capacity=None, flow="flow"):
        """Calculates the Gomory-Hu tree of an undirected graph with optional
        edge capacities.

        The Gomory-Hu tree is a concise representation of the value of all the
        maximum flows (or minimum cuts) in a graph. The vertices of the tree
        correspond exactly to the vertices of the original graph in the same order.
        Edges of the Gomory-Hu tree are annotated by flow values.  The value of
        the maximum flow (or minimum cut) between an arbitrary (u,v) vertex
        pair in the original graph is then given by the minimum flow value (i.e.
        edge annotation) along the shortest path between u and v in the
        Gomory-Hu tree.

        @param capacity: the edge capacities (weights). If C{None}, all
          edges have equal weight. May also be an attribute name.
        @param flow: the name of the edge attribute in the returned graph
          in which the flow values will be stored.
        @return: the Gomory-Hu tree as a L{Graph} object.
        """
        graph, flow_values = GraphBase.gomory_hu_tree(self, capacity)
        graph.es[flow] = flow_values
        return graph

    def is_named(self):
        """Returns whether the graph is named.

        A graph is named if and only if it has a C{"name"} vertex attribute.
        """
        return "name" in self.vertex_attributes()

    def is_weighted(self):
        """Returns whether the graph is weighted.

        A graph is weighted if and only if it has a C{"weight"} edge attribute.
        """
        return "weight" in self.edge_attributes()

    def maxflow(self, source, target, capacity=None):
        """Returns a maximum flow between the given source and target vertices
        in a graph.

        A maximum flow from I{source} to I{target} is an assignment of
        non-negative real numbers to the edges of the graph, satisfying
        two properties:

            1. For each edge, the flow (i.e. the assigned number) is not
               more than the capacity of the edge (see the I{capacity}
               argument)

            2. For every vertex except the source and the target, the
               incoming flow is the same as the outgoing flow.

        The value of the flow is the incoming flow of the target or the
        outgoing flow of the source (which are equal). The maximum flow
        is the maximum possible such value.

        @param capacity: the edge capacities (weights). If C{None}, all
          edges have equal weight. May also be an attribute name.
        @return: a L{Flow} object describing the maximum flow
        """
        return Flow(self, *GraphBase.maxflow(self, source, target, capacity))

    def mincut(self, source=None, target=None, capacity=None):
        """Calculates the minimum cut between the given source and target vertices
        or within the whole graph.

        The minimum cut is the minimum set of edges that needs to be removed to
        separate the source and the target (if they are given) or to disconnect the
        graph (if neither the source nor the target are given). The minimum is
        calculated using the weights (capacities) of the edges, so the cut with
        the minimum total capacity is calculated.

        For undirected graphs and no source and target, the method uses the
        Stoer-Wagner algorithm. For a given source and target, the method uses the
        push-relabel algorithm; see the references below.

        @param source: the source vertex ID. If C{None}, the target must also be
          C{None} and the calculation will be done for the entire graph (i.e.
          all possible vertex pairs).
        @param target: the target vertex ID. If C{None}, the source must also be
          C{None} and the calculation will be done for the entire graph (i.e.
          all possible vertex pairs).
        @param capacity: the edge capacities (weights). If C{None}, all
          edges have equal weight. May also be an attribute name.
        @return: a L{Cut} object describing the minimum cut
        """
        return Cut(self, *GraphBase.mincut(self, source, target, capacity))

    def st_mincut(self, source, target, capacity=None):
        """Calculates the minimum cut between the source and target vertices in a
        graph.

        @param source: the source vertex ID
        @param target: the target vertex ID
        @param capacity: the capacity of the edges. It must be a list or a valid
          attribute name or C{None}. In the latter case, every edge will have the
          same capacity.
        @return: the value of the minimum cut, the IDs of vertices in the
          first and second partition, and the IDs of edges in the cut,
          packed in a 4-tuple
        """
        return Cut(self, *GraphBase.st_mincut(self, source, target, capacity))

    def modularity(self, membership, weights=None):
        """Calculates the modularity score of the graph with respect to a given
        clustering.

        The modularity of a graph w.r.t. some division measures how good the
        division is, or how separated are the different vertex types from each
        other. It's defined as M{Q=1/(2m)*sum(Aij-ki*kj/(2m)delta(ci,cj),i,j)}.
        M{m} is the number of edges, M{Aij} is the element of the M{A}
        adjacency matrix in row M{i} and column M{j}, M{ki} is the degree of
        node M{i}, M{kj} is the degree of node M{j}, and M{Ci} and C{cj} are
        the types of the two vertices (M{i} and M{j}). M{delta(x,y)} is one iff
        M{x=y}, 0 otherwise.

        If edge weights are given, the definition of modularity is modified as
        follows: M{Aij} becomes the weight of the corresponding edge, M{ki}
        is the total weight of edges adjacent to vertex M{i}, M{kj} is the
        total weight of edges adjacent to vertex M{j} and M{m} is the total
        edge weight in the graph.

        @param membership: a membership list or a L{VertexClustering} object
        @param weights: optional edge weights or C{None} if all edges are
          weighed equally. Attribute names are also allowed.
        @return: the modularity score

        @newfield ref: Reference
        @ref: MEJ Newman and M Girvan: Finding and evaluating community
          structure in networks. Phys Rev E 69 026113, 2004.
        """
        if isinstance(membership, VertexClustering):
            if membership.graph != self:
                raise ValueError("clustering object belongs to another graph")
            return GraphBase.modularity(self, membership.membership, weights)
        else:
            return GraphBase.modularity(self, membership, weights)

    def path_length_hist(self, directed=True):
        """Returns the path length histogram of the graph

        @param directed: whether to consider directed paths. Ignored for
          undirected graphs.
        @return: a L{Histogram} object. The object will also have an
          C{unconnected} attribute that stores the number of unconnected
          vertex pairs (where the second vertex can not be reached from
          the first one). The latter one will be of type long (and not
          a simple integer), since this can be I{very} large.
        """
        data, unconn = GraphBase.path_length_hist(self, directed)
        hist = Histogram(bin_width=1)
        for i, length in enumerate(data):
            hist.add(i + 1, length)
        hist.unconnected = int(unconn)
        return hist

    def pagerank(
        self,
        vertices=None,
        directed=True,
        damping=0.85,
        weights=None,
        arpack_options=None,
        implementation="prpack",
        niter=1000,
        eps=0.001,
    ):
        """Calculates the PageRank values of a graph.

        @param vertices: the indices of the vertices being queried.
          C{None} means all of the vertices.
        @param directed: whether to consider directed paths.
        @param damping: the damping factor. M{1-damping} is the PageRank value
          for nodes with no incoming links. It is also the probability of
          resetting the random walk to a uniform distribution in each step.
        @param weights: edge weights to be used. Can be a sequence or iterable
          or even an edge attribute name.
        @param arpack_options: an L{ARPACKOptions} object used to fine-tune
          the ARPACK eigenvector calculation. If omitted, the module-level
          variable called C{arpack_options} is used. This argument is
          ignored if not the ARPACK implementation is used, see the
          I{implementation} argument.
        @param implementation: which implementation to use to solve the
          PageRank eigenproblem. Possible values are:
            - C{"prpack"}: use the PRPACK library. This is a new
              implementation in igraph 0.7
            - C{"arpack"}: use the ARPACK library. This implementation
              was used from version 0.5, until version 0.7.
            - C{"power"}: use a simple power method. This is the
              implementation that was used before igraph version 0.5.
        @param niter: The number of iterations to use in the power method
          implementation. It is ignored in the other implementations
        @param eps: The power method implementation will consider the
          calculation as complete if the difference of PageRank values between
          iterations change less than this value for every node. It is
          ignored by the other implementations.
        @return: a list with the Google PageRank values of the specified
          vertices."""
        if arpack_options is None:
            arpack_options = default_arpack_options
        return self.personalized_pagerank(
            vertices,
            directed,
            damping,
            None,
            None,
            weights,
            arpack_options,
            implementation,
            niter,
            eps,
        )

    def spanning_tree(self, weights=None, return_tree=True):
        """Calculates a minimum spanning tree for a graph.

        @param weights: a vector containing weights for every edge in
          the graph. C{None} means that the graph is unweighted.
        @param return_tree: whether to return the minimum spanning tree (when
          C{return_tree} is C{True}) or to return the IDs of the edges in
          the minimum spanning tree instead (when C{return_tree} is C{False}).
          The default is C{True} for historical reasons as this argument was
          introduced in igraph 0.6.
        @return: the spanning tree as a L{Graph} object if C{return_tree}
          is C{True} or the IDs of the edges that constitute the spanning
          tree if C{return_tree} is C{False}.

        @newfield ref: Reference
        @ref: Prim, R.C.: I{Shortest connection networks and some
          generalizations}. Bell System Technical Journal 36:1389-1401, 1957.
        """
        result = GraphBase._spanning_tree(self, weights)
        if return_tree:
            return self.subgraph_edges(result, delete_vertices=False)
        return result

    def transitivity_avglocal_undirected(self, mode="nan", weights=None):
        """Calculates the average of the vertex transitivities of the graph.

        In the unweighted case, the transitivity measures the probability that
        two neighbors of a vertex are connected. In case of the average local
        transitivity, this probability is calculated for each vertex and then
        the average is taken. Vertices with less than two neighbors require
        special treatment, they will either be left out from the calculation
        or they will be considered as having zero transitivity, depending on
        the I{mode} parameter. The calculation is slightly more involved for
        weighted graphs; in this case, weights are taken into account according
        to the formula of Barrat et al (see the references).

        Note that this measure is different from the global transitivity
        measure (see L{transitivity_undirected()}) as it simply takes the
        average local transitivity across the whole network.

        @param mode: defines how to treat vertices with degree less than two.
          If C{TRANSITIVITY_ZERO} or C{"zero"}, these vertices will have zero
          transitivity. If C{TRANSITIVITY_NAN} or C{"nan"}, these vertices
          will be excluded from the average.
        @param weights: edge weights to be used. Can be a sequence or iterable
          or even an edge attribute name.

        @see: L{transitivity_undirected()}, L{transitivity_local_undirected()}
        @newfield ref: Reference
        @ref: Watts DJ and Strogatz S: I{Collective dynamics of small-world
          networks}. Nature 393(6884):440-442, 1998.
        @ref: Barrat A, Barthelemy M, Pastor-Satorras R and Vespignani A:
          I{The architecture of complex weighted networks}. PNAS 101, 3747 (2004).
          U{http://arxiv.org/abs/cond-mat/0311416}.
        """
        if weights is None:
            return GraphBase.transitivity_avglocal_undirected(self, mode)

        xs = self.transitivity_local_undirected(mode=mode, weights=weights)
        return sum(xs) / float(len(xs))

    def triad_census(self, *args, **kwds):
        """Calculates the triad census of the graph.

        @return: a L{TriadCensus} object.
        @newfield ref: Reference
        @ref: Davis, J.A. and Leinhardt, S.  (1972).  The Structure of
          Positive Interpersonal Relations in Small Groups.  In:
          J. Berger (Ed.), Sociological Theories in Progress, Volume 2,
          218-251. Boston: Houghton Mifflin.
        """
        return TriadCensus(GraphBase.triad_census(self, *args, **kwds))

    # Automorphisms
    def count_automorphisms_vf2(
        self, color=None, edge_color=None, node_compat_fn=None, edge_compat_fn=None
    ):
        """Returns the number of automorphisms of the graph.

        This function simply calls C{count_isomorphisms_vf2} with the graph
        itself. See C{count_isomorphisms_vf2} for an explanation of the
        parameters.

        @return: the number of automorphisms of the graph
        @see: Graph.count_isomorphisms_vf2
        """
        return self.count_isomorphisms_vf2(
            self,
            color1=color,
            color2=color,
            edge_color1=edge_color,
            edge_color2=edge_color,
            node_compat_fn=node_compat_fn,
            edge_compat_fn=edge_compat_fn,
        )

    def get_automorphisms_vf2(
        self, color=None, edge_color=None, node_compat_fn=None, edge_compat_fn=None
    ):
        """Returns all the automorphisms of the graph

        This function simply calls C{get_isomorphisms_vf2} with the graph
        itself. See C{get_isomorphisms_vf2} for an explanation of the
        parameters.

        @return: a list of lists, each item containing a possible mapping
          of the graph vertices to itself according to the automorphism
        @see: Graph.get_isomorphisms_vf2
        """
        return self.get_isomorphisms_vf2(
            self,
            color1=color,
            color2=color,
            edge_color1=edge_color,
            edge_color2=edge_color,
            node_compat_fn=node_compat_fn,
            edge_compat_fn=edge_compat_fn,
        )

    # Various clustering algorithms -- mostly wrappers around GraphBase
    community_fastgreedy = _community_fastgreedy

    community_infomap = _community_infomap

    community_leading_eigenvector_naive = _community_leading_eigenvector_naive

    community_leading_eigenvector = _community_leading_eigenvector

    community_label_propagation = _community_label_propagation

    community_multilevel = _community_multilevel

    community_optimal_modularity = _community_optimal_modularity

    community_edge_betweenness = _community_edge_betweenness

    community_spinglass = _community_spinglass

    community_walktrap = _community_walktrap

    k_core = _k_core

    community_leiden = _community_leiden

    def layout(self, layout=None, *args, **kwds):
        """Returns the layout of the graph according to a layout algorithm.

        Parameters and keyword arguments not specified here are passed to the
        layout algorithm directly. See the documentation of the layout
        algorithms for the explanation of these parameters.

        Registered layout names understood by this method are:

          - C{auto}, C{automatic}: automatic layout
            (see L{layout_auto})

          - C{bipartite}: bipartite layout (see L{layout_bipartite})

          - C{circle}, C{circular}: circular layout
            (see L{layout_circle})

          - C{dh}, C{davidson_harel}: Davidson-Harel layout (see
            L{layout_davidson_harel})

          - C{drl}: DrL layout for large graphs (see L{layout_drl})

          - C{drl_3d}: 3D DrL layout for large graphs
            (see L{layout_drl})

          - C{fr}, C{fruchterman_reingold}: Fruchterman-Reingold layout
            (see L{layout_fruchterman_reingold}).

          - C{fr_3d}, C{fr3d}, C{fruchterman_reingold_3d}: 3D Fruchterman-
            Reingold layout (see L{layout_fruchterman_reingold}).

          - C{grid}: regular grid layout in 2D (see L{layout_grid})

          - C{grid_3d}: regular grid layout in 3D (see L{layout_grid_3d})

          - C{graphopt}: the graphopt algorithm (see L{layout_graphopt})

          - C{kk}, C{kamada_kawai}: Kamada-Kawai layout
            (see L{layout_kamada_kawai})

          - C{kk_3d}, C{kk3d}, C{kamada_kawai_3d}: 3D Kamada-Kawai layout
            (see L{layout_kamada_kawai})

          - C{lgl}, C{large}, C{large_graph}: Large Graph Layout
            (see L{layout_lgl})

          - C{mds}: multidimensional scaling layout (see L{layout_mds})

          - C{random}: random layout (see L{layout_random})

          - C{random_3d}: random 3D layout (see L{layout_random})

          - C{rt}, C{tree}, C{reingold_tilford}: Reingold-Tilford tree
            layout (see L{layout_reingold_tilford})

          - C{rt_circular}, C{reingold_tilford_circular}: circular
            Reingold-Tilford tree layout
            (see L{layout_reingold_tilford_circular})

          - C{sphere}, C{spherical}, C{circle_3d}, C{circular_3d}: spherical
            layout (see L{layout_circle})

          - C{star}: star layout (see L{layout_star})

          - C{sugiyama}: Sugiyama layout (see L{layout_sugiyama})

        @param layout: the layout to use. This can be one of the registered
          layout names or a callable which returns either a L{Layout} object or
          a list of lists containing the coordinates. If C{None}, uses the
          value of the C{plotting.layout} configuration key.
        @return: a L{Layout} object.
        """
        if layout is None:
            layout = config["plotting.layout"]
        if hasattr(layout, "__call__"):
            method = layout
        else:
            layout = layout.lower()
            if layout[-3:] == "_3d":
                kwds["dim"] = 3
                layout = layout[:-3]
            elif layout[-2:] == "3d":
                kwds["dim"] = 3
                layout = layout[:-2]
            method = getattr(self.__class__, self._layout_mapping[layout])
        if not hasattr(method, "__call__"):
            raise ValueError("layout method must be callable")
        layout = method(self, *args, **kwds)
        if not isinstance(layout, Layout):
            layout = Layout(layout)
        return layout

    def layout_auto(self, *args, **kwds):
        """Chooses and runs a suitable layout function based on simple
        topological properties of the graph.

        This function tries to choose an appropriate layout function for
        the graph using the following rules:

          1. If the graph has an attribute called C{layout}, it will be
             used. It may either be a L{Layout} instance, a list of
             coordinate pairs, the name of a layout function, or a
             callable function which generates the layout when called
             with the graph as a parameter.

          2. Otherwise, if the graph has vertex attributes called C{x}
             and C{y}, these will be used as coordinates in the layout.
             When a 3D layout is requested (by setting C{dim} to 3),
             a vertex attribute named C{z} will also be needed.

          3. Otherwise, if the graph is connected and has at most 100
             vertices, the Kamada-Kawai layout will be used (see
             L{layout_kamada_kawai()}).

          4. Otherwise, if the graph has at most 1000 vertices, the
             Fruchterman-Reingold layout will be used (see
             L{layout_fruchterman_reingold()}).

          5. If everything else above failed, the DrL layout algorithm
             will be used (see L{layout_drl()}).

        All the arguments of this function except C{dim} are passed on
        to the chosen layout function (in case we have to call some layout
        function).

        @keyword dim: specifies whether we would like to obtain a 2D or a
          3D layout.
        @return: a L{Layout} object.
        """
        if "layout" in self.attributes():
            layout = self["layout"]
            if isinstance(layout, Layout):
                # Layouts are used intact
                return layout
            if isinstance(layout, (list, tuple)):
                # Lists/tuples are converted to layouts
                return Layout(layout)
            if hasattr(layout, "__call__"):
                # Callables are called
                return Layout(layout(*args, **kwds))
            # Try Graph.layout()
            return self.layout(layout, *args, **kwds)

        dim = kwds.get("dim", 2)
        vattrs = self.vertex_attributes()
        if "x" in vattrs and "y" in vattrs:
            if dim == 3 and "z" in vattrs:
                return Layout(list(zip(self.vs["x"], self.vs["y"], self.vs["z"])))
            else:
                return Layout(list(zip(self.vs["x"], self.vs["y"])))

        if self.vcount() <= 100 and self.is_connected():
            algo = "kk"
        elif self.vcount() <= 1000:
            algo = "fr"
        else:
            algo = "drl"
        return self.layout(algo, *args, **kwds)

    def layout_sugiyama(
        self,
        layers=None,
        weights=None,
        hgap=1,
        vgap=1,
        maxiter=100,
        return_extended_graph=False,
    ):
        """Places the vertices using a layered Sugiyama layout.

        This is a layered layout that is most suitable for directed acyclic graphs,
        although it works on undirected or cyclic graphs as well.

        Each vertex is assigned to a layer and each layer is placed on a horizontal
        line. Vertices within the same layer are then permuted using the barycenter
        heuristic that tries to minimize edge crossings.

        Dummy vertices will be added on edges that span more than one layer. The
        returned layout therefore contains more rows than the number of nodes in
        the original graph; the extra rows correspond to the dummy vertices.

        @param layers: a vector specifying a non-negative integer layer index for
          each vertex, or the name of a numeric vertex attribute that contains
          the layer indices. If C{None}, a layering will be determined
          automatically. For undirected graphs, a spanning tree will be extracted
          and vertices will be assigned to layers using a breadth first search from
          the node with the largest degree. For directed graphs, cycles are broken
          by reversing the direction of edges in an approximate feedback arc set
          using the heuristic of Eades, Lin and Smyth, and then using longest path
          layering to place the vertices in layers.
        @param weights: edge weights to be used. Can be a sequence or iterable or
          even an edge attribute name.
        @param hgap: minimum horizontal gap between vertices in the same layer.
        @param vgap: vertical gap between layers. The layer index will be
          multiplied by I{vgap} to obtain the Y coordinate.
        @param maxiter: maximum number of iterations to take in the crossing
          reduction step. Increase this if you feel that you are getting too many
          edge crossings.
        @param return_extended_graph: specifies that the extended graph with the
          added dummy vertices should also be returned. When this is C{True}, the
          result will be a tuple containing the layout and the extended graph. The
          first |V| nodes of the extended graph will correspond to the nodes of the
          original graph, the remaining ones are dummy nodes. Plotting the extended
          graph with the returned layout and hidden dummy nodes will produce a layout
          that is similar to the original graph, but with the added edge bends.
          The extended graph also contains an edge attribute called C{_original_eid}
          which specifies the ID of the edge in the original graph from which the
          edge of the extended graph was created.
        @return: the calculated layout, which may (and usually will) have more rows
          than the number of vertices; the remaining rows correspond to the dummy
          nodes introduced in the layering step. When C{return_extended_graph} is
          C{True}, it will also contain the extended graph.

        @newfield ref: Reference
        @ref: K Sugiyama, S Tagawa, M Toda: Methods for visual understanding of
          hierarchical system structures. IEEE Systems, Man and Cybernetics\
          11(2):109-125, 1981.
        @ref: P Eades, X Lin and WF Smyth: A fast effective heuristic for the
          feedback arc set problem. Information Processing Letters 47:319-323, 1993.
        """
        if not return_extended_graph:
            return Layout(
                GraphBase._layout_sugiyama(
                    self, layers, weights, hgap, vgap, maxiter, return_extended_graph
                )
            )

        layout, extd_graph, extd_to_orig_eids = GraphBase._layout_sugiyama(
            self, layers, weights, hgap, vgap, maxiter, return_extended_graph
        )
        extd_graph.es["_original_eid"] = extd_to_orig_eids
        return Layout(layout), extd_graph

    def maximum_bipartite_matching(self, types="type", weights=None, eps=None):
        """Finds a maximum matching in a bipartite graph.

        A maximum matching is a set of edges such that each vertex is incident on
        at most one matched edge and the number (or weight) of such edges in the
        set is as large as possible.

        @param types: vertex types in a list or the name of a vertex attribute
          holding vertex types. Types should be denoted by zeros and ones (or
          C{False} and C{True}) for the two sides of the bipartite graph.
          If omitted, it defaults to C{type}, which is the default vertex type
          attribute for bipartite graphs.
        @param weights: edge weights to be used. Can be a sequence or iterable or
          even an edge attribute name.
        @param eps: a small real number used in equality tests in the weighted
          bipartite matching algorithm. Two real numbers are considered equal in
          the algorithm if their difference is smaller than this value. This
          is required to avoid the accumulation of numerical errors. If you
          pass C{None} here, igraph will try to determine an appropriate value
          automatically.
        @return: an instance of L{Matching}."""
        if eps is None:
            eps = -1

        matches = GraphBase._maximum_bipartite_matching(self, types, weights, eps)
        return Matching(self, matches, types=types)

    #############################################
    # Auxiliary I/O functions

    # Graph libraries
    from_networkx = classmethod(_construct_graph_from_networkx)
    to_networkx = _export_graph_to_networkx

    from_graph_tool = classmethod(_construct_graph_from_graph_tool)
    to_graph_tool = _export_graph_to_graph_tool

    # Files
    Read_DIMACS = classmethod(_construct_graph_from_dimacs_file)
    write_dimacs = _write_graph_to_dimacs_file

    Read_GraphMLz = classmethod(_construct_graph_from_graphmlz_file)
    write_graphmlz = _write_graph_to_graphmlz_file

    Read_Pickle = classmethod(_construct_graph_from_pickle_file)
    write_pickle = _write_graph_to_pickle_file

    Read_Picklez = classmethod(_construct_graph_from_picklez_file)
    write_picklez = _write_graph_to_picklez_file

    Read_Adjacency = classmethod(_construct_graph_from_adjacency_file)
    write_adjacency = _write_graph_to_adjacency_file

    Read = classmethod(_construct_graph_from_file)
    Load = Read
    write = _write_graph_to_file
    save = write

    # Various objects
    # list of dict representation of graphs
    DictList = classmethod(_construct_graph_from_dict_list)
    to_dict_list = _export_graph_to_dict_list

    # tuple-like representation of graphs
    TupleList = classmethod(_construct_graph_from_tuple_list)
    to_tuple_list = _export_graph_to_tuple_list

    # dict of sequence representation of graphs
    ListDict = classmethod(_construct_graph_from_list_dict)
    to_list_dict = _export_graph_to_list_dict

    # dict of dicts representation of graphs
    DictDict = classmethod(_construct_graph_from_dict_dict)
    to_dict_dict = _export_graph_to_dict_dict

    # adjacency matrix
    Adjacency = classmethod(_construct_graph_from_adjacency)

    Weighted_Adjacency = classmethod(_construct_graph_from_weighted_adjacency)

    # pandas dataframe(s)
    DataFrame = classmethod(_construct_graph_from_dataframe)

    get_vertex_dataframe = _export_vertex_dataframe

    get_edge_dataframe = _export_edge_dataframe

    # Bipartite graphs
    Bipartite = classmethod(_construct_bipartite_graph)

    Incidence = classmethod(_construct_incidence_bipartite_graph)

    Full_Bipartite = classmethod(_construct_full_bipartite_graph)

    Random_Bipartite = classmethod(_construct_random_bipartite_graph)

    # Other constructors
    GRG = classmethod(_construct_random_geometric_graph)

    # Graph formulae
    Formula = classmethod(construct_graph_from_formula)

    ###########################
    # Vertex and edge sequence

    @property
    def vs(self):
        """The vertex sequence of the graph"""
        return VertexSeq(self)

    @property
    def es(self):
        """The edge sequence of the graph"""
        return EdgeSeq(self)

    def bipartite_projection(
        self, types="type", multiplicity=True, probe1=-1, which="both"
    ):
        """Projects a bipartite graph into two one-mode graphs. Edge directions
        are ignored while projecting.

        Examples:

        >>> g = Graph.Full_Bipartite(10, 5)
        >>> g1, g2 = g.bipartite_projection()
        >>> g1.isomorphic(Graph.Full(10))
        True
        >>> g2.isomorphic(Graph.Full(5))
        True

        @param types: an igraph vector containing the vertex types, or an
          attribute name. Anything that evalulates to C{False} corresponds to
          vertices of the first kind, everything else to the second kind.
        @param multiplicity: if C{True}, then igraph keeps the multiplicity of
          the edges in the projection in an edge attribute called C{"weight"}.
          E.g., if there is an A-C-B and an A-D-B triplet in the bipartite
          graph and there is no other X (apart from X=B and X=D) for which an
          A-X-B triplet would exist in the bipartite graph, the multiplicity
          of the A-B edge in the projection will be 2.
        @param probe1: this argument can be used to specify the order of the
          projections in the resulting list. If given and non-negative, then
          it is considered as a vertex ID; the projection containing the
          vertex will be the first one in the result.
        @param which: this argument can be used to specify which of the two
          projections should be returned if only one of them is needed. Passing
          0 here means that only the first projection is returned, while 1 means
          that only the second projection is returned. (Note that we use 0 and 1
          because Python indexing is zero-based). C{False} is equivalent to 0 and
          C{True} is equivalent to 1. Any other value means that both projections
          will be returned in a tuple.
        @return: a tuple containing the two projected one-mode graphs if C{which}
          is not 1 or 2, or the projected one-mode graph specified by the
          C{which} argument if its value is 0, 1, C{False} or C{True}.
        """
        superclass_meth = super().bipartite_projection

        if which is False:
            which = 0
        elif which is True:
            which = 1
        if which != 0 and which != 1:
            which = -1

        if multiplicity:
            if which == 0:
                g1, w1 = superclass_meth(types, True, probe1, which)
                g2, w2 = None, None
            elif which == 1:
                g1, w1 = None, None
                g2, w2 = superclass_meth(types, True, probe1, which)
            else:
                g1, g2, w1, w2 = superclass_meth(types, True, probe1, which)

            if g1 is not None:
                g1.es["weight"] = w1
                if g2 is not None:
                    g2.es["weight"] = w2
                    return g1, g2
                else:
                    return g1
            else:
                g2.es["weight"] = w2
                return g2
        else:
            return superclass_meth(types, False, probe1, which)

    def bipartite_projection_size(self, types="type", *args, **kwds):
        """Calculates the number of vertices and edges in the bipartite
        projections of this graph according to the specified vertex types.
        This is useful if you have a bipartite graph and you want to estimate
        the amount of memory you would need to calculate the projections
        themselves.

        @param types: an igraph vector containing the vertex types, or an
          attribute name. Anything that evalulates to C{False} corresponds to
          vertices of the first kind, everything else to the second kind.
        @return: a 4-tuple containing the number of vertices and edges in the
          first projection, followed by the number of vertices and edges in the
          second projection.
        """
        return super().bipartite_projection_size(types, *args, **kwds)

    def get_incidence(self, types="type", *args, **kwds):
        """Returns the incidence matrix of a bipartite graph. The incidence matrix
        is an M{n} times M{m} matrix, where M{n} and M{m} are the number of
        vertices in the two vertex classes.

        @param types: an igraph vector containing the vertex types, or an
          attribute name. Anything that evalulates to C{False} corresponds to
          vertices of the first kind, everything else to the second kind.
        @return: the incidence matrix and two lists in a triplet. The first
          list defines the mapping between row indices of the matrix and the
          original vertex IDs. The second list is the same for the column
          indices.
        """
        return super().get_incidence(types, *args, **kwds)

    ###########################
    # DFS (C version will come soon)
    def dfs(self, vid, mode=OUT):
        """Conducts a depth first search (DFS) on the graph.

        @param vid: the root vertex ID
        @param mode: either C{\"in\"} or C{\"out\"} or C{\"all\"}, ignored
          for undirected graphs.
        @return: a tuple with the following items:
           - The vertex IDs visited (in order)
           - The parent of every vertex in the DFS
        """
        nv = self.vcount()
        added = [False for v in range(nv)]
        stack = []

        # prepare output
        vids = []
        parents = []

        # ok start from vid
        stack.append((vid, self.neighbors(vid, mode=mode)))
        vids.append(vid)
        parents.append(vid)
        added[vid] = True

        # go down the rabbit hole
        while stack:
            vid, neighbors = stack[-1]
            if neighbors:
                # Get next neighbor to visit
                neighbor = neighbors.pop()
                if not added[neighbor]:
                    # Add hanging subtree neighbor
                    stack.append((neighbor, self.neighbors(neighbor, mode=mode)))
                    vids.append(neighbor)
                    parents.append(vid)
                    added[neighbor] = True
            else:
                # No neighbor found, end of subtree
                stack.pop()

        return (vids, parents)

    ###########################
    # ctypes support

    @property
    def _as_parameter_(self):
        return self._raw_pointer()

    ###################
    # Custom operators
    __iadd__ = _operator_method_registry['__iadd__']

    __add__ = _operator_method_registry['__add__']

    __and__ = _operator_method_registry['__and__']

    __isub__ = _operator_method_registry['__isub__']

    __sub__ = _operator_method_registry['__sub__']

    __mul__ = _operator_method_registry['__mul__']

    __or__ = _operator_method_registry['__or__']

    def __bool__(self):
        """Returns True if the graph has at least one vertex, False otherwise."""
        return self.vcount() > 0

    def __coerce__(self, other):
        """Coercion rules.

        This method is needed to allow the graph to react to additions
        with lists, tuples, integers, strings, vertices, edges and so on.
        """
        if isinstance(other, (int, tuple, list, str)):
            return self, other
        if isinstance(other, Vertex):
            return self, other
        if isinstance(other, VertexSeq):
            return self, other
        if isinstance(other, Edge):
            return self, other
        if isinstance(other, EdgeSeq):
            return self, other
        return NotImplemented

    @classmethod
    def _reconstruct(cls, attrs, *args, **kwds):
        """Reconstructs a Graph object from Python's pickled format.

        This method is for internal use only, it should not be called
        directly."""
        result = cls(*args, **kwds)
        result.__dict__.update(attrs)
        return result

    def __reduce__(self):
        """Support for pickling."""
        constructor = self.__class__
        gattrs, vattrs, eattrs = {}, {}, {}
        for attr in self.attributes():
            gattrs[attr] = self[attr]
        for attr in self.vs.attribute_names():
            vattrs[attr] = self.vs[attr]
        for attr in self.es.attribute_names():
            eattrs[attr] = self.es[attr]
        parameters = (
            self.vcount(),
            self.get_edgelist(),
            self.is_directed(),
            gattrs,
            vattrs,
            eattrs,
        )
        return (constructor, parameters, self.__dict__)

    __iter__ = None  # needed for PyPy
    __hash__ = None  # needed for PyPy

    __plot__ = _graph_plot

    def __str__(self):
        """Returns a string representation of the graph.

        Behind the scenes, this method constructs a L{GraphSummary}
        instance and invokes its C{__str__} method with a verbosity of 1
        and attribute printing turned off.

        See the documentation of L{GraphSummary} for more details about the
        output.
        """
        params = dict(
            verbosity=1,
            width=78,
            print_graph_attributes=False,
            print_vertex_attributes=False,
            print_edge_attributes=False,
        )
        return self.summary(**params)

    def summary(self, verbosity=0, width=None, *args, **kwds):
        """Returns the summary of the graph.

        The output of this method is similar to the output of the
        C{__str__} method. If I{verbosity} is zero, only the header line
        is returned (see C{__str__} for more details), otherwise the
        header line and the edge list is printed.

        Behind the scenes, this method constructs a L{GraphSummary}
        object and invokes its C{__str__} method.

        @param verbosity: if zero, only the header line is returned
          (see C{__str__} for more details), otherwise the header line
          and the full edge list is printed.
        @param width: the number of characters to use in one line.
          If C{None}, no limit will be enforced on the line lengths.
        @return: the summary of the graph.
        """
        return str(GraphSummary(self, verbosity, width, *args, **kwds))

    def disjoint_union(self, other):
        """Creates the disjoint union of two (or more) graphs.

        @param other: graph or list of graphs to be united with the current one.
        @return: the disjoint union graph
        """
        if isinstance(other, GraphBase):
            other = [other]
        return disjoint_union([self] + other)

    def union(self, other, byname="auto"):
        """Creates the union of two (or more) graphs.

        @param other: graph or list of graphs to be united with the current one.
        @param byname: whether to use vertex names instead of ids. See
          L{igraph.union} for details.
        @return: the union graph
        """
        if isinstance(other, GraphBase):
            other = [other]
        return union([self] + other, byname=byname)

    def intersection(self, other, byname="auto"):
        """Creates the intersection of two (or more) graphs.

        @param other: graph or list of graphs to be intersected with
          the current one.
        @param byname: whether to use vertex names instead of ids. See
          L{igraph.intersection} for details.
        @return: the intersection graph
        """
        if isinstance(other, GraphBase):
            other = [other]
        return intersection([self] + other, byname=byname)

    _format_mapping = {
        "ncol": ("Read_Ncol", "write_ncol"),
        "lgl": ("Read_Lgl", "write_lgl"),
        "graphdb": ("Read_GraphDB", None),
        "graphmlz": ("Read_GraphMLz", "write_graphmlz"),
        "graphml": ("Read_GraphML", "write_graphml"),
        "gml": ("Read_GML", "write_gml"),
        "dot": (None, "write_dot"),
        "graphviz": (None, "write_dot"),
        "net": ("Read_Pajek", "write_pajek"),
        "pajek": ("Read_Pajek", "write_pajek"),
        "dimacs": ("Read_DIMACS", "write_dimacs"),
        "adjacency": ("Read_Adjacency", "write_adjacency"),
        "adj": ("Read_Adjacency", "write_adjacency"),
        "edgelist": ("Read_Edgelist", "write_edgelist"),
        "edge": ("Read_Edgelist", "write_edgelist"),
        "edges": ("Read_Edgelist", "write_edgelist"),
        "pickle": ("Read_Pickle", "write_pickle"),
        "picklez": ("Read_Picklez", "write_picklez"),
        "svg": (None, "write_svg"),
        "gw": (None, "write_leda"),
        "leda": (None, "write_leda"),
        "lgr": (None, "write_leda"),
        "dl": ("Read_DL", None),
    }

    _layout_mapping = {
        "auto": "layout_auto",
        "automatic": "layout_auto",
        "bipartite": "layout_bipartite",
        "circle": "layout_circle",
        "circular": "layout_circle",
        "davidson_harel": "layout_davidson_harel",
        "dh": "layout_davidson_harel",
        "drl": "layout_drl",
        "fr": "layout_fruchterman_reingold",
        "fruchterman_reingold": "layout_fruchterman_reingold",
        "graphopt": "layout_graphopt",
        "grid": "layout_grid",
        "kk": "layout_kamada_kawai",
        "kamada_kawai": "layout_kamada_kawai",
        "lgl": "layout_lgl",
        "large": "layout_lgl",
        "large_graph": "layout_lgl",
        "mds": "layout_mds",
        "random": "layout_random",
        "rt": "layout_reingold_tilford",
        "tree": "layout_reingold_tilford",
        "reingold_tilford": "layout_reingold_tilford",
        "rt_circular": "layout_reingold_tilford_circular",
        "reingold_tilford_circular": "layout_reingold_tilford_circular",
        "sphere": "layout_sphere",
        "spherical": "layout_sphere",
        "star": "layout_star",
        "sugiyama": "layout_sugiyama",
    }

    # After adjusting something here, don't forget to update the docstring
    # of Graph.layout if necessary!


##############################################################
# Additional methods of VertexSeq and EdgeSeq that call Graph methods


def _graphmethod(func=None, name=None):
    """Auxiliary decorator

    This decorator allows some methods of L{VertexSeq} and L{EdgeSeq} to
    call their respective counterparts in L{Graph} to avoid code duplication.

    @param func: the function being decorated. This function will be
      called on the results of the original L{Graph} method.
      If C{None}, defaults to the identity function.
    @param name: the name of the corresponding method in L{Graph}. If
      C{None}, it defaults to the name of the decorated function.
    @return: the decorated function
    """
    if name is None:
        name = func.__name__
    method = getattr(Graph, name)

    if hasattr(func, "__call__"):

        def decorated(*args, **kwds):
            self = args[0].graph
            return func(args[0], method(self, *args, **kwds))

    else:

        def decorated(*args, **kwds):
            self = args[0].graph
            return method(self, *args, **kwds)

    decorated.__name__ = name
    decorated.__doc__ = """Proxy method to L{Graph.%(name)s()}

This method calls the C{%(name)s()} method of the L{Graph} class
restricted to this sequence, and returns the result.

@see: Graph.%(name)s() for details.
""" % {
        "name": name
    }

    return decorated


def _add_proxy_methods():

    # Proxy methods for VertexSeq and EdgeSeq that forward their arguments to
    # the corresponding Graph method are constructed here. Proxy methods for
    # Vertex and Edge are added in the C source code. Make sure that you update
    # the C source whenever you add a proxy method here if that makes sense for
    # an individual vertex or edge
    decorated_methods = {}
    decorated_methods[VertexSeq] = [
        "degree",
        "betweenness",
        "bibcoupling",
        "closeness",
        "cocitation",
        "constraint",
        "diversity",
        "eccentricity",
        "get_shortest_paths",
        "maxdegree",
        "pagerank",
        "personalized_pagerank",
        "shortest_paths",
        "similarity_dice",
        "similarity_jaccard",
        "subgraph",
        "indegree",
        "outdegree",
        "isoclass",
        "delete_vertices",
        "is_separator",
        "is_minimal_separator",
    ]
    decorated_methods[EdgeSeq] = [
        "count_multiple",
        "delete_edges",
        "is_loop",
        "is_multiple",
        "is_mutual",
        "subgraph_edges",
    ]

    rename_methods = {}
    rename_methods[VertexSeq] = {"delete_vertices": "delete"}
    rename_methods[EdgeSeq] = {"delete_edges": "delete", "subgraph_edges": "subgraph"}

    for cls, methods in decorated_methods.items():
        for method in methods:
            new_method_name = rename_methods[cls].get(method, method)
            setattr(cls, new_method_name, _graphmethod(None, method))

    setattr(
        EdgeSeq,
        "edge_betweenness",
        _graphmethod(
            lambda self, result: [result[i] for i in self.indices], "edge_betweenness"
        ),
    )


_add_proxy_methods()

##############################################################
# Making sure that layout methods always return a Layout


def _layout_method_wrapper(func):
    """Wraps an existing layout method to ensure that it returns a Layout
    instead of a list of lists.

    @param func: the method to wrap. Must be a method of the Graph object.
    @return: a new method
    """

    def result(*args, **kwds):
        layout = func(*args, **kwds)
        if not isinstance(layout, Layout):
            layout = Layout(layout)
        return layout

    result.__name__ = func.__name__
    result.__doc__ = func.__doc__
    return result


for name in dir(Graph):
    if not name.startswith("layout_"):
        continue
    if name in ("layout_auto", "layout_sugiyama"):
        continue
    setattr(Graph, name, _layout_method_wrapper(getattr(Graph, name)))

##############################################################
# Adding aliases for the 3D versions of the layout methods


def _3d_version_for(func):
    """Creates an alias for the 3D version of the given layout algoritm.

    This function is a decorator that creates a method which calls I{func} after
    attaching C{dim=3} to the list of keyword arguments.

    @param func: must be a method of the Graph object.
    @return: a new method
    """

    def result(*args, **kwds):
        kwds["dim"] = 3
        return func(*args, **kwds)

    result.__name__ = "%s_3d" % func.__name__
    result.__doc__ = """Alias for L{%s()} with dim=3.\n\n@see: Graph.%s()""" % (
        func.__name__,
        func.__name__,
    )
    return result


Graph.layout_fruchterman_reingold_3d = _3d_version_for(
    Graph.layout_fruchterman_reingold
)
Graph.layout_kamada_kawai_3d = _3d_version_for(Graph.layout_kamada_kawai)
Graph.layout_random_3d = _3d_version_for(Graph.layout_random)
Graph.layout_grid_3d = _3d_version_for(Graph.layout_grid)
Graph.layout_sphere = _3d_version_for(Graph.layout_circle)

##############################################################


def get_include():
    """Returns the folder that contains the C API headers of the Python
    interface of igraph."""
    import igraph

    paths = [
        # The following path works if python-igraph is installed already
        os.path.join(
            sys.prefix,
            "include",
            "python{0}.{1}".format(*sys.version_info),
            "python-igraph",
        ),
        # Fallback for cases when python-igraph is not installed but
        # imported directly from the source tree
        os.path.join(os.path.dirname(igraph.__file__), "..", "src"),
    ]
    for path in paths:
        if os.path.exists(os.path.join(path, "igraphmodule_api.h")):
            return os.path.abspath(path)
    raise ValueError("cannot find the header files of python-igraph")


def read(filename, *args, **kwds):
    """Loads a graph from the given filename.

    This is just a convenience function, calls L{Graph.Read} directly.
    All arguments are passed unchanged to L{Graph.Read}

    @param filename: the name of the file to be loaded
    """
    return Graph.Read(filename, *args, **kwds)


load = read


def write(graph, filename, *args, **kwds):
    """Saves a graph to the given file.

    This is just a convenience function, calls L{Graph.write} directly.
    All arguments are passed unchanged to L{Graph.write}

    @param graph: the graph to be saved
    @param filename: the name of the file to be written
    """
    return graph.write(filename, *args, **kwds)


save = write


config = init_configuration()

# Remove modular methods from namespace
del (
    construct_graph_from_formula,
    _construct_graph_from_graphmlz_file,
    _construct_graph_from_dimacs_file,
    _construct_graph_from_pickle_file,
    _construct_graph_from_picklez_file,
    _construct_graph_from_adjacency_file,
    _construct_graph_from_file,
    _construct_graph_from_dict_list,
    _construct_graph_from_tuple_list,
    _construct_graph_from_list_dict,
    _construct_graph_from_dict_dict,
    _construct_graph_from_adjacency,
    _construct_graph_from_weighted_adjacency,
    _construct_graph_from_dataframe,
    _construct_random_geometric_graph,
    _construct_bipartite_graph,
    _construct_incidence_bipartite_graph,
    _construct_full_bipartite_graph,
    _construct_random_bipartite_graph,
    _construct_graph_from_networkx,
    _export_graph_to_networkx,
    _construct_graph_from_graph_tool,
    _export_graph_to_graph_tool,
    _export_graph_to_list_dict,
    _export_graph_to_dict_dict,
    _export_graph_to_dict_list,
    _export_graph_to_tuple_list,
    _community_fastgreedy,
    _community_infomap,
    _community_leading_eigenvector_naive,
    _community_leading_eigenvector,
    _community_label_propagation,
    _community_multilevel,
    _community_optimal_modularity,
    _community_edge_betweenness,
    _community_spinglass,
    _community_walktrap,
    _k_core,
    _community_leiden,
    _graph_plot,
    _operator_method_registry,
)
