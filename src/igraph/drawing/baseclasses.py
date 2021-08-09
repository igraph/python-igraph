"""
Abstract base classes for the drawing routines.
"""

from abc import ABCMeta, abstractmethod

#####################################################################


class AbstractDrawer(metaclass=ABCMeta):
    """Abstract class that serves as a base class for anything that
    draws an igraph object."""

    @abstractmethod
    def draw(self, *args, **kwds):
        """Abstract method, must be implemented in derived classes."""
        raise NotImplementedError


#####################################################################


class AbstractXMLRPCDrawer(AbstractDrawer):
    """Abstract drawer that uses a remote service via XML-RPC
    to draw something on a remote display.
    """

    def __init__(self, url, service=None):
        """Constructs an abstract drawer using the XML-RPC service
        at the given URL.

        @param url: the URL where the XML-RPC calls for the service should
          be addressed to.
        @param service: the name of the service at the XML-RPC address. If
          C{None}, requests will be directed to the server proxy object
          constructed by C{xmlrpclib.ServerProxy}; if not C{None}, the
          given attribute will be looked up in the server proxy object.
        """
        import xmlrpc.client

        url = self._resolve_hostname(url)
        self.server = xmlrpc.client.ServerProxy(url)
        if service is None:
            self.service = self.server
        else:
            self.service = getattr(self.server, service)

    @staticmethod
    def _resolve_hostname(url):
        """Parses the given URL, resolves the hostname to an IP address
        and returns a new URL with the resolved IP address. This speeds
        up things big time on Mac OS X where an IP lookup would be
        performed for every XML-RPC call otherwise."""
        from urllib.parse import urlparse, urlunparse
        import re

        url_parts = urlparse(url)
        hostname = url_parts.netloc
        if re.match("[0-9.:]+$", hostname):
            # the hostname is already an IP address, possibly with a port
            return url

        from socket import gethostbyname

        if ":" in hostname:
            hostname = hostname[0 : hostname.index(":")]
        hostname = gethostbyname(hostname)
        if url_parts.port is not None:
            hostname = "%s:%d" % (hostname, url_parts.port)
        url_parts = list(url_parts)
        url_parts[1] = hostname
        return urlunparse(url_parts)


#####################################################################


class AbstractVertexDrawer(AbstractDrawer):
    """Abstract vertex drawer object from which all concrete vertex drawer
    implementations are derived."""

    def __init__(self, palette, layout):
        """Constructs the vertex drawer and associates it to the given
        palette.

        @param palette: the palette that can be used to map integer
                        color indices to colors when drawing vertices
        @param layout:  the layout of the vertices in the graph being drawn
        """
        self.layout = layout
        self.palette = palette

    @abstractmethod
    def draw(self, visual_vertex, vertex, coords):
        """Draws the given vertex.

        @param visual_vertex: object specifying the visual properties of the
            vertex. Its structure is defined by the VisualVertexBuilder of the
            L{CairoGraphDrawer}; see its source code.
        @param vertex: the raw igraph vertex being drawn
        @param coords: the X and Y coordinates of the vertex as specified by the
            layout algorithm, scaled into the bounding box.
        """
        raise NotImplementedError
