# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""Implementation of Python-level sparse matrix operations."""

from __future__ import with_statement

__all__ = ()
__docformat__ = "restructuredtext en"
__license__ = u"""
Copyright (C) 2021  igraph development team

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


# Logic to get graph from scipy sparse matrix. This would be simple if there
# weren't so many modes.
def _graph_from_sparse_matrix(klass, matrix, mode=ADJ_DIRECTED):
    '''Construct graph from sparse matrix, unweighted'''
    # This function assumes there is scipy and the matrix is a scipy sparse
    # matrix. The caller should make sure those conditions are met.
    from scipy import sparse

    modes = (
        ADJ_DIRECTED,
        ADJ_UNDIRECTED,
        ADJ_MAX,
        ADJ_MIN,
        ADJ_PLUS,
        ADJ_UPPER,
        ADJ_LOWER,
    )

    if not isinstance(matrix, sparse.coo_matrix):
        matrix = matrix.tocoo()

    # Shorthand notation
    m = matrix

    if mode == ADJ_UNDIRECTED:
        mode = ADJ_MAX

    if mode == ADJ_DIRECTED:
        edges = sum(
            ([(i, j)] * n for i, j, n in zip(m.row, m.col, m.data)),
            [],
        )

    elif mode in (ADJ_MAX, ADJ_MIN, ADJ_PLUS):
        fun_dict = {
            ADJ_MAX: max,
            ADJ_MIN: min,
            ADJ_PLUS: add,
        }
        fun = fun_dict[mode]
        nedges = {}
        for i, j, n in zip(m.row, m.col, m.data):
            # Fist time this pair of vertices
            if (j, i) not in nedges:
                nedges[(i, j)] = n
            else:
                nedges[(j, i)] = fun(nedges[(j, i)], n)

        edges = sum(
            ([e] * n for e, n in nedges.items()),
            [],
        )

    elif mode == ADJ_UPPER:
        edges = sum(
            ([(i, j)] * n for i, j, n in zip(m.row, m.col, m.data) if j >= i),
            [],
        )

    elif mode == ADJ_LOWER:
        edges = sum(
            ([(i, j)] * n for i, j, n in zip(m.row, m.col, m.data) if j <= i),
            [],
        )

    else:
        raise ValueError("mode should be one of " + " ".join(map(str, modes)))

    return klass(
        edges=edges,
        directed=mode == ADJ_DIRECTED,
    )


def _graph_from_weighted_sparse_matrix(klass, matrix, mode=ADJ_DIRECTED, attr='weight'):
    '''Construct graph from sparse matrix, weighted

    NOTE: Of course, you cannot emcompass a fully general weighted multigraph
    with a single adjacency matrix, so we don't try to do it here either.
    '''
    # This function assumes there is scipy and the matrix is a scipy sparse
    # matrix. The caller should make sure those conditions are met.
    from scipy import sparse

    modes = (
        ADJ_DIRECTED,
        ADJ_UNDIRECTED,
        ADJ_MAX,
        ADJ_MIN,
        ADJ_PLUS,
        ADJ_UPPER,
        ADJ_LOWER,
    )

    if not isinstance(matrix, sparse.coo_matrix):
        matrix = matrix.tocoo()

    # Shorthand notation
    m = matrix

    if mode == ADJ_UNDIRECTED:
        mode = ADJ_MAX

    if mode == ADJ_DIRECTED:
        edges = list(zip(m.row, m.col))
        weights = list(m.data)

    elif mode in (ADJ_MAX, ADJ_MIN, ADJ_PLUS):
        fun_dict = {
            ADJ_MAX: max,
            ADJ_MIN: min,
            ADJ_PLUS: add,
        }
        fun = fun_dict[mode]
        nedges = {}
        for i, j, n in zip(m.row, m.col, m.data):
            # Fist time this pair of vertices
            if (j, i) not in nedges:
                nedges[(i, j)] = n
            else:
                nedges[(j, i)] = fun(nedges[(j, i)], n)

        edges, weights = zip(*nedges.items())

    elif mode == ADJ_UPPER:
        edges, weights = [], []
        for i, j, n in zip(m.row, m.col, m.data):
            if j >= i:
                edges.append((i, j))
                weights.append(n)

    elif mode == ADJ_LOWER:
        edges, weights = [], []
        for i, j, n in zip(m.row, m.col, m.data):
            if j <= i:
                edges.append((i, j))
                weights.append(n)

    else:
        raise ValueError("mode should be one of " + " ".join(map(str, modes)))

    return klass(
        edges=edges,
        directed=mode == ADJ_DIRECTED,
        edge_attrs={attr: weights},
    )
