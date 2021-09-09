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

from igraph.sparse_matrix import (
    _graph_from_sparse_matrix,
    _graph_from_weighted_sparse_matrix,
)


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


