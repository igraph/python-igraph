"""
Drawing and plotting routines for IGraph.

Plotting is dependent on the C{pycairo} or C{cairocffi} libraries that provide
Python bindings to the popular U{Cairo library<http://www.cairographics.org>}.
This means that if you don't have U{pycairo<http://www.cairographics.org/pycairo>}
or U{cairocffi<http://cairocffi.readthedocs.io>} installed, you won't be able
to use the plotting capabilities. However, you can still use L{Graph.write_svg}
to save the graph to an SVG file and view it from
U{Mozilla Firefox<http://www.mozilla.org/firefox>} (free) or edit it in
U{Inkscape<http://www.inkscape.org>} (free), U{Skencil<http://www.skencil.org>}
(formerly known as Sketch, also free) or Adobe Illustrator.

Whenever the documentation refers to the C{pycairo} library, you can safely
replace it with C{cairocffi} as the two are API-compatible.
"""


from warnings import warn

import os
import platform
import time

from io import BytesIO
from igraph.configuration import Configuration
from igraph.drawing.colors import Palette, palettes
from igraph.drawing.graph import (
    CairoGraphDrawer,
    MatplotlibGraphDrawer,
    DefaultGraphDrawer,
)
from igraph.drawing.utils import (
    BoundingBox,
    Point,
    Rectangle,
    find_cairo,
    find_matplotlib,
)
from igraph.utils import _is_running_in_ipython, named_temporary_file

__all__ = (
    "BoundingBox",
    "CairoGraphDrawer",
    "MatplotlibGraphDrawer",
    "DefaultGraphDrawer",
    "Plot",
    "Point", "Rectangle",
    "plot",
)

cairo = find_cairo()
mpl, plt = find_matplotlib()

#####################################################################


