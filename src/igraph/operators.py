# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""
IGraph library.

@undocumented: deprecated, _graphmethod, _add_proxy_methods, _layout_method_wrapper,
               _3d_version_for
"""

from __future__ import with_statement

__license__ = u"""
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

# pylint: disable-msg=W0401
# W0401: wildcard import
from igraph._igraph import *

from warnings import warn


def union(graphs, byname='auto'):
    """Graph union.

    The union of two or more graphs is created. The graphs may have identical
    or overlapping vertex sets. Edges which are included in at least one graph
    will be part of the new graph.

    This function keeps the attributes of all graphs. All graph, vertex and
    edge attributes are copied to the result. If an attribute is present in
    multiple graphs and would result a name clash, then this attribute is
    renamed by adding suffixes: _1, _2, etc.

    The 'name' vertex attribute is treated specially if the operation is
    performed based on symbolic vertex names. In this case 'name' must be
    present in all graphs, and it is not renamed in the result graph.

    An error is generated if some input graphs are directed and others are
    undirected.

    @param graph: list of graphs. A lazy sequence is not acceptable.
    @param byname: bool or 'auto' specifying the function behaviour with
      respect to names vertices (i.e. vertices with the 'name' attribute). If
      False, ignore vertex names. If True, merge vertices based on names. If
      'auto', use True if all graphs have named vertices and False otherwise
      (in the latter case, a warning is generated too).
    @return: the union graph
    """

    if any(not isinstance(g, GraphBase) for g in graphs):
        raise TypeError('Not all elements are graphs')

    if byname not in (True, False, 'auto'):
        raise ValueError('"byname" should be a bool or "auto"')

    ngr = len(graphs)
    n_named = sum(g.is_named() for g in graphs)
    if byname == 'auto':
        byname = n_named == ngr
        if n_named not in (0, ngr):
            warn("Some, but not all graphs are named, not using vertex names")
    elif byname and (n_named != ngr):
        raise AttributeError("Some graphs are not named")
    # Now we know that byname is only used is all graphs are named

    # Trivial cases
    if ngr == 0:
        return None
    if ngr == 1:
        return graphs[0]
    # Now there are at least two graphs

    if byname:
        allnames = [g.vs['name'] for g in graphs]
        uninames = list(set.union(*(set(an) for an in allnames)))
        permutation_map = {x: i for i, x in enumerate(uninames)}
        nve = len(uninames)
        newgraphs = []
        for g, an in zip(graphs, allnames):
            # Make a copy
            ng = g.copy()

            # Add the missing vertices
            v_missing = list(set(uninames) - set(an))
            ng.add_vertices(v_missing)

            # Reorder vertices to match uninames
            # vertex k -> p[k]
            permutation = [permutation_map[x] for x in ng.vs['name']]
            ng = ng.permute_vertices(permutation)

            newgraphs.append(ng)
    else:
        newgraphs = graphs

    gu = newgraphs[0].union(newgraphs[1:])

    # Graph attributes
    # TODO

    # Vertex attributes
    # TODO

    # Edge attributes
    # TODO

    return gu


def intersection(graphs, byname='auto', keep_all_vertices=True):
    """Graph intersection.

    The intersection of two or more graphs is created. The graphs may have
    identical or overlapping vertex sets. Edges which are included in all
    graphs will be part of the new graph.

    This function keeps the attributes of all graphs. All graph, vertex and
    edge attributes are copied to the result. If an attribute is present in
    multiple graphs and would result a name clash, then this attribute is
    renamed by adding suffixes: _1, _2, etc.

    The 'name' vertex attribute is treated specially if the operation is
    performed based on symbolic vertex names. In this case 'name' must be
    present in all graphs, and it is not renamed in the result graph.

    An error is generated if some input graphs are directed and others are
    undirected.

    @param graph: list of graphs. A lazy sequence is not acceptable.
    @param byname: bool or 'auto' specifying the function behaviour with
      respect to names vertices (i.e. vertices with the 'name' attribute). If
      False, ignore vertex names. If True, merge vertices based on names. If
      'auto', use True if all graphs have named vertices and False otherwise
      (in the latter case, a warning is generated too).
    @keep_all_vertices: bool specifying if vertices that are not present in all
      graphs should be kept in the intersection.
    @return: the intersection graph
    """

    if any(not isinstance(g, GraphBase) for g in graphs):
        raise TypeError('Not all elements are graphs')

    if byname not in (True, False, 'auto'):
        raise ValueError('"byname" should be a bool or "auto"')

    ngr = len(graphs)
    n_named = sum(g.is_named() for g in graphs)
    if byname == 'auto':
        byname = n_named == ngr
        if n_named not in (0, ngr):
            warn("Some, but not all graphs are named, not using vertex names")
    elif byname and (n_named != ngr):
        raise AttributeError("Some graphs are not named")
    # Now we know that byname is only used is all graphs are named

    # Trivial cases
    if ngr == 0:
        return None
    if ngr == 1:
        return graphs[0]
    # Now there are at least two graphs

    if byname:
        allnames = [g.vs['name'] for g in graphs]

        if keep_all_vertices:
            uninames = list(set.union(*(set(an) for an in allnames)))
            permutation_map = {x: i for i, x in enumerate(uninames)}
        else:
            #TODO

        nve = len(uninames)
        newgraphs = []
        for g, an in zip(graphs, allnames):
            # Make a copy
            ng = g.copy()

            if keep_all_vertices:
                # Add the missing vertices
                v_missing = list(set(uninames) - set(an))
                ng.add_vertices(v_missing)

                # Reorder vertices to match uninames
                # vertex k -> p[k]
                permutation = [permutation_map[x] for x in ng.vs['name']]
                ng = ng.permute_vertices(permutation)

            else:
                # Delete the vertices

                #TODO


            newgraphs.append(ng)
    else:
        newgraphs = graphs

    gu = newgraphs[0].intersection(newgraphs[1:])

    # Graph attributes
    # TODO

    # Vertex attributes
    # TODO

    # Edge attributes
    # TODO

    return gu

