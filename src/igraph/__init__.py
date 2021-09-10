"""
IGraph library.
"""


__license__ = """
Copyright (C) 2006-2012  Tamás Nepusz <ntamas@gmail.com>
Pázmány Péter sétány 1/a, 1117 Budapest, Hungary

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
    __igraph_version__
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
from igraph.drawing import BoundingBox, DefaultGraphDrawer, Plot, Point, Rectangle, plot
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
from igraph.datatypes import Matrix, DyadCensus, TriadCensus, UniqueIdGenerator
from igraph.formula import construct_graph_from_formula
from igraph.io.files import (
    construct_graph_from_graphmlz_file,
    construct_graph_from_dimacs_file,
    construct_graph_from_pickle_file,
    construct_graph_from_picklez_file,
    construct_graph_from_adjacency_file,
    construct_graph_from_file,
    write_graph_to_adjacency_file,
    write_graph_to_dimacs_file,
    write_graph_to_graphmlz_file,
    write_graph_to_pickle_file,
    write_graph_to_picklez_file,
    write_graph_to_file,

)
from igraph.io.objects import (
    construct_graph_from_dict_list,
    construct_graph_from_tuple_list,
    construct_graph_from_sequence_dict,
    construct_graph_from_dict_dict,
    construct_graph_from_dataframe,
    export_vertex_dataframe,
    export_edge_dataframe,
)
from igraph.io.adjacency import (
    construct_graph_from_adjacency,
    construct_graph_from_weighted_adjacency,
)
from igraph.io.libraries import (
    construct_graph_from_networkx,
    export_graph_to_networkx,
    construct_graph_from_graph_tool,
    export_graph_to_graph_tool,
)
from igraph.io.random import (
    construct_random_geometric_graph,
)
from igraph.io.bipartite import (
    construct_bipartite_graph,
    construct_incidence_bipartite_graph,
    construct_full_bipartite_graph,
    construct_random_bipartite_graph,
)
from igraph.io.images import write_graph_to_svg
from igraph.layout import Layout
from igraph.matching import Matching
from igraph.operators import disjoint_union, union, intersection
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
            raise ImportError(
                "You should install scipy in order to use this function"
            )

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
    def community_fastgreedy(self, weights=None):
        """Community structure based on the greedy optimization of modularity.

        This algorithm merges individual nodes into communities in a way that
        greedily maximizes the modularity score of the graph. It can be proven
        that if no merge can increase the current modularity score, the
        algorithm can be stopped since no further increase can be achieved.

        This algorithm is said to run almost in linear time on sparse graphs.

        @param weights: edge attribute name or a list containing edge
          weights
        @return: an appropriate L{VertexDendrogram} object.

        @newfield ref: Reference
        @ref: A Clauset, MEJ Newman and C Moore: Finding community structure
          in very large networks. Phys Rev E 70, 066111 (2004).
        """
        merges, qs = GraphBase.community_fastgreedy(self, weights)

        # qs may be shorter than |V|-1 if we are left with a few separated
        # communities in the end; take this into account
        diff = self.vcount() - len(qs)
        qs.reverse()
        if qs:
            optimal_count = qs.index(max(qs)) + diff + 1
        else:
            optimal_count = diff

        return VertexDendrogram(
            self, merges, optimal_count, modularity_params=dict(weights=weights)
        )

    def community_infomap(self, edge_weights=None, vertex_weights=None, trials=10):
        """Finds the community structure of the network according to the Infomap
        method of Martin Rosvall and Carl T. Bergstrom.

        @param edge_weights: name of an edge attribute or a list containing
          edge weights.
        @param vertex_weights: name of an vertex attribute or a list containing
          vertex weights.
        @param trials: the number of attempts to partition the network.
        @return: an appropriate L{VertexClustering} object with an extra attribute
          called C{codelength} that stores the code length determined by the
          algorithm.

        @newfield ref: Reference
        @ref: M. Rosvall and C. T. Bergstrom: Maps of information flow reveal
          community structure in complex networks, PNAS 105, 1118 (2008).
          U{http://dx.doi.org/10.1073/pnas.0706851105},
          U{http://arxiv.org/abs/0707.0609}.
        @ref: M. Rosvall, D. Axelsson, and C. T. Bergstrom: The map equation,
          Eur. Phys. J. Special Topics 178, 13 (2009).
          U{http://dx.doi.org/10.1140/epjst/e2010-01179-1},
          U{http://arxiv.org/abs/0906.1405}.
        """
        membership, codelength = GraphBase.community_infomap(
            self, edge_weights, vertex_weights, trials
        )
        return VertexClustering(
            self,
            membership,
            params={"codelength": codelength},
            modularity_params={"weights": edge_weights},
        )

    def community_leading_eigenvector_naive(self, clusters=None, return_merges=False):
        """Naive implementation of Newman's eigenvector community structure detection.

        This function splits the network into two components
        according to the leading eigenvector of the modularity matrix and
        then recursively takes the given number of steps by splitting the
        communities as individual networks. This is not the correct way,
        however, see the reference for explanation. Consider using the
        correct L{community_leading_eigenvector} method instead.

        @param clusters: the desired number of communities. If C{None}, the
          algorithm tries to do as many splits as possible. Note that the
          algorithm won't split a community further if the signs of the leading
          eigenvector are all the same, so the actual number of discovered
          communities can be less than the desired one.
        @param return_merges: whether the returned object should be a
          dendrogram instead of a single clustering.
        @return: an appropriate L{VertexClustering} or L{VertexDendrogram}
          object.

        @newfield ref: Reference
        @ref: MEJ Newman: Finding community structure in networks using the
        eigenvectors of matrices, arXiv:physics/0605087"""
        if clusters is None:
            clusters = -1
        cl, merges, q = GraphBase.community_leading_eigenvector_naive(
            self, clusters, return_merges
        )
        if merges is None:
            return VertexClustering(self, cl, modularity=q)
        else:
            return VertexDendrogram(self, merges, safemax(cl) + 1)

    def community_leading_eigenvector(
        self, clusters=None, weights=None, arpack_options=None
    ):
        """Newman's leading eigenvector method for detecting community structure.

        This is the proper implementation of the recursive, divisive algorithm:
        each split is done by maximizing the modularity regarding the
        original network.

        @param clusters: the desired number of communities. If C{None}, the
          algorithm tries to do as many splits as possible. Note that the
          algorithm won't split a community further if the signs of the leading
          eigenvector are all the same, so the actual number of discovered
          communities can be less than the desired one.
        @param weights: name of an edge attribute or a list containing
          edge weights.
        @param arpack_options: an L{ARPACKOptions} object used to fine-tune
          the ARPACK eigenvector calculation. If omitted, the module-level
          variable called C{arpack_options} is used.
        @return: an appropriate L{VertexClustering} object.

        @newfield ref: Reference
        @ref: MEJ Newman: Finding community structure in networks using the
        eigenvectors of matrices, arXiv:physics/0605087"""
        if clusters is None:
            clusters = -1

        kwds = dict(weights=weights)
        if arpack_options is not None:
            kwds["arpack_options"] = arpack_options

        membership, _, q = GraphBase.community_leading_eigenvector(
            self, clusters, **kwds
        )
        return VertexClustering(self, membership, modularity=q)

    def community_label_propagation(self, weights=None, initial=None, fixed=None):
        """Finds the community structure of the graph according to the label
        propagation method of Raghavan et al.

        Initially, each vertex is assigned a different label. After that,
        each vertex chooses the dominant label in its neighbourhood in each
        iteration. Ties are broken randomly and the order in which the
        vertices are updated is randomized before every iteration. The
        algorithm ends when vertices reach a consensus.
        Note that since ties are broken randomly, there is no guarantee that
        the algorithm returns the same community structure after each run.
        In fact, they frequently differ. See the paper of Raghavan et al
        on how to come up with an aggregated community structure.
        @param weights: name of an edge attribute or a list containing
          edge weights
        @param initial: name of a vertex attribute or a list containing
          the initial vertex labels. Labels are identified by integers from
          zero to M{n-1} where M{n} is the number of vertices. Negative
          numbers may also be present in this vector, they represent unlabeled
          vertices.
        @param fixed: a list of booleans for each vertex. C{True} corresponds
          to vertices whose labeling should not change during the algorithm.
          It only makes sense if initial labels are also given. Unlabeled
          vertices cannot be fixed. It may also be the name of a vertex
          attribute; each attribute value will be interpreted as a Boolean.
        @return: an appropriate L{VertexClustering} object.

        @newfield ref: Reference
        @ref: Raghavan, U.N. and Albert, R. and Kumara, S. Near linear
          time algorithm to detect community structures in large-scale
          networks. Phys Rev E 76:036106, 2007.
          U{http://arxiv.org/abs/0709.2938}.
        """
        if isinstance(fixed, str):
            fixed = [bool(o) for o in self.vs[fixed]]
        cl = GraphBase.community_label_propagation(self, weights, initial, fixed)
        return VertexClustering(self, cl, modularity_params=dict(weights=weights))

    def community_multilevel(self, weights=None, return_levels=False):
        """Community structure based on the multilevel algorithm of
        Blondel et al.

        This is a bottom-up algorithm: initially every vertex belongs to a
        separate community, and vertices are moved between communities
        iteratively in a way that maximizes the vertices' local contribution
        to the overall modularity score. When a consensus is reached (i.e. no
        single move would increase the modularity score), every community in
        the original graph is shrank to a single vertex (while keeping the
        total weight of the adjacent edges) and the process continues on the
        next level. The algorithm stops when it is not possible to increase
        the modularity any more after shrinking the communities to vertices.

        This algorithm is said to run almost in linear time on sparse graphs.

        @param weights: edge attribute name or a list containing edge
          weights
        @param return_levels: if C{True}, the communities at each level are
          returned in a list. If C{False}, only the community structure with
          the best modularity is returned.
        @return: a list of L{VertexClustering} objects, one corresponding to
          each level (if C{return_levels} is C{True}), or a L{VertexClustering}
          corresponding to the best modularity.

        @newfield ref: Reference
        @ref: VD Blondel, J-L Guillaume, R Lambiotte and E Lefebvre: Fast
          unfolding of community hierarchies in large networks, J Stat Mech
          P10008 (2008), http://arxiv.org/abs/0803.0476
        """
        if self.is_directed():
            raise ValueError("input graph must be undirected")

        if return_levels:
            levels, qs = GraphBase.community_multilevel(self, weights, True)
            result = []
            for level, q in zip(levels, qs):
                result.append(
                    VertexClustering(
                        self, level, q, modularity_params=dict(weights=weights)
                    )
                )
        else:
            membership = GraphBase.community_multilevel(self, weights, False)
            result = VertexClustering(
                self, membership, modularity_params=dict(weights=weights)
            )
        return result

    def community_optimal_modularity(self, *args, **kwds):
        """Calculates the optimal modularity score of the graph and the
        corresponding community structure.

        This function uses the GNU Linear Programming Kit to solve a large
        integer optimization problem in order to find the optimal modularity
        score and the corresponding community structure, therefore it is
        unlikely to work for graphs larger than a few (less than a hundred)
        vertices. Consider using one of the heuristic approaches instead if
        you have such a large graph.

        @return: the calculated membership vector and the corresponding
          modularity in a tuple."""
        membership, modularity = GraphBase.community_optimal_modularity(
            self, *args, **kwds
        )
        return VertexClustering(self, membership, modularity)

    def community_edge_betweenness(self, clusters=None, directed=True, weights=None):
        """Community structure based on the betweenness of the edges in the
        network.

        The idea is that the betweenness of the edges connecting two
        communities is typically high, as many of the shortest paths between
        nodes in separate communities go through them. So we gradually remove
        the edge with the highest betweenness and recalculate the betweennesses
        after every removal. This way sooner or later the network falls of to
        separate components. The result of the clustering will be represented
        by a dendrogram.

        @param clusters: the number of clusters we would like to see. This
          practically defines the "level" where we "cut" the dendrogram to
          get the membership vector of the vertices. If C{None}, the dendrogram
          is cut at the level which maximizes the modularity when the graph is
          unweighted; otherwise the dendrogram is cut at at a single cluster
          (because cluster count selection based on modularities does not make
          sense for this method if not all the weights are equal).
        @param directed: whether the directionality of the edges should be
          taken into account or not.
        @param weights: name of an edge attribute or a list containing
          edge weights.
        @return: a L{VertexDendrogram} object, initally cut at the maximum
          modularity or at the desired number of clusters.
        """
        merges, qs = GraphBase.community_edge_betweenness(self, directed, weights)
        if qs is not None:
            qs.reverse()
        if clusters is None:
            if qs:
                clusters = qs.index(max(qs)) + 1
            else:
                clusters = 1
        return VertexDendrogram(
            self, merges, clusters, modularity_params=dict(weights=weights)
        )

    def community_spinglass(self, *args, **kwds):
        """Finds the community structure of the graph according to the
        spinglass community detection method of Reichardt & Bornholdt.

        @param weights: edge weights to be used. Can be a sequence or
          iterable or even an edge attribute name.
        @param spins: integer, the number of spins to use. This is the
          upper limit for the number of communities. It is not a problem
          to supply a (reasonably) big number here, in which case some
          spin states will be unpopulated.
        @param parupdate: whether to update the spins of the vertices in
          parallel (synchronously) or not
        @param start_temp: the starting temperature
        @param stop_temp: the stop temperature
        @param cool_fact: cooling factor for the simulated annealing
        @param update_rule: specifies the null model of the simulation.
          Possible values are C{"config"} (a random graph with the same
          vertex degrees as the input graph) or C{"simple"} (a random
          graph with the same number of edges)
        @param gamma: the gamma argument of the algorithm, specifying the
          balance between the importance of present and missing edges
          within a community. The default value of 1.0 assigns equal
          importance to both of them.
        @param implementation: currently igraph contains two implementations
          of the spinglass community detection algorithm. The faster
          original implementation is the default. The other implementation
          is able to take into account negative weights, this can be
          chosen by setting C{implementation} to C{"neg"}
        @param lambda_: the lambda argument of the algorithm, which
          specifies the balance between the importance of present and missing
          negatively weighted edges within a community. Smaller values of
          lambda lead to communities with less negative intra-connectivity.
          If the argument is zero, the algorithm reduces to a graph coloring
          algorithm, using the number of spins as colors. This argument is
          ignored if the original implementation is used. Note the underscore
          at the end of the argument name; this is due to the fact that
          lambda is a reserved keyword in Python.
        @return: an appropriate L{VertexClustering} object.

        @newfield ref: Reference
        @ref: Reichardt J and Bornholdt S: Statistical mechanics of
          community detection. Phys Rev E 74:016110 (2006).
          U{http://arxiv.org/abs/cond-mat/0603718}.
        @ref: Traag VA and Bruggeman J: Community detection in networks
          with positive and negative links. Phys Rev E 80:036115 (2009).
          U{http://arxiv.org/abs/0811.2329}.
        """
        membership = GraphBase.community_spinglass(self, *args, **kwds)
        if "weights" in kwds:
            modularity_params = dict(weights=kwds["weights"])
        else:
            modularity_params = {}
        return VertexClustering(self, membership, modularity_params=modularity_params)

    def community_walktrap(self, weights=None, steps=4):
        """Community detection algorithm of Latapy & Pons, based on random
        walks.

        The basic idea of the algorithm is that short random walks tend to stay
        in the same community. The result of the clustering will be represented
        as a dendrogram.

        @param weights: name of an edge attribute or a list containing
          edge weights
        @param steps: length of random walks to perform

        @return: a L{VertexDendrogram} object, initially cut at the maximum
          modularity.

        @newfield ref: Reference
        @ref: Pascal Pons, Matthieu Latapy: Computing communities in large
          networks using random walks, U{http://arxiv.org/abs/physics/0512106}.
        """
        merges, qs = GraphBase.community_walktrap(self, weights, steps)
        qs.reverse()
        if qs:
            optimal_count = qs.index(max(qs)) + 1
        else:
            optimal_count = 1
        return VertexDendrogram(
            self, merges, optimal_count, modularity_params=dict(weights=weights)
        )

    def k_core(self, *args):
        """Returns some k-cores of the graph.

        The method accepts an arbitrary number of arguments representing
        the desired indices of the M{k}-cores to be returned. The arguments
        can also be lists or tuples. The result is a single L{Graph} object
        if an only integer argument was given, otherwise the result is a
        list of L{Graph} objects representing the desired k-cores in the
        order the arguments were specified. If no argument is given, returns
        all M{k}-cores in increasing order of M{k}.
        """
        if len(args) == 0:
            indices = range(self.vcount())
            return_single = False
        else:
            return_single = True
            indices = []
            for arg in args:
                try:
                    indices.extend(arg)
                except Exception:
                    indices.append(arg)

        if len(indices) > 1 or hasattr(args[0], "__iter__"):
            return_single = False

        corenesses = self.coreness()
        result = []
        vidxs = range(self.vcount())
        for idx in indices:
            core_idxs = [vidx for vidx in vidxs if corenesses[vidx] >= idx]
            result.append(self.subgraph(core_idxs))

        if return_single:
            return result[0]
        return result

    def community_leiden(
        self,
        objective_function="CPM",
        weights=None,
        resolution_parameter=1.0,
        beta=0.01,
        initial_membership=None,
        n_iterations=2,
        node_weights=None,
    ):
        """Finds the community structure of the graph using the Leiden
        algorithm of Traag, van Eck & Waltman.

        @param objective_function: whether to use the Constant Potts
          Model (CPM) or modularity. Must be either C{"CPM"} or C{"modularity"}.
        @param weights: edge weights to be used. Can be a sequence or
          iterable or even an edge attribute name.
        @param resolution_parameter: the resolution parameter to use.
          Higher resolutions lead to more smaller communities, while
          lower resolutions lead to fewer larger communities.
        @param beta: parameter affecting the randomness in the Leiden
          algorithm. This affects only the refinement step of the algorithm.
        @param initial_membership: if provided, the Leiden algorithm
          will try to improve this provided membership. If no argument is
          provided, the aglorithm simply starts from the singleton partition.
        @param n_iterations: the number of iterations to iterate the Leiden
          algorithm. Each iteration may improve the partition further. Using
          a negative number of iterations will run until a stable iteration is
          encountered (i.e. the quality was not increased during that
          iteration).
        @param node_weights: the node weights used in the Leiden algorithm.
          If this is not provided, it will be automatically determined on the
          basis of whether you want to use CPM or modularity. If you do provide
          this, please make sure that you understand what you are doing.
        @return: an appropriate L{VertexClustering} object.

        @newfield ref: Reference
        @ref: Traag, V. A., Waltman, L., & van Eck, N. J. (2019). From Louvain
          to Leiden: guaranteeing well-connected communities. Scientific
          reports, 9(1), 5233. doi: 10.1038/s41598-019-41695-z
        """
        if objective_function.lower() not in ("cpm", "modularity"):
            raise ValueError('objective_function must be "CPM" or "modularity".')

        membership = GraphBase.community_leiden(
            self,
            edge_weights=weights,
            node_weights=node_weights,
            resolution_parameter=resolution_parameter,
            normalize_resolution=(objective_function == "modularity"),
            beta=beta,
            initial_membership=initial_membership,
            n_iterations=n_iterations,
        )

        if weights is not None:
            modularity_params = dict(weights=weights)
        else:
            modularity_params = {}
        return VertexClustering(self, membership, modularity_params=modularity_params)

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
    to_networkx = export_graph_to_networkx

    from_networkx = classmethod(construct_graph_from_networkx)

    to_graph_tool = export_graph_to_graph_tool

    from_graph_tool = classmethod(construct_graph_from_graph_tool)

    # Files
    write_adjacency = write_graph_to_adjacency_file

    write_dimacs = write_graph_to_dimacs_file

    write_graphmlz = write_graph_to_graphmlz_file

    write_pickle = write_graph_to_pickle_file

    write_picklez = write_graph_to_picklez_file

    write_svg = write_graph_to_svg

    write = write_graph_to_file
    save = write

    Read_DIMACS = classmethod(construct_graph_from_dimacs_file)

    Read_GraphMLz = classmethod(construct_graph_from_graphmlz_file)

    Read_Pickle = classmethod(construct_graph_from_pickle_file)

    Read_Picklez = classmethod(construct_graph_from_picklez_file)

    Read_Adjacency = classmethod(construct_graph_from_adjacency_file)

    Read = classmethod(construct_graph_from_file)
    Load = Read

    # Various objects
    # list of dict representation of graphs
    DictList = classmethod(construct_graph_from_dict_list)

    # tuple-like representation of graphs
    TupleList = classmethod(construct_graph_from_tuple_list)

    # dict of sequence representation of graphs
    SequenceDict = classmethod(construct_graph_from_sequence_dict)

    # dict of dicts representation of graphs
    DictDict = classmethod(construct_graph_from_dict_dict)

    # adjacency matrix
    Adjacency = classmethod(construct_graph_from_adjacency)

    Weighted_Adjacency = classmethod(construct_graph_from_weighted_adjacency)

    # pandas dataframe(s)
    DataFrame = classmethod(construct_graph_from_dataframe)

    get_vertex_dataframe = export_vertex_dataframe

    get_edge_dataframe = export_edge_dataframe

    # Bipartite graphs
    Bipartite = classmethod(construct_bipartite_graph)

    Incidence = classmethod(construct_incidence_bipartite_graph)

    Full_Bipartite = classmethod(construct_full_bipartite_graph)

    Random_Bipartite = classmethod(construct_random_bipartite_graph)

    # Other constructors
    GRG = classmethod(construct_random_geometric_graph)

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

    def __iadd__(self, other):
        """In-place addition (disjoint union).

        @see: L{__add__}
        """
        if isinstance(other, (int, str)):
            self.add_vertices(other)
            return self
        elif isinstance(other, tuple) and len(other) == 2:
            self.add_edges([other])
            return self
        elif isinstance(other, list):
            if not other:
                return self
            if isinstance(other[0], tuple):
                self.add_edges(other)
                return self
            if isinstance(other[0], str):
                self.add_vertices(other)
                return self
        return NotImplemented

    def __add__(self, other):
        """Copies the graph and extends the copy depending on the type of
        the other object given.

        @param other: if it is an integer, the copy is extended by the given
          number of vertices. If it is a string, the copy is extended by a
          single vertex whose C{name} attribute will be equal to the given
          string. If it is a tuple with two elements, the copy
          is extended by a single edge. If it is a list of tuples, the copy
          is extended by multiple edges. If it is a L{Graph}, a disjoint
          union is performed.
        """
        if isinstance(other, (int, str)):
            g = self.copy()
            g.add_vertices(other)
        elif isinstance(other, tuple) and len(other) == 2:
            g = self.copy()
            g.add_edges([other])
        elif isinstance(other, list):
            if len(other) > 0:
                if isinstance(other[0], tuple):
                    g = self.copy()
                    g.add_edges(other)
                elif isinstance(other[0], str):
                    g = self.copy()
                    g.add_vertices(other)
                elif isinstance(other[0], Graph):
                    return self.disjoint_union(other)
                else:
                    return NotImplemented
            else:
                return self.copy()

        elif isinstance(other, Graph):
            return self.disjoint_union(other)
        else:
            return NotImplemented

        return g

    def __and__(self, other):
        """Graph intersection operator.

        @param other: the other graph to take the intersection with.
        @return: the intersected graph.
        """
        if isinstance(other, Graph):
            return self.intersection(other)
        else:
            return NotImplemented

    def __isub__(self, other):
        """In-place subtraction (difference).

        @see: L{__sub__}"""
        if isinstance(other, int):
            self.delete_vertices([other])
        elif isinstance(other, tuple) and len(other) == 2:
            self.delete_edges([other])
        elif isinstance(other, list):
            if len(other) > 0:
                if isinstance(other[0], tuple):
                    self.delete_edges(other)
                elif isinstance(other[0], (int, str)):
                    self.delete_vertices(other)
                else:
                    return NotImplemented
        elif isinstance(other, Vertex):
            self.delete_vertices(other)
        elif isinstance(other, VertexSeq):
            self.delete_vertices(other)
        elif isinstance(other, Edge):
            self.delete_edges(other)
        elif isinstance(other, EdgeSeq):
            self.delete_edges(other)
        else:
            return NotImplemented
        return self

    def __sub__(self, other):
        """Removes the given object(s) from the graph

        @param other: if it is an integer, removes the vertex with the given
          ID from the graph (note that the remaining vertices will get
          re-indexed!). If it is a tuple, removes the given edge. If it is
          a graph, takes the difference of the two graphs. Accepts
          lists of integers or lists of tuples as well, but they can't be
          mixed! Also accepts L{Edge} and L{EdgeSeq} objects.
        """
        if isinstance(other, Graph):
            return self.difference(other)

        result = self.copy()
        if isinstance(other, (int, str)):
            result.delete_vertices([other])
        elif isinstance(other, tuple) and len(other) == 2:
            result.delete_edges([other])
        elif isinstance(other, list):
            if len(other) > 0:
                if isinstance(other[0], tuple):
                    result.delete_edges(other)
                elif isinstance(other[0], (int, str)):
                    result.delete_vertices(other)
                else:
                    return NotImplemented
            else:
                return result
        elif isinstance(other, Vertex):
            result.delete_vertices(other)
        elif isinstance(other, VertexSeq):
            result.delete_vertices(other)
        elif isinstance(other, Edge):
            result.delete_edges(other)
        elif isinstance(other, EdgeSeq):
            result.delete_edges(other)
        else:
            return NotImplemented

        return result

    def __mul__(self, other):
        """Copies exact replicas of the original graph an arbitrary number of
        times.

        @param other: if it is an integer, multiplies the graph by creating the
          given number of identical copies and taking the disjoint union of
          them.
        """
        if isinstance(other, int):
            if other == 0:
                return Graph()
            elif other == 1:
                return self
            elif other > 1:
                return self.disjoint_union([self] * (other - 1))
            else:
                return NotImplemented

        return NotImplemented

    def __bool__(self):
        """Returns True if the graph has at least one vertex, False otherwise."""
        return self.vcount() > 0

    def __or__(self, other):
        """Graph union operator.

        @param other: the other graph to take the union with.
        @return: the union graph.
        """
        if isinstance(other, Graph):
            return self.union(other)
        else:
            return NotImplemented

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

    def __plot__(self, context, bbox, palette, *args, **kwds):
        """Plots the graph to the given Cairo context in the given bounding box

        The visual style of vertices and edges can be modified at three
        places in the following order of precedence (lower indices override
        higher indices):

          1. Keyword arguments of this function (or of L{plot()} which is
             passed intact to C{Graph.__plot__()}.

          2. Vertex or edge attributes, specified later in the list of
             keyword arguments.

          3. igraph-wide plotting defaults (see
             L{igraph.config.Configuration})

          4. Built-in defaults.

        E.g., if the C{vertex_size} keyword attribute is not present,
        but there exists a vertex attribute named C{size}, the sizes of
        the vertices will be specified by that attribute.

        Besides the usual self-explanatory plotting parameters (C{context},
        C{bbox}, C{palette}), it accepts the following keyword arguments:

          - C{autocurve}: whether to use curves instead of straight lines for
            multiple edges on the graph plot. This argument may be C{True}
            or C{False}; when omitted, C{True} is assumed for graphs with
            less than 10.000 edges and C{False} otherwise.

          - C{drawer_factory}: a subclass of L{AbstractCairoGraphDrawer}
            which will be used to draw the graph. You may also provide
            a function here which takes two arguments: the Cairo context
            to draw on and a bounding box (an instance of L{BoundingBox}).
            If this keyword argument is missing, igraph will use the
            default graph drawer which should be suitable for most purposes.
            It is safe to omit this keyword argument unless you need to use
            a specific graph drawer.

          - C{keep_aspect_ratio}: whether to keep the aspect ratio of the layout
            that igraph calculates to place the nodes. C{True} means that the
            layout will be scaled proportionally to fit into the bounding box
            where the graph is to be drawn but the aspect ratio will be kept
            the same (potentially leaving empty space next to, below or above
            the graph). C{False} means that the layout will be scaled independently
            along the X and Y axis in order to fill the entire bounding box.
            The default is C{False}.

          - C{layout}: the layout to be used. If not an instance of
            L{Layout}, it will be passed to L{layout} to calculate
            the layout. Note that if you want a deterministic layout that
            does not change with every plot, you must either use a
            deterministic layout function (like L{layout_circle}) or
            calculate the layout in advance and pass a L{Layout} object here.

          - C{margin}: the top, right, bottom, left margins as a 4-tuple.
            If it has less than 4 elements or is a single float, the elements
            will be re-used until the length is at least 4.

          - C{mark_groups}: whether to highlight some of the vertex groups by
            colored polygons. This argument can be one of the following:

              - C{False}: no groups will be highlighted

              - C{True}: only valid if the object plotted is a
                L{VertexClustering} or L{VertexCover}. The vertex groups in the
                clutering or cover will be highlighted such that the i-th
                group will be colored by the i-th color from the current
                palette. If used when plotting a graph, it will throw an error.

              - A dict mapping tuples of vertex indices to color names.
                The given vertex groups will be highlighted by the given
                colors.

              - A list containing pairs or an iterable yielding pairs, where
                the first element of each pair is a list of vertex indices and
                the second element is a color.

              - A L{VertexClustering} or L{VertexCover} instance. The vertex
                groups in the clustering or cover will be highlighted such that
                the i-th group will be colored by the i-th color from the
                current palette.

            In place of lists of vertex indices, you may also use L{VertexSeq}
            instances.

            In place of color names, you may also use color indices into the
            current palette. C{None} as a color name will mean that the
            corresponding group is ignored.

          - C{vertex_size}: size of the vertices. The corresponding vertex
            attribute is called C{size}. The default is 10. Vertex sizes
            are measured in the unit of the Cairo context on which igraph
            is drawing.

          - C{vertex_color}: color of the vertices. The corresponding vertex
            attribute is C{color}, the default is red.  Colors can be
            specified either by common X11 color names (see the source
            code of L{igraph.drawing.colors} for a list of known colors), by
            3-tuples of floats (ranging between 0 and 255 for the R, G and
            B components), by CSS-style string specifications (C{#rrggbb})
            or by integer color indices of the specified palette.

          - C{vertex_frame_color}: color of the frame (i.e. stroke) of the
            vertices. The corresponding vertex attribute is C{frame_color},
            the default is black. See C{vertex_color} for the possible ways
            of specifying a color.

          - C{vertex_frame_width}: the width of the frame (i.e. stroke) of the
            vertices. The corresponding vertex attribute is C{frame_width}.
            The default is 1. Vertex frame widths are measured in the unit of the
            Cairo context on which igraph is drawing.

          - C{vertex_shape}: shape of the vertices. Alternatively it can
            be specified by the C{shape} vertex attribute. Possibilities
            are: C{square}, {circle}, {triangle}, {triangle-down} or
            C{hidden}. See the source code of L{igraph.drawing} for a
            list of alternative shape names that are also accepted and
            mapped to these.

          - C{vertex_label}: labels drawn next to the vertices.
            The corresponding vertex attribute is C{label}.

          - C{vertex_label_dist}: distance of the midpoint of the vertex
            label from the center of the corresponding vertex.
            The corresponding vertex attribute is C{label_dist}.

          - C{vertex_label_color}: color of the label. Corresponding
            vertex attribute: C{label_color}. See C{vertex_color} for
            color specification syntax.

          - C{vertex_label_size}: font size of the label, specified
            in the unit of the Cairo context on which we are drawing.
            Corresponding vertex attribute: C{label_size}.

          - C{vertex_label_angle}: the direction of the line connecting
            the midpoint of the vertex with the midpoint of the label.
            This can be used to position the labels relative to the
            vertices themselves in conjunction with C{vertex_label_dist}.
            Corresponding vertex attribute: C{label_angle}. The
            default is C{-math.pi/2}.

          - C{vertex_order}: drawing order of the vertices. This must be
            a list or tuple containing vertex indices; vertices are then
            drawn according to this order.

          - C{vertex_order_by}: an alternative way to specify the drawing
            order of the vertices; this attribute is interpreted as the name
            of a vertex attribute, and vertices are drawn such that those
            with a smaller attribute value are drawn first. You may also
            reverse the order by passing a tuple here; the first element of
            the tuple should be the name of the attribute, the second element
            specifies whether the order is reversed (C{True}, C{False},
            C{"asc"} and C{"desc"} are accepted values).

          - C{edge_color}: color of the edges. The corresponding edge
            attribute is C{color}, the default is red. See C{vertex_color}
            for color specification syntax.

          - C{edge_curved}: whether the edges should be curved. Positive
            numbers correspond to edges curved in a counter-clockwise
            direction, negative numbers correspond to edges curved in a
            clockwise direction. Zero represents straight edges. C{True}
            is interpreted as 0.5, C{False} is interpreted as 0. The
            default is 0 which makes all the edges straight.

          - C{edge_width}: width of the edges in the default unit of the
            Cairo context on which we are drawing. The corresponding
            edge attribute is C{width}, the default is 1.

          - C{edge_arrow_size}: arrow size of the edges. The
            corresponding edge attribute is C{arrow_size}, the default
            is 1.

          - C{edge_arrow_width}: width of the arrowhead on the edge. The
            corresponding edge attribute is C{arrow_width}, the default
            is 1.

          - C{edge_order}: drawing order of the edges. This must be
            a list or tuple containing edge indices; edges are then
            drawn according to this order.

          - C{edge_order_by}: an alternative way to specify the drawing
            order of the edges; this attribute is interpreted as the name
            of an edge attribute, and edges are drawn such that those
            with a smaller attribute value are drawn first. You may also
            reverse the order by passing a tuple here; the first element of
            the tuple should be the name of the attribute, the second element
            specifies whether the order is reversed (C{True}, C{False},
            C{"asc"} and C{"desc"} are accepted values).
        """
        drawer_factory = kwds.get("drawer_factory", DefaultGraphDrawer)
        if "drawer_factory" in kwds:
            del kwds["drawer_factory"]
        drawer = drawer_factory(context, bbox)
        drawer.draw(self, palette, *args, **kwds)

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


class VertexSeq(_VertexSeq):
    """Class representing a sequence of vertices in the graph.

    This class is most easily accessed by the C{vs} field of the
    L{Graph} object, which returns an ordered sequence of all vertices in
    the graph. The vertex sequence can be refined by invoking the
    L{VertexSeq.select()} method. L{VertexSeq.select()} can also be
    accessed by simply calling the L{VertexSeq} object.

    An alternative way to create a vertex sequence referring to a given
    graph is to use the constructor directly:

      >>> g = Graph.Full(3)
      >>> vs = VertexSeq(g)
      >>> restricted_vs = VertexSeq(g, [0, 1])

    The individual vertices can be accessed by indexing the vertex sequence
    object. It can be used as an iterable as well, or even in a list
    comprehension:

      >>> g=Graph.Full(3)
      >>> for v in g.vs:
      ...   v["value"] = v.index ** 2
      ...
      >>> [v["value"] ** 0.5 for v in g.vs]
      [0.0, 1.0, 2.0]

    The vertex set can also be used as a dictionary where the keys are the
    attribute names. The values corresponding to the keys are the values
    of the given attribute for every vertex selected by the sequence.

      >>> g=Graph.Full(3)
      >>> for idx, v in enumerate(g.vs):
      ...   v["weight"] = idx*(idx+1)
      ...
      >>> g.vs["weight"]
      [0, 2, 6]
      >>> g.vs.select(1,2)["weight"] = [10, 20]
      >>> g.vs["weight"]
      [0, 10, 20]

    If you specify a sequence that is shorter than the number of vertices in
    the VertexSeq, the sequence is reused:

      >>> g = Graph.Tree(7, 2)
      >>> g.vs["color"] = ["red", "green"]
      >>> g.vs["color"]
      ['red', 'green', 'red', 'green', 'red', 'green', 'red']

    You can even pass a single string or integer, it will be considered as a
    sequence of length 1:

      >>> g.vs["color"] = "red"
      >>> g.vs["color"]
      ['red', 'red', 'red', 'red', 'red', 'red', 'red']

    Some methods of the vertex sequences are simply proxy methods to the
    corresponding methods in the L{Graph} object. One such example is
    C{VertexSeq.degree()}:

      >>> g=Graph.Tree(7, 2)
      >>> g.vs.degree()
      [2, 3, 3, 1, 1, 1, 1]
      >>> g.vs.degree() == g.degree()
      True
    """

    def attributes(self):
        """Returns the list of all the vertex attributes in the graph
        associated to this vertex sequence."""
        return self.graph.vertex_attributes()

    def find(self, *args, **kwds):
        """Returns the first vertex of the vertex sequence that matches some
        criteria.

        The selection criteria are equal to the ones allowed by L{VertexSeq.select}.
        See L{VertexSeq.select} for more details.

        For instance, to find the first vertex with name C{foo} in graph C{g}:

            >>> g.vs.find(name="foo")            #doctest:+SKIP

        To find an arbitrary isolated vertex:

            >>> g.vs.find(_degree=0)             #doctest:+SKIP
        """
        # Shortcut: if "name" is in kwds, there are no positional arguments,
        # and the specified name is a string, we try that first because that
        # attribute is indexed. Note that we cannot do this if name is an
        # integer, because it would then translate to g.vs.select(name), which
        # searches by _index_ if the argument is an integer
        if not args:
            if "name" in kwds:
                name = kwds.pop("name")
            elif "name_eq" in kwds:
                name = kwds.pop("name_eq")
            else:
                name = None

            if name is not None:
                if isinstance(name, str):
                    args = [name]
                else:
                    # put back what we popped
                    kwds["name"] = name

        if args:
            # Selecting first based on positional arguments, then checking
            # the criteria specified by the (remaining) keyword arguments
            vertex = _VertexSeq.find(self, *args)
            if not kwds:
                return vertex
            vs = self.graph.vs.select(vertex.index)
        else:
            vs = self

        # Selecting based on keyword arguments
        vs = vs.select(**kwds)
        if vs:
            return vs[0]
        raise ValueError("no such vertex")

    def select(self, *args, **kwds):
        """Selects a subset of the vertex sequence based on some criteria

        The selection criteria can be specified by the positional and the keyword
        arguments. Positional arguments are always processed before keyword
        arguments.

          - If the first positional argument is C{None}, an empty sequence is
            returned.

          - If the first positional argument is a callable object, the object
            will be called for every vertex in the sequence. If it returns
            C{True}, the vertex will be included, otherwise it will
            be excluded.

          - If the first positional argument is an iterable, it must return
            integers and they will be considered as indices of the current
            vertex set (NOT the whole vertex set of the graph -- the
            difference matters when one filters a vertex set that has
            already been filtered by a previous invocation of
            L{VertexSeq.select()}. In this case, the indices do not refer
            directly to the vertices of the graph but to the elements of
            the filtered vertex sequence.

          - If the first positional argument is an integer, all remaining
            arguments are expected to be integers. They are considered as
            indices of the current vertex set again.

        Keyword arguments can be used to filter the vertices based on their
        attributes. The name of the keyword specifies the name of the attribute
        and the filtering operator, they should be concatenated by an
        underscore (C{_}) character. Attribute names can also contain
        underscores, but operator names don't, so the operator is always the
        largest trailing substring of the keyword name that does not contain
        an underscore. Possible operators are:

          - C{eq}: equal to

          - C{ne}: not equal to

          - C{lt}: less than

          - C{gt}: greater than

          - C{le}: less than or equal to

          - C{ge}: greater than or equal to

          - C{in}: checks if the value of an attribute is in a given list

          - C{notin}: checks if the value of an attribute is not in a given
            list

        For instance, if you want to filter vertices with a numeric C{age}
        property larger than 200, you have to write:

          >>> g.vs.select(age_gt=200)                   #doctest: +SKIP

        Similarly, to filter vertices whose C{type} is in a list of predefined
        types:

          >>> list_of_types = ["HR", "Finance", "Management"]
          >>> g.vs.select(type_in=list_of_types)        #doctest: +SKIP

        If the operator is omitted, it defaults to C{eq}. For instance, the
        following selector selects vertices whose C{cluster} property equals
        to 2:

          >>> g.vs.select(cluster=2)                    #doctest: +SKIP

        In the case of an unknown operator, it is assumed that the
        recognized operator is part of the attribute name and the actual
        operator is C{eq}.

        Attribute names inferred from keyword arguments are treated specially
        if they start with an underscore (C{_}). These are not real attributes
        but refer to specific properties of the vertices, e.g., its degree.
        The rule is as follows: if an attribute name starts with an underscore,
        the rest of the name is interpreted as a method of the L{Graph} object.
        This method is called with the vertex sequence as its first argument
        (all others left at default values) and vertices are filtered
        according to the value returned by the method. For instance, if you
        want to exclude isolated vertices:

          >>> g = Graph.Famous("zachary")
          >>> non_isolated = g.vs.select(_degree_gt=0)

        For properties that take a long time to be computed (e.g., betweenness
        centrality for large graphs), it is advised to calculate the values
        in advance and store it in a graph attribute. The same applies when
        you are selecting based on the same property more than once in the
        same C{select()} call to avoid calculating it twice unnecessarily.
        For instance, the following would calculate betweenness centralities
        twice:

          >>> edges = g.vs.select(_betweenness_gt=10, _betweenness_lt=30)

        It is advised to use this instead:

          >>> g.vs["bs"] = g.betweenness()
          >>> edges = g.vs.select(bs_gt=10, bs_lt=30)

        @return: the new, filtered vertex sequence"""
        vs = _VertexSeq.select(self, *args)

        operators = {
            "lt": operator.lt,
            "gt": operator.gt,
            "le": operator.le,
            "ge": operator.ge,
            "eq": operator.eq,
            "ne": operator.ne,
            "in": lambda a, b: a in b,
            "notin": lambda a, b: a not in b,
        }
        for keyword, value in kwds.items():
            if "_" not in keyword or keyword.rindex("_") == 0:
                keyword = keyword + "_eq"
            attr, _, op = keyword.rpartition("_")
            try:
                func = operators[op]
            except KeyError:
                # No such operator, assume that it's part of the attribute name
                attr, op, func = keyword, "eq", operators["eq"]

            if attr[0] == "_":
                # Method call, not an attribute
                values = getattr(vs.graph, attr[1:])(vs)
            else:
                values = vs[attr]
            filtered_idxs = [i for i, v in enumerate(values) if func(v, value)]
            vs = vs.select(filtered_idxs)

        return vs

    def __call__(self, *args, **kwds):
        """Shorthand notation to select()

        This method simply passes all its arguments to L{VertexSeq.select()}.
        """
        return self.select(*args, **kwds)


##############################################################


class EdgeSeq(_EdgeSeq):
    """Class representing a sequence of edges in the graph.

    This class is most easily accessed by the C{es} field of the
    L{Graph} object, which returns an ordered sequence of all edges in
    the graph. The edge sequence can be refined by invoking the
    L{EdgeSeq.select()} method. L{EdgeSeq.select()} can also be
    accessed by simply calling the L{EdgeSeq} object.

    An alternative way to create an edge sequence referring to a given
    graph is to use the constructor directly:

      >>> g = Graph.Full(3)
      >>> es = EdgeSeq(g)
      >>> restricted_es = EdgeSeq(g, [0, 1])

    The individual edges can be accessed by indexing the edge sequence
    object. It can be used as an iterable as well, or even in a list
    comprehension:

      >>> g=Graph.Full(3)
      >>> for e in g.es:
      ...   print(e.tuple)
      ...
      (0, 1)
      (0, 2)
      (1, 2)
      >>> [max(e.tuple) for e in g.es]
      [1, 2, 2]

    The edge sequence can also be used as a dictionary where the keys are the
    attribute names. The values corresponding to the keys are the values
    of the given attribute of every edge in the graph:

      >>> g=Graph.Full(3)
      >>> for idx, e in enumerate(g.es):
      ...   e["weight"] = idx*(idx+1)
      ...
      >>> g.es["weight"]
      [0, 2, 6]
      >>> g.es["weight"] = range(3)
      >>> g.es["weight"]
      [0, 1, 2]

    If you specify a sequence that is shorter than the number of edges in
    the EdgeSeq, the sequence is reused:

      >>> g = Graph.Tree(7, 2)
      >>> g.es["color"] = ["red", "green"]
      >>> g.es["color"]
      ['red', 'green', 'red', 'green', 'red', 'green']

    You can even pass a single string or integer, it will be considered as a
    sequence of length 1:

      >>> g.es["color"] = "red"
      >>> g.es["color"]
      ['red', 'red', 'red', 'red', 'red', 'red']

    Some methods of the edge sequences are simply proxy methods to the
    corresponding methods in the L{Graph} object. One such example is
    C{EdgeSeq.is_multiple()}:

      >>> g=Graph(3, [(0,1), (1,0), (1,2)])
      >>> g.es.is_multiple()
      [False, True, False]
      >>> g.es.is_multiple() == g.is_multiple()
      True
    """

    def attributes(self):
        """Returns the list of all the edge attributes in the graph
        associated to this edge sequence."""
        return self.graph.edge_attributes()

    def find(self, *args, **kwds):
        """Returns the first edge of the edge sequence that matches some
        criteria.

        The selection criteria are equal to the ones allowed by L{VertexSeq.select}.
        See L{VertexSeq.select} for more details.

        For instance, to find the first edge with weight larger than 5 in graph C{g}:

            >>> g.es.find(weight_gt=5)           #doctest:+SKIP
        """
        if args:
            # Selecting first based on positional arguments, then checking
            # the criteria specified by the keyword arguments
            edge = _EdgeSeq.find(self, *args)
            if not kwds:
                return edge
            es = self.graph.es.select(edge.index)
        else:
            es = self

        # Selecting based on positional arguments
        es = es.select(**kwds)
        if es:
            return es[0]
        raise ValueError("no such edge")

    def select(self, *args, **kwds):
        """Selects a subset of the edge sequence based on some criteria

        The selection criteria can be specified by the positional and the
        keyword arguments. Positional arguments are always processed before
        keyword arguments.

          - If the first positional argument is C{None}, an empty sequence is
            returned.

          - If the first positional argument is a callable object, the object
            will be called for every edge in the sequence. If it returns
            C{True}, the edge will be included, otherwise it will
            be excluded.

          - If the first positional argument is an iterable, it must return
            integers and they will be considered as indices of the current
            edge set (NOT the whole edge set of the graph -- the
            difference matters when one filters an edge set that has
            already been filtered by a previous invocation of
            L{EdgeSeq.select()}. In this case, the indices do not refer
            directly to the edges of the graph but to the elements of
            the filtered edge sequence.

          - If the first positional argument is an integer, all remaining
            arguments are expected to be integers. They are considered as
            indices of the current edge set again.

        Keyword arguments can be used to filter the edges based on their
        attributes and properties. The name of the keyword specifies the name
        of the attribute and the filtering operator, they should be
        concatenated by an underscore (C{_}) character. Attribute names can
        also contain underscores, but operator names don't, so the operator is
        always the largest trailing substring of the keyword name that does not
        contain an underscore. Possible operators are:

          - C{eq}: equal to

          - C{ne}: not equal to

          - C{lt}: less than

          - C{gt}: greater than

          - C{le}: less than or equal to

          - C{ge}: greater than or equal to

          - C{in}: checks if the value of an attribute is in a given list

          - C{notin}: checks if the value of an attribute is not in a given
            list

        For instance, if you want to filter edges with a numeric C{weight}
        property larger than 50, you have to write:

          >>> g.es.select(weight_gt=50)            #doctest: +SKIP

        Similarly, to filter edges whose C{type} is in a list of predefined
        types:

          >>> list_of_types = ["inhibitory", "excitatory"]
          >>> g.es.select(type_in=list_of_types)   #doctest: +SKIP

        If the operator is omitted, it defaults to C{eq}. For instance, the
        following selector selects edges whose C{type} property is
        C{intracluster}:

          >>> g.es.select(type="intracluster")     #doctest: +SKIP

        In the case of an unknown operator, it is assumed that the
        recognized operator is part of the attribute name and the actual
        operator is C{eq}.

        Keyword arguments are treated specially if they start with an
        underscore (C{_}). These are not real attributes but refer to specific
        properties of the edges, e.g., their centrality.  The rules are as
        follows:

          1. C{_source} or {_from} means the source vertex of an edge. For
             undirected graphs, only the C{eq} operator is supported and it
             is treated as {_incident} (since undirected graphs have no notion
             of edge directionality).

          2. C{_target} or {_to} means the target vertex of an edge. For
             undirected graphs, only the C{eq} operator is supported and it
             is treated as {_incident} (since undirected graphs have no notion
             of edge directionality).

          3. C{_within} ignores the operator and checks whether both endpoints
             of the edge lie within a specified set.

          4. C{_between} ignores the operator and checks whether I{one}
             endpoint of the edge lies within a specified set and the I{other}
             endpoint lies within another specified set. The two sets must be
             given as a tuple.

          5. C{_incident} ignores the operator and checks whether the edge is
             incident on a specific vertex or a set of vertices.

          6. Otherwise, the rest of the name is interpreted as a method of the
             L{Graph} object. This method is called with the edge sequence as
             its first argument (all others left at default values) and edges
             are filtered according to the value returned by the method.

        For instance, if you want to exclude edges with a betweenness
        centrality less than 2:

          >>> g = Graph.Famous("zachary")
          >>> excl = g.es.select(_edge_betweenness_ge = 2)

        To select edges originating from vertices 2 and 4:

          >>> edges = g.es.select(_source_in = [2, 4])

        To select edges lying entirely within the subgraph spanned by vertices
        2, 3, 4 and 7:

          >>> edges = g.es.select(_within = [2, 3, 4, 7])

        To select edges with one endpoint in the vertex set containing vertices
        2, 3, 4 and 7 and the other endpoint in the vertex set containing
        vertices 8 and 9:

          >>> edges = g.es.select(_between = ([2, 3, 4, 7], [8, 9]))

        For properties that take a long time to be computed (e.g., betweenness
        centrality for large graphs), it is advised to calculate the values
        in advance and store it in a graph attribute. The same applies when
        you are selecting based on the same property more than once in the
        same C{select()} call to avoid calculating it twice unnecessarily.
        For instance, the following would calculate betweenness centralities
        twice:

          >>> edges = g.es.select(_edge_betweenness_gt=10,       # doctest:+SKIP
          ...                     _edge_betweenness_lt=30)

        It is advised to use this instead:

          >>> g.es["bs"] = g.edge_betweenness()
          >>> edges = g.es.select(bs_gt=10, bs_lt=30)

        @return: the new, filtered edge sequence
        """
        es = _EdgeSeq.select(self, *args)
        is_directed = self.graph.is_directed()

        def _ensure_set(value):
            if isinstance(value, VertexSeq):
                value = set(v.index for v in value)
            elif not isinstance(value, (set, frozenset)):
                value = set(value)
            return value

        operators = {
            "lt": operator.lt,
            "gt": operator.gt,
            "le": operator.le,
            "ge": operator.ge,
            "eq": operator.eq,
            "ne": operator.ne,
            "in": lambda a, b: a in b,
            "notin": lambda a, b: a not in b,
        }

        # TODO(ntamas): some keyword arguments should be prioritized over
        # others; for instance, we have optimized code paths for _source and
        # _target in directed and undirected graphs if es.is_all() is True;
        # these should be executed first. This matters only if there are
        # multiple keyword arguments and es.is_all() is True.

        for keyword, value in kwds.items():
            if "_" not in keyword or keyword.rindex("_") == 0:
                keyword = keyword + "_eq"
            pos = keyword.rindex("_")
            attr, op = keyword[0:pos], keyword[pos + 1 :]
            try:
                func = operators[op]
            except KeyError:
                # No such operator, assume that it's part of the attribute name
                attr, op, func = keyword, "eq", operators["eq"]

            if attr[0] == "_":
                if attr in ("_source", "_from", "_target", "_to") and not is_directed:
                    if op not in ("eq", "in"):
                        raise RuntimeError("unsupported for undirected graphs")

                    # translate to _incident to avoid confusion
                    attr = "_incident"
                    if func == operators["eq"]:
                        if hasattr(value, "__iter__") and not isinstance(value, str):
                            value = set(value)
                        else:
                            value = set([value])

                if attr in ("_source", "_from"):
                    if es.is_all() and op == "eq":
                        # shortcut here: use .incident() as it is much faster
                        filtered_idxs = sorted(es.graph.incident(value, mode="out"))
                        func = None
                        # TODO(ntamas): there are more possibilities; we could
                        # optimize "ne", "in" and "notin" in similar ways
                    else:
                        values = [e.source for e in es]
                        if op == "in" or op == "notin":
                            value = _ensure_set(value)

                elif attr in ("_target", "_to"):
                    if es.is_all() and op == "eq":
                        # shortcut here: use .incident() as it is much faster
                        filtered_idxs = sorted(es.graph.incident(value, mode="in"))
                        func = None
                        # TODO(ntamas): there are more possibilities; we could
                        # optimize "ne", "in" and "notin" in similar ways
                    else:
                        values = [e.target for e in es]
                        if op == "in" or op == "notin":
                            value = _ensure_set(value)

                elif attr == "_incident":
                    func = None  # ignoring function, filtering here
                    value = _ensure_set(value)

                    # Fetch all the edges that are incident on at least one of
                    # the vertices specified
                    candidates = set()
                    for v in value:
                        candidates.update(es.graph.incident(v))

                    if not es.is_all():
                        # Find those that are in the current edge sequence
                        filtered_idxs = [
                            i for i, e in enumerate(es) if e.index in candidates
                        ]
                    else:
                        # We are done, the filtered indexes are in the candidates set
                        filtered_idxs = sorted(candidates)

                elif attr == "_within":
                    func = None  # ignoring function, filtering here
                    value = _ensure_set(value)

                    # Fetch all the edges that are incident on at least one of
                    # the vertices specified
                    candidates = set()
                    for v in value:
                        candidates.update(es.graph.incident(v))

                    if not es.is_all():
                        # Find those where both endpoints are OK
                        filtered_idxs = [
                            i
                            for i, e in enumerate(es)
                            if e.index in candidates
                            and e.source in value
                            and e.target in value
                        ]
                    else:
                        # Optimized version when the edge sequence contains all
                        # the edges exactly once in increasing order of edge IDs
                        filtered_idxs = [
                            i
                            for i in candidates
                            if es[i].source in value and es[i].target in value
                        ]

                elif attr == "_between":
                    if len(value) != 2:
                        raise ValueError(
                            "_between selector requires two vertex ID lists"
                        )
                    func = None  # ignoring function, filtering here
                    set1 = _ensure_set(value[0])
                    set2 = _ensure_set(value[1])

                    # Fetch all the edges that are incident on at least one of
                    # the vertices specified
                    candidates = set()
                    for v in set1:
                        candidates.update(es.graph.incident(v))
                    for v in set2:
                        candidates.update(es.graph.incident(v))

                    if not es.is_all():
                        # Find those where both endpoints are OK
                        filtered_idxs = [
                            i
                            for i, e in enumerate(es)
                            if (e.source in set1 and e.target in set2)
                            or (e.target in set1 and e.source in set2)
                        ]
                    else:
                        # Optimized version when the edge sequence contains all
                        # the edges exactly once in increasing order of edge IDs
                        filtered_idxs = [
                            i
                            for i in candidates
                            if (es[i].source in set1 and es[i].target in set2)
                            or (es[i].target in set1 and es[i].source in set2)
                        ]

                else:
                    # Method call, not an attribute
                    values = getattr(es.graph, attr[1:])(es)
            else:
                values = es[attr]

            # If we have a function to apply on the values, do that; otherwise
            # we assume that filtered_idxs has already been calculated.
            if func is not None:
                filtered_idxs = [i for i, v in enumerate(values) if func(v, value)]

            es = es.select(filtered_idxs)

        return es

    def __call__(self, *args, **kwds):
        """Shorthand notation to select()

        This method simply passes all its arguments to L{EdgeSeq.select()}.
        """
        return self.select(*args, **kwds)


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


def autocurve(graph, attribute="curved", default=0):
    """Calculates curvature values for each of the edges in the graph to make
    sure that multiple edges are shown properly on a graph plot.

    This function checks the multiplicity of each edge in the graph and
    assigns curvature values (numbers between -1 and 1, corresponding to
    CCW (-1), straight (0) and CW (1) curved edges) to them. The assigned
    values are either stored in an edge attribute or returned as a list,
    depending on the value of the I{attribute} argument.

    @param graph: the graph on which the calculation will be run
    @param attribute: the name of the edge attribute to save the curvature
      values to. The default value is C{curved}, which is the name of the
      edge attribute the default graph plotter checks to decide whether an
      edge should be curved on the plot or not. If I{attribute} is C{None},
      the result will not be stored.
    @param default: the default curvature for single edges. Zero means that
      single edges will be straight. If you want single edges to be curved
      as well, try passing 0.5 or -0.5 here.
    @return: the list of curvature values if I{attribute} is C{None},
      otherwise C{None}.
    """

    # The following loop could be re-written in C if it turns out to be a
    # bottleneck. Unfortunately we cannot use Graph.count_multiple() here
    # because we have to ignore edge directions.
    multiplicities = defaultdict(list)
    for edge in graph.es:
        u, v = edge.tuple
        if u > v:
            multiplicities[v, u].append(edge.index)
        else:
            multiplicities[u, v].append(edge.index)

    result = [default] * graph.ecount()
    for eids in multiplicities.values():
        # Is it a single edge?
        if len(eids) < 2:
            continue

        if len(eids) % 2 == 1:
            # Odd number of edges; the last will be straight
            result[eids.pop()] = 0

        # Arrange the remaining edges
        curve = 2.0 / (len(eids) + 2)
        dcurve, sign = curve, 1
        for idx, eid in enumerate(eids):
            edge = graph.es[eid]
            if edge.source > edge.target:
                result[eid] = -sign * curve
            else:
                result[eid] = sign * curve
            if idx % 2 == 1:
                curve += dcurve
            sign *= -1

    if attribute is None:
        return result

    graph.es[attribute] = result


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

# Remove constructors from namespace
del (
    construct_graph_from_formula,
    construct_graph_from_graphmlz_file,
    construct_graph_from_dimacs_file,
    construct_graph_from_pickle_file,
    construct_graph_from_picklez_file,
    construct_graph_from_adjacency_file,
    construct_graph_from_file,
    construct_graph_from_dict_list,
    construct_graph_from_tuple_list,
    construct_graph_from_sequence_dict,
    construct_graph_from_dict_dict,
    construct_graph_from_adjacency,
    construct_graph_from_weighted_adjacency,
    construct_graph_from_dataframe,
    construct_random_geometric_graph,
    construct_bipartite_graph,
    construct_incidence_bipartite_graph,
    construct_full_bipartite_graph,
    construct_random_bipartite_graph,
    construct_graph_from_networkx,
    export_graph_to_networkx,
    construct_graph_from_graph_tool,
    export_graph_to_graph_tool,
    )