class CairoPlot:
    """Class representing an arbitrary plot.

    Objects that you can plot include graphs, matrices, palettes, clusterings,
    covers, and dengrograms.

    Two main backends are supported: Cairo and matplotlib.

    In Cairo, every plot has an associated surface object. The surface is an
    instance of C{cairo.Surface}, a member of the C{pycairo} library. The
    surface itself provides a unified API to various plotting targets like SVG
    files, X11 windows, PostScript files, PNG files and so on. C{igraph} does
    not usually know on which surface it is plotting at each point in time,
    since C{pycairo} takes care of the actual drawing. Everything that's
    supported by C{pycairo} should be supported by this class as well.

    Current Cairo surfaces include:

      - C{cairo.GlitzSurface} -- OpenGL accelerated surface for the X11
        Window System.

      - C{cairo.ImageSurface} -- memory buffer surface. Can be written to a
        C{PNG} image file.

      - C{cairo.PDFSurface} -- PDF document surface.

      - C{cairo.PSSurface} -- PostScript document surface.

      - C{cairo.SVGSurface} -- SVG (Scalable Vector Graphics) document surface.

      - C{cairo.Win32Surface} -- Microsoft Windows screen rendering.

      - C{cairo.XlibSurface} -- X11 Window System screen rendering.

    If you create a C{Plot} object with a string given as the target surface,
    the string will be treated as a filename, and its extension will decide
    which surface class will be used. Please note that not all surfaces might
    be available, depending on your C{pycairo} installation.

    In matplotlib, every plot has an associated Axes object, which provides a
    context. Matplotlib itself supports various backends with their own
    surfaces.

    A C{Plot} has an assigned default palette (see L{igraph.drawing.colors.Palette})
    which is used for plotting objects.

    A C{Plot} object also has a list of objects to be plotted with their
    respective bounding boxes, palettes and opacities. Bounding boxes are
    specific to the Cairo backend and will be None in the matplotlib backend.
    Palettes assigned to an object override the default palette of the plot.
    Objects can be added by the L{Plot.add} method and removed by the
    L{Plot.remove} method.
    """

    def __init__(
            self,
            target=None,
            bbox=None,
            palette=None,
            background=None,
            margin=20,
            ):
        """Creates a new plot using Cairo or Matplotlib.

        @param target: the target surface to write to. It can be one of the
          following types:

            - C{None} -- a Cairo surface will be created and the object will be
              plotted there.

            - C{cairo.Surface} -- the given Cairo surface will be used.

            - C{string} -- a file with the given name will be created and an
              appropriate Cairo surface will be attached to it.

            - C{plt.Axes} -- the given matplotlib Axes will be used.

        @param bbox: the bounding box of the surface (only for Cairo). It is
          interpreted differently with different surfaces: PDF and PS surfaces
          will treat it as points (1 point = 1/72 inch). Image surfaces will
          treat it as pixels. SVG surfaces will treat it as an abstract
          unit, but it will mostly be interpreted as pixels when viewing
          the SVG file in Firefox.

        @param palette: the palette primarily used on the plot if the
          added objects do not specify a private palette. Must be either
          an L{igraph.drawing.colors.Palette} object or a string referring
          to a valid key of C{igraph.drawing.colors.palettes} (see module
          L{igraph.drawing.colors}) or C{None}. In the latter case, the default
          palette given by the configuration key C{plotting.palette} is used.

        @param background: the background color. If C{None}, the background
          will be transparent for Cairo and your default style for matplotlib.
          You can use any color specification here that is understood by
          L{igraph.drawing.colors.color_name_to_rgba}.
        """

        self._filename = None
        self._need_tmpfile = False

        if bbox is None:
            self.bbox = BoundingBox(600, 600)
        elif isinstance(bbox, tuple) or isinstance(bbox, list):
            self.bbox = BoundingBox(bbox)
        else:
            self.bbox = bbox
        self.bbox = self.bbox.contract(margin)

        # Several Windows-specific hacks will be used from now on, thanks
        # to Dale Hunscher for debugging and fixing all that stuff
        self._windows_hacks = "Windows" in platform.platform()

        if palette is None:
            config = Configuration.instance()
            palette = config["plotting.palette"]
        if not isinstance(palette, Palette):
            palette = palettes[palette]
        self._palette = palette

        if target is None:
            self._need_tmpfile = True
            self._surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, int(self.bbox.width), int(self.bbox.height)
            )
        elif isinstance(target, cairo.Surface):
            self._surface = target
        else:
            self._filename = target
            _, ext = os.path.splitext(target)
            ext = ext.lower()
            if ext == ".pdf":
                self._surface = cairo.PDFSurface(
                    target, self.bbox.width, self.bbox.height
                )
            elif ext == ".ps" or ext == ".eps":
                self._surface = cairo.PSSurface(
                    target, self.bbox.width, self.bbox.height
                )
            elif ext == ".png":
                self._surface = cairo.ImageSurface(
                    cairo.FORMAT_ARGB32, int(self.bbox.width), int(self.bbox.height)
                )
            elif ext == ".svg":
                self._surface = cairo.SVGSurface(
                    target, self.bbox.width, self.bbox.height
                )
            else:
                raise ValueError("image format not handled by Cairo: %s" % ext)

        self._ctx = cairo.Context(self._surface)

        self._surface_was_created = not isinstance(target, cairo.Surface)
        self._objects = []
        self._is_dirty = False

        if background is None:
            background = "white"
        self.background = background

    def add(self, obj, bbox=None, palette=None, opacity=1.0, *args, **kwds):
        """Adds an object to the plot.

        Arguments not specified here are stored and passed to the object's
        plotting function when necessary. Since you are most likely interested
        in the arguments acceptable by graphs, see L{Graph.__plot__} for more
        details.

        @param obj: the object to be added
        @param bbox: the bounding box of the object. If C{None}, the object
          will fill the entire area of the plot.
        @param palette: the color palette used for drawing the object. If the
          object tries to get a color assigned to a positive integer, it
          will use this palette. If C{None}, defaults to the global palette
          of the plot.
        @param opacity: the opacity of the object being plotted, in the range
          0.0-1.0

        @see: Graph.__plot__
        """
        if opacity < 0.0 or opacity > 1.0:
            raise ValueError("opacity must be between 0.0 and 1.0")
        if bbox is None:
            bbox = self.bbox
        if (bbox is not None) and (not isinstance(bbox, BoundingBox)):
            bbox = BoundingBox(bbox)
        self._objects.append((obj, bbox, palette, opacity, args, kwds))
        self.mark_dirty()

    @property
    def background(self):
        """Returns the background color of the plot. C{None} means a
        transparent background.
        """
        return self._background

    @background.setter
    def background(self, color):
        """Sets the background color of the plot. C{None} means a
        transparent background. You can use any color specification here
        that is understood by the C{get} method of the current palette
        or by L{igraph.drawing.colors.color_name_to_rgb}.
        """
        if color is None:
            self._background = None
        else:
            self._background = self._palette.get(color)

    def remove(self, obj, bbox=None, idx=1):
        """Removes an object from the plot.

        If the object has been added multiple times and no bounding box
        was specified, it removes the instance which occurs M{idx}th
        in the list of identical instances of the object.

        @param obj: the object to be removed
        @param bbox: optional bounding box specification for the object.
          If given, only objects with exactly this bounding box will be
          considered.
        @param idx: if multiple objects match the specification given by
          M{obj} and M{bbox}, only the M{idx}th occurrence will be removed.
        @return: C{True} if the object has been removed successfully,
          C{False} if the object was not on the plot at all or M{idx}
          was larger than the count of occurrences
        """
        for i in range(len(self._objects)):
            current_obj, current_bbox = self._objects[i][0:2]
            if current_obj is obj and (bbox is None or current_bbox == bbox):
                idx -= 1
                if idx == 0:
                    self._objects[i : (i + 1)] = []
                    self.mark_dirty()
                    return True
        return False

    def mark_dirty(self):
        """Marks the plot as dirty (should be redrawn)"""
        self._is_dirty = True

    def redraw(self, context=None):
        """Redraws the plot"""
        ctx = context or self._ctx
        if self._background is not None:
            ctx.set_source_rgba(*self._background)
            ctx.rectangle(0, 0, self.bbox.width, self.bbox.height)
            ctx.fill()

        for obj, bbox, palette, opacity, args, kwds in self._objects:
            if palette is None:
                palette = getattr(obj, "_default_palette", self._palette)
            plotter = getattr(obj, "__plot__", None)
            if plotter is None:
                warn("%s does not support plotting" % (obj,))
            else:
                if opacity < 1.0:
                    ctx.push_group()
                else:
                    ctx.save()
                plotter('cairo', ctx, bbox, palette, *args, **kwds)
                if opacity < 1.0:
                    ctx.pop_group_to_source()
                    ctx.paint_with_alpha(opacity)
                else:
                    ctx.restore()

        self._is_dirty = False

    def save(self, fname=None):
        """Saves the plot.

        @param fname: the filename to save to. It is ignored if the surface
          of the plot is not an C{ImageSurface}.
        """
        if self._is_dirty:
            self.redraw()
        if isinstance(self._surface, cairo.ImageSurface):
            if fname is None and self._need_tmpfile:
                with named_temporary_file(prefix="igraph", suffix=".png") as fname:
                    self._surface.write_to_png(fname)
                    return None

            fname = fname or self._filename
            if fname is None:
                raise ValueError(
                    "no file name is known for the surface " + "and none given"
                )
            return self._surface.write_to_png(fname)

        if fname is not None:
            warn("filename is ignored for surfaces other than ImageSurface")

        self._ctx.show_page()
        self._surface.finish()

    def show(self):
        """Saves the plot to a temporary file and shows it.

        This method is deprecated from python-igraph 0.9.1 and will be removed in
        version 0.10.0.

        @deprecated: Opening an image viewer with a temporary file never worked
            reliably across platforms.
        """
        warn("Plot.show() is deprecated from python-igraph 0.9.1", DeprecationWarning)

        if not isinstance(self._surface, cairo.ImageSurface):
            sur = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, int(self.bbox.width), int(self.bbox.height)
            )
            ctx = cairo.Context(sur)
            self.redraw(ctx)
        else:
            sur = self._surface
            ctx = self._ctx
            if self._is_dirty:
                self.redraw(ctx)

        with named_temporary_file(prefix="igraph", suffix=".png") as tmpfile:
            sur.write_to_png(tmpfile)
            config = Configuration.instance()
            imgviewer = config["apps.image_viewer"]
            if not imgviewer:
                # No image viewer was given and none was detected. This
                # should only happen on unknown platforms.
                plat = platform.system()
                raise NotImplementedError(
                    "showing plots is not implemented on this platform: %s" % plat
                )
            else:
                os.system("%s %s" % (imgviewer, tmpfile))
                if platform.system() == "Darwin" or self._windows_hacks:
                    # On Mac OS X and Windows, launched applications are likely to
                    # fork and give control back to Python immediately.
                    # Chances are that the temporary image file gets removed
                    # before the image viewer has a chance to open it, so
                    # we wait here a little bit. Yes, this is quite hackish :(
                    time.sleep(5)

    def _repr_svg_(self):
        """Returns an SVG representation of this plot as a string.

        This method is used by IPython to display this plot inline.
        """
        io = BytesIO()
        # Create a new SVG surface and use that to get the SVG representation,
        # which will end up in io
        surface = cairo.SVGSurface(io, self.bbox.width, self.bbox.height)
        context = cairo.Context(surface)
        # Plot the graph on this context
        self.redraw(context)
        # No idea why this is needed but python crashes without
        context.show_page()
        surface.finish()
        # Return the raw SVG representation
        result = io.getvalue()
        if hasattr(result, "encode"):
            result = result.encode("utf-8")  # for Python 2.x
        else:
            result = result.decode("utf-8")  # for Python 3.x

        return result, {"isolated": True}  # put it inside an iframe

    @property
    def bounding_box(self):
        """Returns the bounding box of the Cairo surface as a
        L{BoundingBox} object"""
        return BoundingBox(self.bbox)

    @property
    def height(self):
        """Returns the height of the Cairo surface on which the plot
        is drawn"""
        return self.bbox.height

    @property
    def surface(self):
        """Returns the Cairo surface on which the plot is drawn"""
        return self._surface

    @property
    def width(self):
        """Returns the width of the Cairo surface on which the plot
        is drawn"""
        return self.bbox.width


