# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""Implementation of Python-level sparse matrix operations."""

from __future__ import with_statement

__all__ = ()
__docformat__ = "restructuredtext en"

from operator import add
from igraph._igraph import (
    ADJ_DIRECTED,
    ADJ_UNDIRECTED,
    ADJ_MAX,
    ADJ_MIN,
    ADJ_PLUS,
    ADJ_UPPER,
    ADJ_LOWER,
)


_SUPPORTED_MODES = ("directed", "undirected", "max", "min", "plus", "lower", "upper")


def _convert_mode_argument(mode):
    # resolve mode constants, convert to lowercase
    mode = (
        {
            ADJ_DIRECTED: "directed",
            ADJ_UNDIRECTED: "undirected",
            ADJ_MAX: "max",
            ADJ_MIN: "min",
            ADJ_PLUS: "plus",
            ADJ_UPPER: "upper",
            ADJ_LOWER: "lower",
        }
        .get(mode, mode)
        .lower()
    )

    if mode not in _SUPPORTED_MODES:
        raise ValueError("mode should be one of " + (" ".join(_SUPPORTED_MODES)))

    if mode == "undirected":
        mode = "max"

    return mode


# Logic to get graph from scipy sparse matrix. This would be simple if there
# weren't so many modes.
def _graph_from_sparse_matrix(klass, matrix, mode="directed"):
    """Construct graph from sparse matrix, unweighted"""
    # This function assumes there is scipy and the matrix is a scipy sparse
    # matrix. The caller should make sure those conditions are met.
    from scipy import sparse

    if not isinstance(matrix, sparse.coo_matrix):
        matrix = matrix.tocoo()

    nvert = max(matrix.shape)
    if min(matrix.shape) != nvert:
        raise ValueError("Matrix must be square")

    # Shorthand notation
    m = matrix

    mode = _convert_mode_argument(mode)

    if mode == "directed":
        edges = sum(
            ([(i, j)] * n for i, j, n in zip(m.row, m.col, m.data)),
            [],
        )

    elif mode in ("max", "plus"):
        fun = max if mode == "max" else add
        nedges = {}
        for i, j, n in zip(m.row, m.col, m.data):
            pair = (i, j) if i < j else (j, i)
            nedges[pair] = fun(nedges.get(pair, 0), n)

        edges = sum(
            ([e] * n for e, n in nedges.items()),
            [],
        )

    elif mode == "min":
        tmp = {(i, j): n for i, j, n in zip(m.row, m.col, m.data)}

        nedges = {}
        for pair, weight in tmp.items():
            i, j = pair
            if i == j:
                nedges[pair] = weight
            elif i < j:
                nedges[pair] = min(weight, tmp.get((j, i), 0))

        edges = sum(
            ([e] * n for e, n in nedges.items()),
            [],
        )

    elif mode == "upper":
        edges = sum(
            ([(i, j)] * n for i, j, n in zip(m.row, m.col, m.data) if j >= i),
            [],
        )

    elif mode == "lower":
        edges = sum(
            ([(i, j)] * n for i, j, n in zip(m.row, m.col, m.data) if j <= i),
            [],
        )

    else:
        raise ValueError("invalid mode")

    return klass(nvert, edges=edges, directed=(mode == "directed"))


def _graph_from_weighted_sparse_matrix(
    klass, matrix, mode=ADJ_DIRECTED, attr="weight", loops=True
):
    """Construct graph from sparse matrix, weighted

    NOTE: Of course, you cannot emcompass a fully general weighted multigraph
    with a single adjacency matrix, so we don't try to do it here either.
    """
    # This function assumes there is scipy and the matrix is a scipy sparse
    # matrix. The caller should make sure those conditions are met.
    from scipy import sparse

    if not isinstance(matrix, sparse.coo_matrix):
        matrix = matrix.tocoo()

    nvert = max(matrix.shape)
    if min(matrix.shape) != nvert:
        raise ValueError("Matrix must be square")

    # Shorthand notation
    m = matrix

    mode = _convert_mode_argument(mode)

    if mode == "directed":
        if not loops:
            edges, weights = [], []
            for i, j, n in zip(m.row, m.col, m.data):
                if i != j:
                    edges.append((i, j))
                    weights.append(n)
        else:
            edges = list(zip(m.row, m.col))
            weights = list(m.data)

    elif mode in ("max", "plus"):
        fun = max if mode == "max" else add
        nedges = {}
        for i, j, n in zip(m.row, m.col, m.data):
            if i == j and not loops:
                continue
            pair = (i, j) if i < j else (j, i)
            nedges[pair] = fun(nedges.get(pair, 0), n)

        edges, weights = zip(*nedges.items())

    elif mode == "min":
        tmp = {(i, j): n for i, j, n in zip(m.row, m.col, m.data)}

        nedges = {}
        for pair, weight in tmp.items():
            i, j = pair
            if i == j and loops:
                nedges[pair] = weight
            elif i < j:
                nedges[pair] = min(weight, tmp.get((j, i), 0))

        edges, weights = [], []
        for pair in sorted(nedges.keys()):
            weight = nedges[pair]
            if weight != 0:
                edges.append(pair)
                weights.append(nedges[pair])

    elif mode == "upper":
        edges, weights = [], []
        for i, j, n in zip(m.row, m.col, m.data):
            if j > i or (loops and j == i):
                edges.append((i, j))
                weights.append(n)

    elif mode == "lower":
        edges, weights = [], []
        for i, j, n in zip(m.row, m.col, m.data):
            if j < i or (loops and j == i):
                edges.append((i, j))
                weights.append(n)

    else:
        raise ValueError("invalid mode")

    return klass(
        nvert, edges=edges, directed=(mode == "directed"), edge_attrs={attr: weights}
    )
