from igraph._igraph import (
    Vertex,
    Edge,
)
from igraph.seq import VertexSeq, EdgeSeq


__all__ = (
    "__iadd__",
    "__add__",
    "__and__",
    "__isub__",
    "__sub__",
    "__mul__",
    "__or__",
)


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
    # Deferred import to avoid cycles
    from igraph import Graph

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
    # Deferred import to avoid cycles
    from igraph import Graph

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
    # Deferred import to avoid cycles
    from igraph import Graph

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
    # Deferred import to avoid cycles
    from igraph import Graph

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


def __or__(self, other):
    """Graph union operator.

    @param other: the other graph to take the union with.
    @return: the union graph.
    """
    # Deferred import to avoid cycles
    from igraph import Graph

    if isinstance(other, Graph):
        return self.union(other)
    else:
        return NotImplemented
