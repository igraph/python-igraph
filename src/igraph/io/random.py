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

