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
from igraph.datatypes import UniqueIdGenerator


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
    directd=False,
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
            n = max(n, source, *sequence)
            for target, edge_attrs in target_dict.items():
                edge_list.append((source, target))
                edge_attribute_list.append(edge_attrs)

    # Construct graph without edge attributes
    graph = cls(n, edge_list, directed, {}, vertex_attributes, {})

    # Add edge attributes
    for edge, edge_attrs in zip(graph.es, edge_attribute_list):
        for key, val in edge_attrs:
            edge[key] = val

    return graph
