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

from igraph.utils import (
    named_temporary_file,
)


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