class MatplotlibPlot:
    def __init__(
            self,
            target=None,
            palette=None,
            background=None,
            ):
        if target is None:
            # Ignore the figure, one can recover it via target.figure
            _, target = plt.subplots()

        self._ctx = target

        if palette is None:
            config = Configuration.instance()
            palette = config["plotting.palette"]
        if not isinstance(palette, Palette):
            palette = palettes[palette]
        self._palette = palette
        self.background = background

        self._objects = []
        self._is_dirty = False

    def add(self, obj, palette=None, opacity=1.0, *args, **kwds):
        """Adds an object to the plot.

        Arguments not specified here are stored and passed to the object's
        plotting function when necessary. Since you are most likely interested
        in the arguments acceptable by graphs, see L{Graph.__plot__} for more
        details.

        @param obj: the object to be added
        @param palette: the color palette used for drawing the object. If the
          object tries to get a color assigned to a positive integer, it
          will use this palette. If C{None}, defaults to the global palette
          of the plot.
        @param opacity: the opacity of the object being plotted, in the range
          0.0-1.0.

        @see: Graph.__plot__
        """
        if opacity < 0.0 or opacity > 1.0:
            raise ValueError("opacity must be between 0.0 and 1.0")

        self._objects.append((obj, palette, opacity, args, kwds))
        self.mark_dirty()

    def mark_dirty(self):
        """Marks the plot as dirty (should be redrawn)"""
        self._is_dirty = True

    @property
    def background(self):
        """Returns the background color of the plot. C{None} means a
        transparent background.
        """
        return self._background

    @background.setter
    def background(self, color):
        """Sets the background color of the plot. C{None} means a
        transparent background. You can use any color specification here
        that is understood by the C{get} method of the current palette
        or by L{igraph.drawing.colors.color_name_to_rgb}.
        """
        if color is None:
            self._background = None
        else:
            self._background = self._palette.get(color)

    def remove(self, obj, idx=1):
        """Removes an object from the plot.

        If the object has been added multiple times and no bounding box
        was specified, it removes the instance which occurs M{idx}th
        in the list of identical instances of the object.

        @param obj: the object to be removed
        @param bbox: optional bounding box specification for the object.
          If given, only objects with exactly this bounding box will be
          considered.
        @param idx: if multiple objects match the specification given by
          M{obj} and M{bbox}, only the M{idx}th occurrence will be removed.
        @return: C{True} if the object has been removed successfully,
          C{False} if the object was not on the plot at all or M{idx}
          was larger than the count of occurrences
        """
        for i in range(len(self._objects)):
            current_obj = self._objects[i][0]
            if current_obj is obj:
                idx -= 1
                if idx == 0:
                    self._objects[i : (i + 1)] = []
                    self.mark_dirty()
                    return True
        return False

    def show(self):
        """Saves the plot to a temporary file and shows it.

        This method is deprecated from python-igraph 0.9.1 and will be removed in
        version 0.10.0.

        @deprecated: Opening an image viewer with a temporary file never worked
            reliably across platforms.
        """
        if self._is_dirty:
            self.redraw()

        plt.show()

    def redraw(self, context=None):
        """Redraws the plot"""
        ax = context or self._ctx

        if self._background is not None:
            ax.set_facecolor(self._background)

        for obj, palette, opacity, args, kwds in self._objects:
            if palette is None:
                palette = getattr(obj, "_default_palette", self._palette)
            plotter = getattr(obj, "__plot__", None)
            if plotter is None:
                warn("%s does not support plotting" % (obj,))
            else:
                if (opacity < 1.0) and ('alpha' not in kwds):
                    kwds['alpha'] = opacity
                plotter(
                    'matplotlib',
                    ax,
                    palette=palette,
                    *args, **kwds,
                    )

        self._is_dirty = False

    def save(self, fname=None, **kwargs):
        if fname is None:
            raise ValueError('Please specify a file path')

        fig = self._ctx.figure
        fig.savefig(fname, **kwargs)


