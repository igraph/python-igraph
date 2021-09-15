"""
Drawing routines to draw graphs.

This module contains routines to draw graphs on:

  - Cairo surfaces (L{DefaultGraphDrawer})
  - Matplotlib axes (L{MatplotlibGraphDrawer})

It also contains routines to send an igraph graph directly to
(U{Cytoscape<http://www.cytoscape.org>}) using the
(U{CytoscapeRPC plugin<http://gforge.nbic.nl/projects/cytoscaperpc/>}), see
L{CytoscapeGraphDrawer}. L{CytoscapeGraphDrawer} can also fetch the current
network from Cytoscape and convert it to igraph format.
"""

from warnings import warn

from igraph.drawing.baseclasses import AbstractGraphDrawer, AbstractXMLRPCDrawer

__all__ = ("CytoscapeGraphDrawer",)


class CytoscapeGraphDrawer(AbstractXMLRPCDrawer, AbstractGraphDrawer):
    """Graph drawer that sends/receives graphs to/from Cytoscape using
    CytoscapeRPC.

    This graph drawer cooperates with U{Cytoscape<http://www.cytoscape.org>}
    using U{CytoscapeRPC<http://wiki.nbic.nl/index.php/CytoscapeRPC>}.
    You need to install the CytoscapeRPC plugin first and start the
    XML-RPC server on a given port (port 9000 by default) from the
    appropriate Plugins submenu in Cytoscape.

    Graph, vertex and edge attributes are transferred to Cytoscape whenever
    possible (i.e. when a suitable mapping exists between a Python type
    and a Cytoscape type). If there is no suitable Cytoscape type for a
    Python type, the drawer will use a string attribute on the Cytoscape
    side and invoke C{str()} on the Python attributes.

    If an attribute to be created on the Cytoscape side already exists with
    a different type, an underscore will be appended to the attribute name
    to resolve the type conflict.

    You can use the C{network_id} attribute of this class to figure out the
    network ID of the last graph drawn with this drawer.
    """

    def __init__(self, url="http://localhost:9000/Cytoscape"):
        """Constructs a Cytoscape graph drawer using the XML-RPC interface
        of Cytoscape at the given URL."""
        super().__init__(url, "Cytoscape")
        self.network_id = None

    def draw(self, graph, name="Network from igraph", create_view=True, *args, **kwds):
        """Sends the given graph to Cytoscape as a new network.

        @param name: the name of the network in Cytoscape.
        @param create_view: whether to create a view for the network
          in Cytoscape.The default is C{True}.
        @keyword node_ids: specifies the identifiers of the nodes to
          be used in Cytoscape. This must either be the name of a
          vertex attribute or a list specifying the identifiers, one
          for each node in the graph. The default is C{None}, which
          simply uses the vertex index for each vertex."""
        from xmlrpc.client import Fault

        # Positional arguments are not used
        if args:
            warn(
                "Positional arguments to plot functions are ignored "
                "and will be deprecated soon.",
                DeprecationWarning,
            )

        cy = self.service

        # Create the network
        if not create_view:
            try:
                network_id = cy.createNetwork(name, False)
            except Fault:
                warn(
                    "CytoscapeRPC too old, cannot create network without view."
                    " Consider upgrading CytoscapeRPC to use this feature."
                )
                network_id = cy.createNetwork(name)
        else:
            network_id = cy.createNetwork(name)
        self.network_id = network_id

        # Create the nodes
        if "node_ids" in kwds:
            node_ids = kwds["node_ids"]
            if isinstance(node_ids, str):
                node_ids = graph.vs[node_ids]
        else:
            node_ids = list(range(graph.vcount()))
        node_ids = [str(identifier) for identifier in node_ids]
        cy.createNodes(network_id, node_ids)

        # Create the edges
        edgelists = [[], []]
        for v1, v2 in graph.get_edgelist():
            edgelists[0].append(node_ids[v1])
            edgelists[1].append(node_ids[v2])
        edge_ids = cy.createEdges(
            network_id,
            edgelists[0],
            edgelists[1],
            ["unknown"] * graph.ecount(),
            [graph.is_directed()] * graph.ecount(),
            False,
        )

        if "layout" in kwds:
            # Calculate/get the layout of the graph
            layout = self.ensure_layout(kwds["layout"], graph)
            size = 100 * graph.vcount() ** 0.5
            layout.fit_into((size, size), keep_aspect_ratio=True)
            layout.translate(-size / 2.0, -size / 2.0)
            cy.setNodesPositions(network_id, node_ids, *list(zip(*list(layout))))
        else:
            # Ask Cytoscape to perform the default layout so the user can
            # at least see something in Cytoscape while the attributes are
            # being transferred
            cy.performDefaultLayout(network_id)

        # Send the network attributes
        attr_names = set(cy.getNetworkAttributeNames())
        for attr in graph.attributes():
            cy_type, value = self.infer_cytoscape_type([graph[attr]])
            value = value[0]
            if value is None:
                continue

            # Resolve type conflicts (if any)
            try:
                while (
                    attr in attr_names and cy.getNetworkAttributeType(attr) != cy_type
                ):
                    attr += "_"
            except Fault:
                # getNetworkAttributeType is not available in some older versions
                # so we simply pass here
                pass
            cy.addNetworkAttributes(attr, cy_type, {network_id: value})

        # Send the node attributes
        attr_names = set(cy.getNodeAttributeNames())
        for attr in graph.vertex_attributes():
            cy_type, values = self.infer_cytoscape_type(graph.vs[attr])
            values = dict(pair for pair in zip(node_ids, values) if pair[1] is not None)
            # Resolve type conflicts (if any)
            while attr in attr_names and cy.getNodeAttributeType(attr) != cy_type:
                attr += "_"
            # Send the attribute values
            cy.addNodeAttributes(attr, cy_type, values, True)

        # Send the edge attributes
        attr_names = set(cy.getEdgeAttributeNames())
        for attr in graph.edge_attributes():
            cy_type, values = self.infer_cytoscape_type(graph.es[attr])
            values = dict(pair for pair in zip(edge_ids, values) if pair[1] is not None)
            # Resolve type conflicts (if any)
            while attr in attr_names and cy.getEdgeAttributeType(attr) != cy_type:
                attr += "_"
            # Send the attribute values
            cy.addEdgeAttributes(attr, cy_type, values)

    def fetch(self, name=None, directed=False, keep_canonical_names=False):
        """Fetches the network with the given name from Cytoscape.

        When fetching networks from Cytoscape, the C{canonicalName} attributes
        of vertices and edges are not converted by default. Use the
        C{keep_canonical_names} parameter to retrieve these attributes as well.

        @param name: the name of the network in Cytoscape.
        @param directed: whether the network is directed.
        @param keep_canonical_names: whether to keep the C{canonicalName}
            vertex/edge attributes that are added automatically by Cytoscape
        @return: an appropriately constructed igraph L{Graph}."""
        from igraph import Graph

        cy = self.service

        # Check the version number. Anything older than 1.3 is bad.
        version = cy.version()
        if " " in version:
            version = version.split(" ")[0]
        version = tuple(map(int, version.split(".")[:2]))
        if version < (1, 3):
            raise NotImplementedError(
                "CytoscapeGraphDrawer requires Cytoscape-RPC 1.3 or newer"
            )

        # Find out the ID of the network we are interested in
        if name is None:
            network_id = cy.getNetworkID()
        else:
            network_id = [k for k, v in cy.getNetworkList().items() if v == name]
            if not network_id:
                raise ValueError("no such network: %r" % name)
            elif len(network_id) > 1:
                raise ValueError("more than one network exists with name: %r" % name)
            network_id = network_id[0]

        # Fetch the list of all the nodes and edges
        vertices = cy.getNodes(network_id)
        edges = cy.getEdges(network_id)
        n, m = len(vertices), len(edges)

        # Fetch the graph attributes
        graph_attrs = cy.getNetworkAttributes(network_id)

        # Fetch the vertex attributes
        vertex_attr_names = cy.getNodeAttributeNames()
        vertex_attrs = {}
        for attr_name in vertex_attr_names:
            if attr_name == "canonicalName" and not keep_canonical_names:
                continue
            has_attr = cy.nodesHaveAttribute(attr_name, vertices)
            filtered = [idx for idx, ok in enumerate(has_attr) if ok]
            values = cy.getNodesAttributes(
                attr_name, [name for name, ok in zip(vertices, has_attr) if ok]
            )
            attrs = [None] * n
            for idx, value in zip(filtered, values):
                attrs[idx] = value
            vertex_attrs[attr_name] = attrs

        # Fetch the edge attributes
        edge_attr_names = cy.getEdgeAttributeNames()
        edge_attrs = {}
        for attr_name in edge_attr_names:
            if attr_name == "canonicalName" and not keep_canonical_names:
                continue
            has_attr = cy.edgesHaveAttribute(attr_name, edges)
            filtered = [idx for idx, ok in enumerate(has_attr) if ok]
            values = cy.getEdgesAttributes(
                attr_name, [name for name, ok in zip(edges, has_attr) if ok]
            )
            attrs = [None] * m
            for idx, value in zip(filtered, values):
                attrs[idx] = value
            edge_attrs[attr_name] = attrs

        # Create a vertex name index
        vertex_name_index = dict((v, k) for k, v in enumerate(vertices))
        del vertices

        # Remap the edges list to numeric IDs
        edge_list = []
        for edge in edges:
            parts = edge.split()
            edge_list.append((vertex_name_index[parts[0]], vertex_name_index[parts[2]]))
        del edges

        return Graph(
            n,
            edge_list,
            directed=directed,
            graph_attrs=graph_attrs,
            vertex_attrs=vertex_attrs,
            edge_attrs=edge_attrs,
        )

    @staticmethod
    def infer_cytoscape_type(values):
        """Returns a Cytoscape type that can be used to represent all the
        values in `values` and an appropriately converted copy of `values` that
        is suitable for an XML-RPC call.  Note that the string type in
        Cytoscape is used as a catch-all type; if no other type fits, attribute
        values will be converted to string and then posted to Cytoscape.

        ``None`` entries are allowed in `values`, they will be ignored on the
        Cytoscape side.
        """
        types = [type(value) for value in values if value is not None]
        if all(t == bool for t in types):
            return "BOOLEAN", values
        if all(issubclass(t, (int, int)) for t in types):
            return "INTEGER", values
        if all(issubclass(t, float) for t in types):
            return "FLOATING", values
        return "STRING", [
            str(value) if not isinstance(value, str) else value for value in values
        ]


