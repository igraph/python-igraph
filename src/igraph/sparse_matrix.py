# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""Implementation of union, disjoint union and intersection operators."""

from __future__ import with_statement

__all__ = ['_graph_from_sparse_matrix']
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

# pylint: disable-msg=W0401
# W0401: wildcard import
from igraph._igraph import *


# Logic to get graph from scipy sparse matrix. This would be simple if there
# weren't so many modes.
def _graph_from_sparse_matrix(klass, matrix, mode=ADJ_DIRECTED):
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

    if mode == ADJ_DIRECTED:
        edges = sum(
                ([(i, j)] * n for i, j, n in zip(m.row, m.col, m.data)),
                [],
                )
        return klass(
                edges=edges, directed=True,
            )

    if mode == ADJ_UNDIRECTED:
        mode = ADJ_MAX

    if mode in (ADJ_MAX, ADJ_MIN, ADJ_PLUS):
        fun_dict = {
                ADJ_MAX: max,
                ADJ_MIN: min,
                ADJ_PLUS: lambda *x: sum(x),
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
        return klass(
                edges=edges, directed=False,
            )

    if mode == ADJ_UPPER:
        edges = sum(
                ([(i, j)] * n for i, j, n in zip(m.row, m.col, m.data) if j >= i),
                [],
                )
        return klass(
                edges=edges, directed=True,
            )

    if mode == ADJ_LOWER:
        edges = sum(
                ([(i, j)] * n for i, j, n in zip(m.row, m.col, m.data) if j <= i),
                [],
                )
        return klass(
                edges=edges, directed=True,
            )

    raise ValueError('mode should be one of ' + ' '.join(map(str, modes)))