class Plot:
    def __init__(self, backend, target, *args, **kwargs):
        self._backend = backend
        if backend == 'cairo':
            bbox = kwargs.pop('bbox', None)
            palette = kwargs.pop('palette', None)
            background = kwargs.pop('background', 'white')
            self._instance = CairoPlot(
                    target=target,
                    bbox=bbox,
                    palette=palette,
                    background=background,
                    )
        else:
            self._instance = MatplotlibPlot(
                    target,
                    )

    @property
    def backend(self):
        return self._backend

    def add(self, obj, *args, **kwargs):
        return self._instance.add(
            obj, *args, **kwargs,
        )

    def remove(self, obj, *args, **kwargs):
        return self._instance.remove(
            obj, *args, **kwargs,
        )

    def show(self):
        return self._instance.show()

    def redraw(self):
        return self._instance.redraw()

    def save(self, fname=None):
        return self._instance.save(fname=fname)



#####################################################################


def plot(obj, target=None, bbox=(0, 0, 600, 600), *args, **kwds):
    """Plots the given object to the given target.

    Positional and keyword arguments not explicitly mentioned here will be
    passed down to the C{__plot__} method of the object being plotted.
    Since you are most likely interested in the keyword arguments available
    for graph plots, see L{Graph.__plot__} as well.

    @param obj: the object to be plotted
    @param target: the target where the object should be plotted. It can be one
      of the following types:

        - C{matplotib.axes.Axes} -- a matplotlib/pyplot axes in which the
          graph will be plotted. Drawing is delegated to the chosen matplotlib
          backend, and you can use interactive backends and matplotlib
          functions to save to file as well.

        - C{string} -- a file with the given name will be created and an
          appropriate Cairo surface will be attached to it. The supported image
          formats are: PNG, PDF, SVG and PostScript.

        - C{cairo.Surface} -- the given Cairo surface will be used. This can
          refer to a PNG image, an arbitrary window, an SVG file, anything that
          Cairo can handle.

        - C{None} -- a temporary file will be created and the object will be
          plotted there. igraph will attempt to open an image viewer and show
          the temporary file. This feature is deprecated from python-igraph
          version 0.9.1 and will be removed in 0.10.0.

    @param bbox: the bounding box of the plot. It must be a tuple with either
      two or four integers, or a L{BoundingBox} object. If this is a tuple
      with two integers, it is interpreted as the width and height of the plot
      (in pixels for PNG images and on-screen plots, or in points for PDF,
      SVG and PostScript plots, where 72 pt = 1 inch = 2.54 cm). If this is
      a tuple with four integers, the first two denotes the X and Y coordinates
      of a corner and the latter two denoting the X and Y coordinates of the
      opposite corner.

    @keyword opacity: the opacity of the object being plotted. It can be
      used to overlap several plots of the same graph if you use the same
      layout for them -- for instance, you might plot a graph with opacity
      0.5 and then plot its spanning tree over it with opacity 0.1. To
      achieve this, you'll need to modify the L{Plot} object returned with
      L{Plot.add}.

    @keyword palette: the palette primarily used on the plot if the
      added objects do not specify a private palette. Must be either
      an L{igraph.drawing.colors.Palette} object or a string referring
      to a valid key of C{igraph.drawing.colors.palettes} (see module
      L{igraph.drawing.colors}) or C{None}. In the latter case, the default
      palette given by the configuration key C{plotting.palette} is used.

    @keyword margin: the top, right, bottom, left margins as a 4-tuple.
      If it has less than 4 elements or is a single float, the elements
      will be re-used until the length is at least 4. The default margin
      is 20 on each side.

    @keyword inline: whether to try and show the plot object inline in the
      current IPython notebook. Passing C{None} here or omitting this keyword
      argument will look up the preferred behaviour from the
      C{shell.ipython.inlining.Plot} configuration key.  Note that this keyword
      argument has an effect only if igraph is run inside IPython and C{target}
      is C{None}.

    @return: an appropriate L{Plot} object.

    @see: Graph.__plot__
    """

    # Switch backend based on target (first) and config (second)
    if hasattr(plt, "Axes") and isinstance(target, plt.Axes):
        backend = 'matplotlib'
    elif isinstance(target, cairo.Surface):
        backend = 'cairo'
    else:
        backend = Configuration.instance()['plotting.backend']

    if backend == "":
        raise ImportError('cairo or matplotlib are needed for plotting')

    inline = False
    if backend == 'cairo':
        if target is None and _is_running_in_ipython():
            inline = kwds.get("inline")
            if inline is None:
                inline = Configuration.instance()["shell.ipython.inlining.Plot"]

    result = Plot(
        backend,
        target,
    )

    if backend == 'cairo':
        result.add(obj, bbox, *args, **kwds)
    else:
        result.add(obj, *args, **kwds)

    # Matplotlib takes care of the actual backend. We want to show but also
    # return the object in case the user wants to add more objects. Whether the
    # plot is actually drawn on the cavas depends on mpl config, e.g. plt.ion()
    if backend == 'matplotlib':
        result.show()
        return result

    # If we requested an inline plot, just return the result and IPython will
    # call its _repr_svg_ method. If we requested a non-inline plot, show the
    # plot in a separate window and return nothing
    if inline:
        return result

    # We are either not in IPython or the user specified an explicit plot target,
    # so just show or save the result

    if target is None:
        # show with the default backend
        result.show()
    elif isinstance(target, str):
        # save
        result.save()

    # Also return the plot itself
    return result


#####################################################################