#####################################################################


class GephiGraphStreamingDrawer(AbstractGraphDrawer):
    """Graph drawer that sends a graph to a file-like object (e.g., socket, URL
    connection, file) using the Gephi graph streaming format.

    The Gephi graph streaming format is a simple JSON-based format that can be used
    to post mutations to a graph (i.e. node and edge additions, removals and updates)
    to a remote component. For instance, one can open up Gephi
    (U{http://www.gephi.org}), install the Gephi graph streaming plugin and then
    send a graph from igraph straight into the Gephi window by using
    C{GephiGraphStreamingDrawer} with the appropriate URL where Gephi is
    listening.

    The C{connection} property exposes the L{GephiConnection} that the drawer
    uses. The drawer also has a property called C{streamer} which exposes the underlying
    L{GephiGraphStreamer} that is responsible for generating the JSON objects,
    encoding them and writing them to a file-like object. If you want to customize
    the encoding process, this is the object where you can tweak things to your taste.
    """

    def __init__(self, conn=None, *args, **kwds):
        """Constructs a Gephi graph streaming drawer that will post graphs to the
        given Gephi connection. If C{conn} is C{None}, the remaining arguments of
        the constructor are forwarded intact to the constructor of
        L{GephiConnection} in order to create a connection. This means that any of
        the following are valid:

          - C{GephiGraphStreamingDrawer()} will construct a drawer that connects to
            workspace 0 of the local Gephi instance on port 8080.

          - C{GephiGraphStreamingDrawer(workspace=2)} will connect to workspace 2
            of the local Gephi instance on port 8080.

          - C{GephiGraphStreamingDrawer(port=1234)} will connect to workspace 0
            of the local Gephi instance on port 1234.

          - C{GephiGraphStreamingDrawer(host="remote", port=1234, workspace=7)}
            will connect to workspace 7 of the Gephi instance on host C{remote},
            port 1234.

          - C{GephiGraphStreamingDrawer(url="http://remote:1234/workspace7)} is
            the same as above, but with an explicit URL.
        """
        super().__init__()

        from igraph.remote.gephi import GephiGraphStreamer, GephiConnection

        self.connection = conn or GephiConnection(*args, **kwds)
        self.streamer = GephiGraphStreamer()

    def draw(self, graph, *args, **kwds):
        """Draws (i.e. sends) the given graph to the destination of the drawer using
        the Gephi graph streaming API.

        The following keyword arguments are allowed:

            - ``encoder`` lets one specify an instance of ``json.JSONEncoder`` that
              will be used to encode the JSON objects.
        """
        # Positional arguments are not used
        if args:
            warn(
                "Positional arguments to plot functions are ignored "
                "and will be deprecated soon.",
                DeprecationWarning,
            )

        self.streamer.post(graph, self.connection, encoder=kwds.get("encoder"))
