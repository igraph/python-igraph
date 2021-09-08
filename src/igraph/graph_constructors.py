"""
IGraph library.
"""


__license__ = """
Copyright (C) 2006-2012  Tamás Nepusz <ntamas@gmail.com>
Pázmány Péter sétány 1/a, 1117 Budapest, Hungary

Copyright (C) 2021- igraph development team

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
import gzip
from shutil import copyfileobj
from warnings import warn

from igraph.datatypes import UniqueIdGenerator
from igraph.sparse_matrix import (
    _graph_from_sparse_matrix,
    _graph_from_weighted_sparse_matrix,
)
from igraph.utils import (
    named_temporary_file,
)


def construct_graph_from_dict_list(
    cls,
    vertices,
    edges,
    directed=False,
    vertex_name_attr="name",
    edge_foreign_keys=("source", "target"),
    iterative=False,
):
    """Constructs a graph from a list-of-dictionaries representation.

    This representation assumes that vertices and edges are encoded in
    two lists, each list containing a Python dict for each vertex and
    each edge, respectively. A distinguished element of the vertex dicts
    contain a vertex ID which is used in the edge dicts to refer to
    source and target vertices. All the remaining elements of the dict
    are considered vertex and edge attributes. Note that the implementation
    does not assume that the objects passed to this method are indeed
    lists of dicts, but they should be iterable and they should yield
    objects that behave as dicts. So, for instance, a database query
    result is likely to be fit as long as it's iterable and yields
    dict-like objects with every iteration.

    @param vertices: the data source for the vertices or C{None} if
      there are no special attributes assigned to vertices and we
      should simply use the edge list of dicts to infer vertex names.
    @param edges: the data source for the edges.
    @param directed: whether the constructed graph will be directed
    @param vertex_name_attr: the name of the distinguished key in the
      dicts in the vertex data source that contains the vertex names.
      Ignored if C{vertices} is C{None}.
    @param edge_foreign_keys: the name of the attributes in the dicts
      in the edge data source that contain the source and target
      vertex names.
    @param iterative: whether to add the edges to the graph one by one,
      iteratively, or to build a large edge list first and use that to
      construct the graph. The latter approach is faster but it may
      not be suitable if your dataset is large. The default is to
      add the edges in a batch from an edge list.
    @return: the graph that was constructed
    """

    def create_list_from_indices(indices, n):
        result = [None] * n
        for i, v in indices:
            result[i] = v
        return result

    # Construct the vertices
    vertex_attrs, n = {}, 0
    if vertices:
        for idx, vertex_data in enumerate(vertices):
            for k, v in vertex_data.items():
                try:
                    vertex_attrs[k].append((idx, v))
                except KeyError:
                    vertex_attrs[k] = [(idx, v)]
            n += 1
        for k, v in vertex_attrs.items():
            vertex_attrs[k] = create_list_from_indices(v, n)
    else:
        vertex_attrs[vertex_name_attr] = []

    vertex_names = vertex_attrs[vertex_name_attr]
    # Check for duplicates in vertex_names
    if len(vertex_names) != len(set(vertex_names)):
        raise ValueError("vertex names are not unique")
    # Create a reverse mapping from vertex names to indices
    vertex_name_map = UniqueIdGenerator(initial=vertex_names)

    # Construct the edges
    efk_src, efk_dest = edge_foreign_keys
    if iterative:
        g = cls(n, [], directed, {}, vertex_attrs)
        for idx, edge_data in enumerate(edges):
            src_name, dst_name = edge_data[efk_src], edge_data[efk_dest]
            v1 = vertex_name_map[src_name]
            if v1 == n:
                g.add_vertices(1)
                g.vs[n][vertex_name_attr] = src_name
                n += 1
            v2 = vertex_name_map[dst_name]
            if v2 == n:
                g.add_vertices(1)
                g.vs[n][vertex_name_attr] = dst_name
                n += 1
            g.add_edge(v1, v2)
            for k, v in edge_data.items():
                g.es[idx][k] = v

        return g
    else:
        edge_list, edge_attrs, m = [], {}, 0
        for idx, edge_data in enumerate(edges):
            v1 = vertex_name_map[edge_data[efk_src]]
            v2 = vertex_name_map[edge_data[efk_dest]]

            edge_list.append((v1, v2))
            for k, v in edge_data.items():
                try:
                    edge_attrs[k].append((idx, v))
                except KeyError:
                    edge_attrs[k] = [(idx, v)]
            m += 1
        for k, v in edge_attrs.items():
            edge_attrs[k] = create_list_from_indices(v, m)

        # It may have happened that some vertices were added during
        # the process
        if len(vertex_name_map) > n:
            diff = len(vertex_name_map) - n
            more = [None] * diff
            for k, v in vertex_attrs.items():
                v.extend(more)
            vertex_attrs[vertex_name_attr] = list(vertex_name_map.values())
            n = len(vertex_name_map)

        # Create the graph
        return cls(n, edge_list, directed, {}, vertex_attrs, edge_attrs)


def construct_graph_from_tuple_list(
    cls,
    edges,
    directed=False,
    vertex_name_attr="name",
    edge_attrs=None,
    weights=False,
):
    """Constructs a graph from a list-of-tuples representation.

    This representation assumes that the edges of the graph are encoded
    in a list of tuples (or lists). Each item in the list must have at least
    two elements, which specify the source and the target vertices of the edge.
    The remaining elements (if any) specify the edge attributes of that edge,
    where the names of the edge attributes originate from the C{edge_attrs}
    list. The names of the vertices will be stored in the vertex attribute
    given by C{vertex_name_attr}.

    The default parameters of this function are suitable for creating
    unweighted graphs from lists where each item contains the source vertex
    and the target vertex. If you have a weighted graph, you can use items
    where the third item contains the weight of the edge by setting
    C{edge_attrs} to C{"weight"} or C{["weight"]}. If you have even more
    edge attributes, add them to the end of each item in the C{edges}
    list and also specify the corresponding edge attribute names in
    C{edge_attrs} as a list.

    @param edges: the data source for the edges. This must be a list
      where each item is a tuple (or list) containing at least two
      items: the name of the source and the target vertex. Note that
      names will be assigned to the C{name} vertex attribute (or another
      vertex attribute if C{vertex_name_attr} is specified), even if
      all the vertex names in the list are in fact numbers.
    @param directed: whether the constructed graph will be directed
    @param vertex_name_attr: the name of the vertex attribute that will
      contain the vertex names.
    @param edge_attrs: the names of the edge attributes that are filled
      with the extra items in the edge list (starting from index 2, since
      the first two items are the source and target vertices). C{None}
      means that only the source and target vertices will be extracted
      from each item. If you pass a string here, it will be wrapped in
      a list for convenience.
    @param weights: alternative way to specify that the graph is
      weighted. If you set C{weights} to C{true} and C{edge_attrs} is
      not given, it will be assumed that C{edge_attrs} is C{["weight"]}
      and igraph will parse the third element from each item into an
      edge weight. If you set C{weights} to a string, it will be assumed
      that C{edge_attrs} contains that string only, and igraph will
      store the edge weights in that attribute.
    @return: the graph that was constructed
    """
    if edge_attrs is None:
        if not weights:
            edge_attrs = ()
        else:
            if not isinstance(weights, str):
                weights = "weight"
            edge_attrs = [weights]
    else:
        if weights:
            raise ValueError(
                "`weights` must be False if `edge_attrs` is " "not None"
            )

    if isinstance(edge_attrs, str):
        edge_attrs = [edge_attrs]

    # Set up a vertex ID generator
    idgen = UniqueIdGenerator()

    # Construct the edges and the edge attributes
    edge_list = []
    edge_attributes = {}
    for name in edge_attrs:
        edge_attributes[name] = []

    for item in edges:
        edge_list.append((idgen[item[0]], idgen[item[1]]))
        for index, name in enumerate(edge_attrs, 2):
            try:
                edge_attributes[name].append(item[index])
            except IndexError:
                edge_attributes[name].append(None)

    # Set up the "name" vertex attribute
    vertex_attributes = {}
    vertex_attributes[vertex_name_attr] = list(idgen.values())
    n = len(idgen)

    # Construct the graph
    return cls(n, edge_list, directed, {}, vertex_attributes, edge_attributes)


def construct_graph_from_sequence_dict(
    cls,
    edges,
    directed=False,
    vertex_name_attr="name",
):
    """Constructs a graph from a dict-of-sequences representation.

    This function is used to construct a graph from a dictionary of
    sequences (e.g. of lists). For each key x, its corresponding value is
    a sequence of multiple objects: for each y, the edge (x,y) will be
    created in the graph. x and y must be either one of:

    - two integers: the vertices with those ids will be connected
    - two strings: the vertices with those names will be connected

    If names are used, the order of vertices is not guaranteed, and each
    vertex will be given the vertex_name_attr attribute.
    """
    # Check if we are using names or integers
    for item in edges:
        break
    if not isinstance(item, (int, str)):
        raise ValueError("Keys must be integers or strings")

    vertex_attributes = {}
    if isinstance(item, str):
        name_map = UniqueIdGenerator()
        edge_list = []
        for source, sequence in edges.items():
            source_id = name_map[source]
            for target in sequence:
                edge_list.append((source_id, name_map[target]))
        vertex_attributes[vertex_name_attr] = name_map.values()
        n = len(name_map)

    else:
        edge_list = []
        n = 0
        for source, sequence in edges.items():
            n = max(n, source, *sequence)
            for target in sequence:
                edge_list.append((source, target))
        n += 1

    # Construct the graph
    return cls(n, edge_list, directed, {}, vertex_attributes, {})


def construct_graph_from_dict_dict(
    cls,
    edges,
    directed=False,
):
    """Constructs a graph from a dict-of-dicts representation.

    Each key can be an integer or a string and represent a vertex. Each value
    is a dict representing edges (outgoing if the graph is directed) from that
    vertex. Each dict key is an integer/string for a target vertex, such that
    an edge will be created between those two vertices, while each value is
    a dictionary of edge attributes for that edge.

    Example:

    {'Alice': {'Bob': {'weight': 1.5}, 'David': {'weight': 2}}}

    creates a graph with three vertices (Alice, Bob, and David) and two edges:
    
    - Alice - Bob (with weight 1.5)
    - Alice - David (with weight 2)
    """
    # Check if we are using names or integers
    for item in edges:
        break
    if not isinstance(item, (int, str)):
        raise ValueError("Keys must be integers or strings")

    vertex_attributes = {}
    edge_attribute_list = []
    if isinstance(item, str):
        name_map = UniqueIdGenerator()
        edge_list = []
        for source, target_dict in edges.items():
            source_id = name_map[source]
            for target, edge_attrs in target_dict.items():
                edge_list.append((source_id, name_map[target]))
                edge_attribute_list.append(edge_attrs)
        vertex_attributes['name'] = name_map.values()
        n = len(name_map)

    else:
        edge_list = []
        n = 0
        for source, target_dict in edges.items():
            n = max(n, source, *target_dict)
            for target, edge_attrs in target_dict.items():
                edge_list.append((source, target))
                edge_attribute_list.append(edge_attrs)
        n += 1

    # Construct graph without edge attributes
    graph = cls(n, edge_list, directed, {}, vertex_attributes, {})

    # Add edge attributes
    for edge, edge_attrs in zip(graph.es, edge_attribute_list):
        for key, val in edge_attrs:
            edge[key] = val

    return graph


def construct_graph_from_adjacency(cls, matrix, mode="directed", *args, **kwargs):
    """Generates a graph from its adjacency matrix.

    @param matrix: the adjacency matrix. Possible types are:
      - a list of lists
      - a numpy 2D array or matrix (will be converted to list of lists)
      - a scipy.sparse matrix (will be converted to a COO matrix, but not
        to a dense matrix)
      - a pandas.DataFrame (column/row names must match, and will be used
        as vertex names).
    @param mode: the mode to be used. Possible values are:
      - C{"directed"} - the graph will be directed and a matrix
        element gives the number of edges between two vertex.
      - C{"undirected"} - alias to C{"max"} for convenience.
      - C{"max"} - undirected graph will be created and the number of
        edges between vertex M{i} and M{j} is M{max(A(i,j), A(j,i))}
      - C{"min"} - like C{"max"}, but with M{min(A(i,j), A(j,i))}
      - C{"plus"}  - like C{"max"}, but with M{A(i,j) + A(j,i)}
      - C{"upper"} - undirected graph with the upper right triangle of
        the matrix (including the diagonal)
      - C{"lower"} - undirected graph with the lower left triangle of
        the matrix (including the diagonal)
    """
    # Deferred import to avoid cycles
    from igraph import Graph

    try:
        import numpy as np
    except ImportError:
        np = None

    try:
        from scipy import sparse
    except ImportError:
        sparse = None

    try:
        import pandas as pd
    except ImportError:
        pd = None

    if (sparse is not None) and isinstance(matrix, sparse.spmatrix):
        return _graph_from_sparse_matrix(cls, matrix, mode=mode)

    if (pd is not None) and isinstance(matrix, pd.DataFrame):
        vertex_names = matrix.index.tolist()
        matrix = matrix.values
    else:
        vertex_names = None

    if (np is not None) and isinstance(matrix, np.ndarray):
        matrix = matrix.tolist()

    graph = super(Graph, cls).Adjacency(matrix, mode=mode)

    # Add vertex names if present
    if vertex_names is not None:
        graph.vs['name'] = vertex_names

    return graph


def construct_graph_from_weighted_adjacency(cls, matrix, mode="directed", attr="weight", loops=True):
    """Generates a graph from its weighted adjacency matrix.

    @param matrix: the adjacency matrix. Possible types are:
      - a list of lists
      - a numpy 2D array or matrix (will be converted to list of lists)
      - a scipy.sparse matrix (will be converted to a COO matrix, but not
        to a dense matrix)
    @param mode: the mode to be used. Possible values are:
      - C{"directed"} - the graph will be directed and a matrix
        element gives the number of edges between two vertex.
      - C{"undirected"} - alias to C{"max"} for convenience.
      - C{"max"}   - undirected graph will be created and the number of
        edges between vertex M{i} and M{j} is M{max(A(i,j), A(j,i))}
      - C{"min"}   - like C{"max"}, but with M{min(A(i,j), A(j,i))}
      - C{"plus"}  - like C{"max"}, but with M{A(i,j) + A(j,i)}
      - C{"upper"} - undirected graph with the upper right triangle of
        the matrix (including the diagonal)
      - C{"lower"} - undirected graph with the lower left triangle of
        the matrix (including the diagonal)

      These values can also be given as strings without the C{ADJ} prefix.
    @param attr: the name of the edge attribute that stores the edge
      weights.
    @param loops: whether to include loop edges. When C{False}, the diagonal
      of the adjacency matrix will be ignored.

    """
    # Deferred import to avoid cycles
    from igraph import Graph

    try:
        import numpy as np
    except ImportError:
        np = None

    try:
        from scipy import sparse
    except ImportError:
        sparse = None

    try:
        import pandas as pd
    except ImportError:
        pd = None

    if (sparse is not None) and isinstance(matrix, sparse.spmatrix):
        return _graph_from_weighted_sparse_matrix(
            cls,
            matrix,
            mode=mode,
            attr=attr,
            loops=loops,
        )

    if (pd is not None) and isinstance(matrix, pd.DataFrame):
        vertex_names = matrix.index.tolist()
        matrix = matrix.values
    else:
        vertex_names = None

    if (np is not None) and isinstance(matrix, np.ndarray):
        matrix = matrix.tolist()

    graph = super(Graph, cls).Weighted_Adjacency(
        matrix,
        mode=mode,
        attr=attr,
        loops=loops,
    )

    # Add vertex names if present
    if vertex_names is not None:
        graph.vs['name'] = vertex_names

    return graph


def construct_graph_from_dataframe(cls, edges, directed=True, vertices=None, use_vids=False):
    """Generates a graph from one or two dataframes.

    @param edges: pandas DataFrame containing edges and metadata. The first
      two columns of this DataFrame contain the source and target vertices
      for each edge. These indicate the vertex *names* rather than IDs
      unless `use_vids` is True and these are non-negative integers. Further
      columns may contain edge attributes.
    @param directed: bool setting whether the graph is directed
    @param vertices: None (default) or pandas DataFrame containing vertex
      metadata. The first column of the DataFrame must contain the unique
      vertex *names*. If `use_vids` is True, the DataFrame's index must
      contain the vertex IDs as a sequence of intergers from `0` to
      `len(vertices) - 1`. All other columns will be added as vertex
      attributes by column name.
    @use_vids: whether to interpret the first two columns of the `edges`
      argument as vertex ids (0-based integers) instead of vertex names.
      If this argument is set to True and the first two columns of `edges`
      are not integers, an error is thrown.

    @return: the graph

    Vertex names in either the `edges` or `vertices` arguments that are set
    to NaN (not a number) will be set to the string "NA". That might lead
    to unexpected behaviour: fill your NaNs with values before calling this
    function to mitigate.
    """
    # Deferred import to avoid cycles
    from igraph import Graph

    try:
        import pandas as pd
    except ImportError:
        raise ImportError("You should install pandas in order to use this function")
    try:
        import numpy as np
    except:
        raise ImportError("You should install numpy in order to use this function")

    if edges.shape[1] < 2:
        raise ValueError("The 'edges' DataFrame must contain at least two columns")
    if vertices is not None and vertices.shape[1] < 1:
        raise ValueError("The 'vertices' DataFrame must contain at least one column")

    if use_vids:
        if not (str(edges.dtypes[0]).startswith("int") and str(edges.dtypes[1]).startswith("int")):
            raise TypeError(f"Source and target IDs must be 0-based integers, found types {edges.dtypes.tolist()[:2]}")
        elif (edges.iloc[:, :2] < 0).any(axis=None):
            raise ValueError("Source and target IDs must not be negative")
        if vertices is not None:
            vertices = vertices.sort_index()
            if not vertices.index.equals(pd.RangeIndex.from_range(range(vertices.shape[0]))):
                if not str(vertices.index.dtype).startswith("int"):
                    raise TypeError(f"Vertex IDs must be 0-based integers, found type {vertices.index.dtype}")
                elif (vertices.index < 0).any(axis=None):
                    raise ValueError("Vertex IDs must not be negative")
                else:
                    raise ValueError(f"Vertex IDs must be an integer sequence from 0 to {vertices.shape[0] - 1}")
    else:
        # Handle if some source and target names in 'edges' are 'NA'
        if edges.iloc[:, :2].isna().any(axis=None):
            warn("In the first two columns of 'edges' NA elements were replaced with string \"NA\"")
            edges = edges.copy()
            edges.iloc[:, :2].fillna("NA", inplace=True)

        # Bring DataFrame(s) into same format as with 'use_vids=True'
        if vertices is None:
            vertices = pd.DataFrame({"name": np.unique(edges.values[:, :2])})

        if vertices.iloc[:, 0].isna().any():
            warn("In the first column of 'vertices' NA elements were replaced with string \"NA\"")
            vertices = vertices.copy()
            vertices.iloc[:, 0].fillna("NA", inplace=True)

        if vertices.iloc[:, 0].duplicated().any():
            raise ValueError("Vertex names must be unique")

        if vertices.shape[1] > 1 and "name" in vertices.columns[1:]:
            raise ValueError("Vertex attribute conflict: DataFrame already contains column 'name'")

        vertices = vertices.rename({vertices.columns[0]: "name"}, axis=1).reset_index(drop=True)

        # Map source and target names in 'edges' to IDs
        vid_map = pd.Series(vertices.index, index=vertices.iloc[:, 0])
        edges = edges.copy()
        edges.iloc[:, 0] = edges.iloc[:, 0].map(vid_map)
        edges.iloc[:, 1] = edges.iloc[:, 1].map(vid_map)

    # Create graph
    if vertices is None:
        nv = edges.iloc[:, :2].max().max() + 1
        g = Graph(n=nv, directed=directed)
    else:
        if not edges.iloc[:, :2].isin(vertices.index).all(axis=None):
            raise ValueError("Some vertices in the edge DataFrame are missing from vertices DataFrame")
        nv = vertices.shape[0]
        g = Graph(n=nv, directed=directed)
        # Add vertex attributes
        for col in vertices.columns:
            g.vs[col] = vertices[col].tolist()

    # add edges including optional attributes
    e_list = list(edges.iloc[:, :2].itertuples(index=False, name=None))
    e_attr = edges.iloc[:, 2:].to_dict(orient='list') if edges.shape[1] > 2 else None
    g.add_edges(e_list, e_attr)

    return g


def construct_graph_from_adjacency_file(
    cls, f, sep=None, comment_char="#", attribute=None, *args, **kwds
):
    """Constructs a graph based on an adjacency matrix from the given file.

    Additional positional and keyword arguments not mentioned here are
    passed intact to L{Adjacency}.

    @param f: the name of the file to be read or a file object
    @param sep: the string that separates the matrix elements in a row.
      C{None} means an arbitrary sequence of whitespace characters.
    @param comment_char: lines starting with this string are treated
      as comments.
    @param attribute: an edge attribute name where the edge weights are
      stored in the case of a weighted adjacency matrix. If C{None},
      no weights are stored, values larger than 1 are considered as
      edge multiplicities.
    @return: the created graph"""
    if isinstance(f, str):
        f = open(f)

    matrix, ri = [], 0
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue
        if line.startswith(comment_char):
            continue
        row = [float(x) for x in line.split(sep)]
        matrix.append(row)
        ri += 1

    f.close()

    if attribute is None:
        graph = cls.Adjacency(matrix, *args, **kwds)
    else:
        kwds["attr"] = attribute
        graph = cls.Weighted_Adjacency(matrix, *args, **kwds)

    return graph


def construct_graph_from_dimacs_file(cls, f, directed=False):
    """Reads a graph from a file conforming to the DIMACS minimum-cost flow
    file format.

    For the exact definition of the format, see
    U{http://lpsolve.sourceforge.net/5.5/DIMACS.htm}.

    Restrictions compared to the official description of the format are
    as follows:

      - igraph's DIMACS reader requires only three fields in an arc
        definition, describing the edge's source and target node and
        its capacity.
      - Source vertices are identified by 's' in the FLOW field, target
        vertices are identified by 't'.
      - Node indices start from 1. Only a single source and target node
        is allowed.

    @param f: the name of the file or a Python file handle
    @param directed: whether the generated graph should be directed.
    @return: the generated graph. The indices of the source and target
      vertices are attached as graph attributes C{source} and C{target},
      the edge capacities are stored in the C{capacity} edge attribute.
    """
    # Deferred import to avoid cycles
    from igraph import Graph

    graph, source, target, cap = super(Graph, cls).Read_DIMACS(f, directed)
    graph.es["capacity"] = cap
    graph["source"] = source
    graph["target"] = target
    return graph


def construct_graph_from_graphmlz_file(cls, f, directed=True, index=0):
    """Reads a graph from a zipped GraphML file.

    @param f: the name of the file
    @param index: if the GraphML file contains multiple graphs,
      specified the one that should be loaded. Graph indices
      start from zero, so if you want to load the first graph,
      specify 0 here.
    @return: the loaded graph object"""
    with named_temporary_file() as tmpfile:
        with open(tmpfile, "wb") as outf:
            copyfileobj(gzip.GzipFile(f, "rb"), outf)
        return cls.Read_GraphML(tmpfile, directed=directed, index=index)


def construct_graph_from_pickle_file(cls, fname=None):
    """Reads a graph from Python pickled format

    @param fname: the name of the file, a stream to read from, or
      a string containing the pickled data.
    @return: the created graph object.
    """
    import pickle as pickle

    if hasattr(fname, "read"):
        # Probably a file or a file-like object
        result = pickle.load(fname)
    else:
        try:
            fp = open(fname, "rb")
        except UnicodeDecodeError:
            try:
                # We are on Python 3.6 or above and we are passing a pickled
                # stream that cannot be decoded as Unicode. Try unpickling
                # directly.
                result = pickle.loads(fname)
            except TypeError:
                raise IOError(
                    "Cannot load file. If fname is a file name, that "
                    "filename may be incorrect."
                )
        except IOError:
            try:
                # No file with the given name, try unpickling directly.
                result = pickle.loads(fname)
            except TypeError:
                raise IOError(
                    "Cannot load file. If fname is a file name, that "
                    "filename may be incorrect."
                )
        else:
            result = pickle.load(fp)
            fp.close()

    if not isinstance(result, cls):
        raise TypeError("unpickled object is not a %s" % cls.__name__)

    return result


def construct_graph_from_picklez_file(cls, fname):
    """Reads a graph from compressed Python pickled format, uncompressing
    it on-the-fly.

    @param fname: the name of the file or a stream to read from.
    @return: the created graph object.
    """
    import pickle as pickle

    if hasattr(fname, "read"):
        # Probably a file or a file-like object
        if isinstance(fname, gzip.GzipFile):
            result = pickle.load(fname)
        else:
            result = pickle.load(gzip.GzipFile(mode="rb", fileobj=fname))
    else:
        result = pickle.load(gzip.open(fname, "rb"))

    if not isinstance(result, cls):
        raise TypeError("unpickled object is not a %s" % cls.__name__)

    return result


def construct_graph_from_file(cls, f, format=None, *args, **kwds):
    """Unified reading function for graphs.

    This method tries to identify the format of the graph given in
    the first parameter and calls the corresponding reader method.

    The remaining arguments are passed to the reader method without
    any changes.

    @param f: the file containing the graph to be loaded
    @param format: the format of the file (if known in advance).
      C{None} means auto-detection. Possible values are: C{"ncol"}
      (NCOL format), C{"lgl"} (LGL format), C{"graphdb"} (GraphDB
      format), C{"graphml"}, C{"graphmlz"} (GraphML and gzipped
      GraphML format), C{"gml"} (GML format), C{"net"}, C{"pajek"}
      (Pajek format), C{"dimacs"} (DIMACS format), C{"edgelist"},
      C{"edges"} or C{"edge"} (edge list), C{"adjacency"}
      (adjacency matrix), C{"dl"} (DL format used by UCINET),
      C{"pickle"} (Python pickled format),
      C{"picklez"} (gzipped Python pickled format)
    @raises IOError: if the file format can't be identified and
      none was given.
    """
    if format is None:
        format = cls._identify_format(f)
    try:
        reader = cls._format_mapping[format][0]
    except (KeyError, IndexError):
        raise IOError("unknown file format: %s" % str(format))
    if reader is None:
        raise IOError("no reader method for file format: %s" % str(format))
    reader = getattr(cls, reader)
    return reader(f, *args, **kwds)


def construct_random_geometric_graph(cls, n, radius, torus=False):
    """Generates a random geometric graph.

    The algorithm drops the vertices randomly on the 2D unit square and
    connects them if they are closer to each other than the given radius.
    The coordinates of the vertices are stored in the vertex attributes C{x}
    and C{y}.

    @param n: The number of vertices in the graph
    @param radius: The given radius
    @param torus: This should be C{True} if we want to use a torus instead of a
      square.
    """
    result, xs, ys = cls._GRG(n, radius, torus)
    result.vs["x"] = xs
    result.vs["y"] = ys
    return result


def construct_incidence_bipartite_graph(
    cls,
    matrix,
    directed=False,
    mode="out",
    multiple=False,
    weighted=None,
    *args,
    **kwds
):
    """Creates a bipartite graph from an incidence matrix.

    Example:

    >>> g = Graph.Incidence([[0, 1, 1], [1, 1, 0]])

    @param matrix: the incidence matrix.
    @param directed: whether to create a directed graph.
    @param mode: defines the direction of edges in the graph. If
      C{"out"}, then edges go from vertices of the first kind
      (corresponding to rows of the matrix) to vertices of the
      second kind (the columns of the matrix). If C{"in"}, the
      opposite direction is used. C{"all"} creates mutual edges.
      Ignored for undirected graphs.
    @param multiple: defines what to do with non-zero entries in the
      matrix. If C{False}, non-zero entries will create an edge no matter
      what the value is. If C{True}, non-zero entries are rounded up to
      the nearest integer and this will be the number of multiple edges
      created.
    @param weighted: defines whether to create a weighted graph from the
      incidence matrix. If it is c{None} then an unweighted graph is created
      and the multiple argument is used to determine the edges of the graph.
      If it is a string then for every non-zero matrix entry, an edge is created
      and the value of the entry is added as an edge attribute named by the
      weighted argument. If it is C{True} then a weighted graph is created and
      the name of the edge attribute will be ‘weight’.

    @raise ValueError: if the weighted and multiple are passed together.

    @return: the graph with a binary vertex attribute named C{"type"} that
      stores the vertex classes.
    """
    is_weighted = True if weighted or weighted == "" else False
    if is_weighted and multiple:
        raise ValueError("arguments weighted and multiple can not co-exist")
    result, types = cls._Incidence(matrix, directed, mode, multiple, *args, **kwds)
    result.vs["type"] = types
    if is_weighted:
        weight_attr = "weight" if weighted is True else weighted
        _, rows, _ = result.get_incidence()
        num_vertices_of_first_kind = len(rows)
        for edge in result.es:
            source, target = edge.tuple
            if source in rows:
                edge[weight_attr] = matrix[source][
                    target - num_vertices_of_first_kind
                ]
            else:
                edge[weight_attr] = matrix[target][
                    source - num_vertices_of_first_kind
                ]
    return result


def construct_bipartite_graph(cls, types, edges, directed=False, *args, **kwds):
    """Creates a bipartite graph with the given vertex types and edges.
    This is similar to the default constructor of the graph, the
    only difference is that it checks whether all the edges go
    between the two vertex classes and it assigns the type vector
    to a C{type} attribute afterwards.

    Examples:

    >>> g = Graph.Bipartite([0, 1, 0, 1], [(0, 1), (2, 3), (0, 3)])
    >>> g.is_bipartite()
    True
    >>> g.vs["type"]
    [False, True, False, True]

    @param types: the vertex types as a boolean list. Anything that
      evaluates to C{False} will denote a vertex of the first kind,
      anything that evaluates to C{True} will denote a vertex of the
      second kind.
    @param edges: the edges as a list of tuples.
    @param directed: whether to create a directed graph. Bipartite
      networks are usually undirected, so the default is C{False}

    @return: the graph with a binary vertex attribute named C{"type"} that
      stores the vertex classes.
    """
    result = cls._Bipartite(types, edges, directed, *args, **kwds)
    result.vs["type"] = [bool(x) for x in types]
    return result


def construct_full_bipartite_graph(cls, n1, n2, directed=False, mode="all", *args, **kwds):
    """Generates a full bipartite graph (directed or undirected, with or
    without loops).

    >>> g = Graph.Full_Bipartite(2, 3)
    >>> g.is_bipartite()
    True
    >>> g.vs["type"]
    [False, False, True, True, True]

    @param n1: the number of vertices of the first kind.
    @param n2: the number of vertices of the second kind.
    @param directed: whether tp generate a directed graph.
    @param mode: if C{"out"}, then all vertices of the first kind are
      connected to the others; C{"in"} specifies the opposite direction,
      C{"all"} creates mutual edges. Ignored for undirected graphs.

    @return: the graph with a binary vertex attribute named C{"type"} that
      stores the vertex classes.
    """
    result, types = cls._Full_Bipartite(n1, n2, directed, mode, *args, **kwds)
    result.vs["type"] = types
    return result


def construct_random_bipartite_graph(
    cls, n1, n2, p=None, m=None, directed=False, neimode="all", *args, **kwds
):
    """Generates a random bipartite graph with the given number of vertices and
    edges (if m is given), or with the given number of vertices and the given
    connection probability (if p is given).

    If m is given but p is not, the generated graph will have n1 vertices of
    type 1, n2 vertices of type 2 and m randomly selected edges between them. If
    p is given but m is not, the generated graph will have n1 vertices of type 1
    and n2 vertices of type 2, and each edge will exist between them with
    probability p.

    @param n1: the number of vertices of type 1.
    @param n2: the number of vertices of type 2.
    @param p: the probability of edges. If given, C{m} must be missing.
    @param m: the number of edges. If given, C{p} must be missing.
    @param directed: whether to generate a directed graph.
    @param neimode: if the graph is directed, specifies how the edges will be
      generated. If it is C{"all"}, edges will be generated in both directions
      (from type 1 to type 2 and vice versa) independently. If it is C{"out"}
      edges will always point from type 1 to type 2. If it is C{"in"}, edges
      will always point from type 2 to type 1. This argument is ignored for
      undirected graphs.
    """
    if p is None:
        p = -1
    if m is None:
        m = -1
    result, types = cls._Random_Bipartite(
        n1, n2, p, m, directed, neimode, *args, **kwds
    )
    result.vs["type"] = types
    return result
