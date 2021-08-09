"""
Abstract base classes for the drawing routines.
"""

from abc import ABCMeta, abstractmethod
from math import atan2, pi

from .text import TextAlignment

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


class AbstractEdgeDrawer(metaclass=ABCMeta):
    """Abstract edge drawer object from which all concrete edge drawer
    implementations are derived.
    """

    @staticmethod
    def _curvature_to_float(value):
        """Converts values given to the 'curved' edge style argument
        in plotting calls to floating point values."""
        if value is None or value is False:
            return 0.0
        if value is True:
            return 0.5
        return float(value)

    @abstractmethod
    def draw_directed_edge(self, edge, src_vertex, dest_vertex):
        """Draws a directed edge.

        @param edge: the edge to be drawn. Visual properties of the edge
          are defined by the attributes of this object.
        @param src_vertex: the source vertex. Visual properties are defined
          by the attributes of this object.
        @param dest_vertex: the source vertex. Visual properties are defined
          by the attributes of this object.
        """
        raise NotImplementedError

    @abstractmethod
    def draw_undirected_edge(self, edge, src_vertex, dest_vertex):
        """Draws an undirected edge.

        @param edge: the edge to be drawn. Visual properties of the edge
          are defined by the attributes of this object.
        @param src_vertex: the source vertex. Visual properties are defined
          by the attributes of this object.
        @param dest_vertex: the source vertex. Visual properties are defined
          by the attributes of this object.
        """
        raise NotImplementedError

    def get_label_position(self, edge, src_vertex, dest_vertex):
        """Returns the position where the label of an edge should be drawn. The
        default implementation returns the midpoint of the edge and an alignment
        that tries to avoid overlapping the label with the edge.

        @param edge: the edge to be drawn. Visual properties of the edge
          are defined by the attributes of this object.
        @param src_vertex: the source vertex. Visual properties are given
          again as attributes.
        @param dest_vertex: the target vertex. Visual properties are given
          again as attributes.
        @return: a tuple containing two more tuples: the desired position of the
          label and the desired alignment of the label, where the position is
          given as C{(x, y)} and the alignment is given as C{(horizontal, vertical)}.
          Members of the alignment tuple are taken from constants in the
          L{TextAlignment} class.
        """
        # TODO: curved edges don't play terribly well with this function,
        # we could try to get the mid point of the actual curved arrow
        # (Bezier curve) and use that.

        # Determine the angle of the line
        dx = dest_vertex.position[0] - src_vertex.position[0]
        dy = dest_vertex.position[1] - src_vertex.position[1]
        if dx != 0 or dy != 0:
            # Note that we use -dy because the Y axis points downwards
            angle = atan2(-dy, dx) % (2 * pi)
        else:
            angle = None

        # Determine the midpoint
        pos = (
            (src_vertex.position[0] + dest_vertex.position[0]) / 2.0,
            (src_vertex.position[1] + dest_vertex.position[1]) / 2,
        )

        # Determine the alignment based on the angle
        pi4 = pi / 4
        if angle is None:
            halign, valign = TextAlignment.CENTER, TextAlignment.CENTER
        else:
            index = int((angle / pi4) % 8)
            halign = [
                TextAlignment.RIGHT,
                TextAlignment.RIGHT,
                TextAlignment.RIGHT,
                TextAlignment.RIGHT,
                TextAlignment.LEFT,
                TextAlignment.LEFT,
                TextAlignment.LEFT,
                TextAlignment.LEFT,
            ][index]
            valign = [
                TextAlignment.BOTTOM,
                TextAlignment.CENTER,
                TextAlignment.CENTER,
                TextAlignment.TOP,
                TextAlignment.TOP,
                TextAlignment.CENTER,
                TextAlignment.CENTER,
                TextAlignment.BOTTOM,
            ][index]

        return pos, (halign, valign)


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
