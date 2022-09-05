"""
Sphinx plugin to run example scripts and create a gallery page.

Lightly modified from the seaborn project (Michael Waskom).
Originally, lightly modified from the mpld3 project.

"""
import os
import os.path as op
import re
import glob
import token
import tokenize
import shutil
import warnings

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402


INDEX_TEMPLATE = """

.. raw:: html

    <style type="text/css">
    .figure-box {{
        position: relative;
        float: left;
        margin: 10px;
        width: 180px;
        height: 220px;
    }}

    .figure img {{
        position: absolute;
        display: inline;
        left: 0;
        width: 170px;
        height: 170px;
    }}

    .figure:hover img {{
        -webkit-filter: blur(3px);
        -moz-filter: blur(3px);
        -o-filter: blur(3px);
        -ms-filter: blur(3px);
        filter: blur(3px);
    }}

    .figure span {{
        position: absolute;
        display: inline;
        left: 0;
        width: 170px;
        height: 170px;
        background: rgba(255, 255, 255, 0);
        color: black;
        opacity: 0;
        z-index: 100;
        transition: opacity 0.25s ease-in-out;
    }}

    .figure p {{
        position: absolute;
        top: 50%;
        width: 100%;
        transform: translateY(-50%);
        margin: 0;
    }}

    .figure:hover span {{
        background: rgba(255, 255, 255, 0.75);
        opacity: 1;
    }}

    .caption {{
        position: absolute;
        width: 180px;
        top: 190px;
        text-align: center !important;
    }}
    </style>

.. _{sphinx_tag}:

Gallery
=======

{toctree}

{contents}

.. raw:: html

    <div style="clear: both"></div>
"""


def create_thumbnail(infile, thumbfile,
                     size=275,
                     #width=275, height=275,
                     #cx=0.5, cy=0.5, border=4,
                     ):
    '''Store a thumbnail from a PNG figure.

    For nonsquare images, pad them with the background color as estimated from
    the top left corner of the image.
    '''
    import numpy as np

    baseout, extout = op.splitext(thumbfile)

    im = matplotlib.image.imread(infile)
    rows, cols, ncolors = im.shape

    if rows > cols:
        tmp = np.empty((rows, rows, ncolors), dtype=im.dtype)
        tmp[:] = im[0, 0]
        diff = (rows - cols) // 2
        tmp[:, diff:diff + cols] = im
        im = tmp
    elif cols > rows:
        tmp = np.empty((cols, cols, ncolors), dtype=im.dtype)
        tmp[:] = im[0, 0]
        diff = (cols - rows) // 2
        tmp[diff:diff + rows] = im
        im = tmp

    #x0 = int(cx * cols - .5 * width)
    #y0 = int(cy * rows - .5 * height)
    #xslice = slice(x0, x0 + width)
    #yslice = slice(y0, y0 + height)
    #thumb = im[yslice, xslice]
    #thumb[:border, :, :3] = thumb[-border:, :, :3] = 0
    #thumb[:, :border, :3] = thumb[:, -border:, :3] = 0

    dpi = 100
    fig = plt.figure(figsize=(size / dpi, size / dpi), dpi=dpi)

    ax = fig.add_axes([0, 0, 1, 1], aspect='auto',
                      frameon=False, xticks=[], yticks=[])
    ax.imshow(im, aspect='auto', resample=True,
              interpolation='bilinear')
    fig.savefig(thumbfile, dpi=dpi)
    plt.close(fig)


def indent(s, N=4):
    """indent a string"""
    return s.replace('\n', '\n' + N * ' ')


class TutorialGenerator(object):
    """Tools for generating an example page from a file"""
    def __init__(self, dirname, thumbs_dir):
        self.dirname = dirname
        self.thumbs_dir = thumbs_dir

    @property
    def modulename(self):
        return op.split(self.dirname)[-1]

    @property
    def rstfilename(self):
        return op.join(self.dirname, self.modulename + ".rst")

    @property
    def htmlfilename(self):
        return 'tutorials/{0}/{0}.html'.format(self.modulename)

    @property
    def sphinxtag(self):
        return self.modulename

    @property
    def pagetitle(self):
        return self.docstring.strip().split('\n')[0].strip()

    def create_thumbnail_if_needed(self):
        '''Create a thumbnail except for animated GIFs'''

        # Make thumbnail for PNG images, for GIFs just pass through
        animated_giffiles = glob.glob(
            op.join(self.dirname, "figures", "*.gif")
        )
        if len(animated_giffiles):
            thumbfile = animated_giffiles[0]
        else:
            imagefile = glob.glob(op.join(self.dirname, "figures", "*.png"))[0]
            thumbfile = op.join(self.thumbs_dir, self.modulename + '_thumb.png')
            create_thumbnail(imagefile, thumbfile)

        # Thumbnail/GIF file without path
        self.thumbfilename = op.split(thumbfile)[1]

    def extract_title(self):
        '''Extract title from RST file'''
        with open(self.rstfilename, 'rt') as f:
            for line in f:
                if set(line.rstrip('\n')) == set('='):
                    break
            else:
                raise IOError('Title not found')
            title = next(f).rstrip('\n')
        self.title = title

    def toctree_entry(self):
        return "   ./{:}\n\n".format(op.splitext(self.htmlfilename)[0])

    def contents_entry(self):
        return (".. raw:: html\n\n"
                "    <div class='figure-box align-center'>\n"
                "    <a href=./tutorials/{1}/{1}.html>\n"
                "    <div class='figure align-center'>\n"
                "    <img src=_images/{0}>\n"
                "    <span class='figure-label'>\n"
                "    <p>{2}</p>\n"
                "    </span>\n"
                "    </div>\n"
                "    <div class='caption'>\n"
                "    {2}\n"
                "    </div>\n"
                "    </a>\n"
                "    </div>\n\n"
                "\n\n"
                "".format(self.thumbfilename,
                          self.modulename,
                          self.title,
                          ))


def main(app):
    source_dir = op.abspath(op.join(app.builder.srcdir, 'tutorials'))
    thumbs_dir = op.join(app.builder.outdir, "_images")

    if not op.isdir(thumbs_dir):
        os.makedirs(thumbs_dir, exist_ok=True)

    toctree = ("\n\n"
               ".. toctree::\n"
               "   :hidden:\n\n")
    content_dict = {}

    # Write individual example files
    for filename in sorted(glob.glob(op.join(source_dir, "*", "*.rst"))):
        print(filename)

        # Folder for this tutorial
        dirname = op.dirname(filename)

        # Extract title for thumbnail alt/subtitle
        ex = TutorialGenerator(dirname, thumbs_dir)

        # Extract title
        ex.extract_title()

        # Make thumbnail if needed
        ex.create_thumbnail_if_needed()

        # Generate toctree and content raw html code
        toctree += ex.toctree_entry()
        content_dict[ex.title] = ex.contents_entry()

    # Sort
    content_list = ["\n\n"] + [content_dict.pop('Quick Start')]
    for title in sorted(content_dict):
        content_list.append(content_dict[title])
    contents = ''.join(content_list)

    # write index file
    index_file = op.join(source_dir, '..', 'gallery.rst')
    with open(index_file, 'w') as index:
        index.write(INDEX_TEMPLATE.format(sphinx_tag="gallery",
                                          toctree=toctree,
                                          contents=contents))


def setup(app):
    app.connect('builder-inited', main)

