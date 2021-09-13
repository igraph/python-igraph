def _export_graph_to_networkx(graph, create_using=None):
    """Converts the graph to networkx format.

    @param create_using: specifies which NetworkX graph class to use when
        constructing the graph. C{None} means to let igraph infer the most
        appropriate class based on whether the graph is directed and whether
        it has multi-edges.
    """
    import networkx as nx

    # Graph: decide on directness and mutliplicity
    if create_using is None:
        if graph.has_multiple():
            cls = nx.MultiDiGraph if graph.is_directed() else nx.MultiGraph
        else:
            cls = nx.DiGraph if graph.is_directed() else nx.Graph
    else:
        cls = create_using

    # Graph attributes
    kw = {x: graph[x] for x in graph.attributes()}
    g = cls(**kw)

    # Nodes and node attributes
    for i, v in enumerate(graph.vs):
        # TODO: use _nx_name if the attribute is present so we can achieve
        # a lossless round-trip in terms of vertex names
        g.add_node(i, **v.attributes())

    # Edges and edge attributes
    for edge in graph.es:
        g.add_edge(edge.source, edge.target, **edge.attributes())

    return g


def _construct_graph_from_networkx(cls, g):
    """Converts the graph from networkx

    Vertex names will be converted to "_nx_name" attribute and the vertices
    will get new ids from 0 up (as standard in igraph).

    @param g: networkx Graph or DiGraph
    """
    # Graph attributes
    gattr = dict(g.graph)

    # Nodes
    vnames = list(g.nodes)
    vattr = {"_nx_name": vnames}
    vcount = len(vnames)
    vd = {v: i for i, v in enumerate(vnames)}

    # NOTE: we do not need a special class for multigraphs, it is taken
    # care for at the edge level rather than at the graph level.
    graph = cls(
        n=vcount, directed=g.is_directed(), graph_attrs=gattr, vertex_attrs=vattr
    )

    # Node attributes
    for v, datum in g.nodes.data():
        for key, val in list(datum.items()):
            graph.vs[vd[v]][key] = val

    # Edges and edge attributes
    eattr_names = {name for (_, _, data) in g.edges.data() for name in data}
    eattr = {name: [] for name in eattr_names}
    edges = []
    for (u, v, data) in g.edges.data():
        edges.append((vd[u], vd[v]))
        for name in eattr_names:
            eattr[name].append(data.get(name))

    graph.add_edges(edges, eattr)

    return graph

def _export_graph_to_graph_tool(
    graph, graph_attributes=None, vertex_attributes=None, edge_attributes=None
):
    """Converts the graph to graph-tool

    Data types: graph-tool only accepts specific data types. See the
    following web page for a list:

    https://graph-tool.skewed.de/static/doc/quickstart.html

    Note: because of the restricted data types in graph-tool, vertex and
    edge attributes require to be type-consistent across all vertices or
    edges. If you set the property for only some vertices/edges, the other
    will be tagged as None in python-igraph, so they can only be converted
    to graph-tool with the type 'object' and any other conversion will
    fail.

    @param graph_attributes: dictionary of graph attributes to transfer.
      Keys are attributes from the graph, values are data types (see
      below). C{None} means no graph attributes are transferred.
    @param vertex_attributes: dictionary of vertex attributes to transfer.
      Keys are attributes from the vertices, values are data types (see
      below). C{None} means no vertex attributes are transferred.
    @param edge_attributes: dictionary of edge attributes to transfer.
      Keys are attributes from the edges, values are data types (see
      below). C{None} means no vertex attributes are transferred.
    """
    import graph_tool as gt

    # Graph
    g = gt.Graph(directed=graph.is_directed())

    # Nodes
    vc = graph.vcount()
    g.add_vertex(vc)

    # Graph attributes
    if graph_attributes is not None:
        for x, dtype in list(graph_attributes.items()):
            # Strange syntax for setting internal properties
            gprop = g.new_graph_property(str(dtype))
            g.graph_properties[x] = gprop
            g.graph_properties[x] = graph[x]

    # Vertex attributes
    if vertex_attributes is not None:
        for x, dtype in list(vertex_attributes.items()):
            # Create a new vertex property
            g.vertex_properties[x] = g.new_vertex_property(str(dtype))
            # Fill the values from the igraph.Graph
            for i in range(vc):
                g.vertex_properties[x][g.vertex(i)] = graph.vs[i][x]

    # Edges and edge attributes
    if edge_attributes is not None:
        for x, dtype in list(edge_attributes.items()):
            g.edge_properties[x] = g.new_edge_property(str(dtype))
    for edge in graph.es:
        e = g.add_edge(edge.source, edge.target)
        if edge_attributes is not None:
            for x, dtype in list(edge_attributes.items()):
                prop = edge.attributes().get(x, None)
                g.edge_properties[x][e] = prop

    return g


def _construct_graph_from_graph_tool(cls, g):
    """Converts the graph from graph-tool

    @param g: graph-tool Graph
    """
    # Graph attributes
    gattr = dict(g.graph_properties)

    # Nodes
    vcount = g.num_vertices()

    # Graph
    graph = cls(n=vcount, directed=g.is_directed(), graph_attrs=gattr)

    # Node attributes
    for key, val in g.vertex_properties.items():
        prop = val.get_array()
        for i in range(vcount):
            graph.vs[i][key] = prop[i]

    # Edges and edge attributes
    # NOTE: graph-tool is quite strongly typed, so each property is always
    # defined for all edges, using default values for the type. E.g. for a
    # string property/attribute the missing edges get an empty string.
    edges = []
    eattr_names = list(g.edge_properties)
    eattr = {name: [] for name in eattr_names}
    for e in g.edges():
        edges.append((int(e.source()), int(e.target())))
        for name, attr_map in g.edge_properties.items():
            eattr[name].append(attr_map[e])

    graph.add_edges(edges, eattr)

    return graph
