.. include:: include/global.rst

.. Installing igraph

.. _installing-igraph:

===================
Installing |igraph|
===================

This chapter describes how to install the C core of |igraph| and its Python bindings on
Windows, macOS, and GNU/Linux.

Which |igraph| is right for you?
================================

|igraph| is primarily a library written in C. It is *not* a standalone program, nor it is a
pure Python package that you can just drop in your Python path. Therefore, if you would like
to use |igraph|'s functionality in Python, you must install a few packages. Do not worry,
though, there are precompiled packages for the major operating systems. Precompiled packages
are often called *binary packages*, while the raw source code is usually referred to as the
*source package*.

In general, you should almost always opt for the binary package unless a binary package is
not available for your platform or you have some local modifications that you want to
incorporate into |igraph|'s source. `Installation from a binary package`_ tells you how to
install |igraph| from a precompiled binary package on various platforms. `Compiling python-igraph
from source`_ tells you how to compile |igraph| from the source package.

Installation from a binary package
==================================

Installing |igraph| from the Python Package Index
-------------------------------------------------

To ensure getting the latest binary release of |igraph|'s Python interface, it is recommended
that you install it from the `Python Package Index
<http://pypi.python.org/pypi/python-igraph>`_ (PyPI), which has installers for Windows, Linux,
and macOS. We aim to provide binary packages for the three latest minor versions of Python 3.x.

To install |python-igraph| globally, use the following command (you probably need
administrator/root privileges)::

  $ pip install python-igraph

Many users like to install packages into a project-specific `virtual environment
<https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments>`_.
A variation of the following commands should work on most platforms::

  $ python -m venv venv
  $ source venv/bin/activate
  $ pip install python-igraph

Alternatively, if you do not want to activate the virtualenv, you can call the ``pip`` executable
in it directly::

  $ python -m venv venv
  $ venv/bin/pip install python-igraph

Installing |igraph| via Conda
-----------------------------

Users of the `Anaconda Python distribution <https://www.anaconda.com/distribution/>`_ or the
`conda package manager <https://conda.io/>`_ may opt to install |igraph|'s Python interface
using conda. That can be achieved by running the following command::

  $ conda install -c conda-forge python-igraph

|igraph| on Windows
-------------------

Precompiled Windows wheels for |igraph|'s Python interface are available on the `Python Package Index
<http://pypi.python.org/pypi/python-igraph>`_ (see `Installing igraph from the Python Package
Index`_).

Graph plotting in |igraph| is implemented using a third-party package called `Cairo
<http://www.cairographics.org>`_. If you want to create publication-quality plots in |igraph|
on Windows, you must also install Cairo and its Python bindings. The Cairo project does not
provide pre-compiled binaries for Windows, but Christoph Gohlke maintains a site containing
unofficial Windows binaries for several Python extension packages, including Cairo.
Therefore, the easiest way to install Cairo on Windows along with its Python bindings is
simply to download it from `Christoph's site
<http://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo>`_. Make sure you use an installer that is
suitable for your Windows platform (32-bit or 64-bit) and the version of Python you are using.

After running the installer, you can launch Python again and check if it worked:

  >>> import igraph as ig
  >>> g = ig.Graph.Famous("petersen")
  >>> ig.plot(g)

If PyCairo was successfully installed, this will display a Petersen graph.

|igraph| on macOS
-----------------

Precompiled macOS wheels for |igraph|'s Python interface are available on the `Python Package Index
<http://pypi.python.org/pypi/python-igraph>`_  (see `Installing igraph from the Python Package
Index`_).

Graph plotting in |igraph| is implemented using a third-party package called `Cairo
<http://www.cairographics.org>`_. If you want to create publication-quality plots in |igraph|
on macOS, you must also install Cairo and its Python bindings. The Cairo project does not
provide pre-compiled binaries for macOS, but the `Homebrew package manager
<https://brew.sh/>`_, so you can use it to install Cairo. After installing Homebrew itself, you
can run::

  $ brew install cairo

After installing Cairo, launch Python and check if it worked:

  >>> import igraph as ig
  >>> g = ig.Graph.Famous("petersen")
  >>> ig.plot(g)

If Cairo was successfully installed, this will display a Petersen graph.

|igraph| on Linux
-----------------

|igraph|'s Python interface and its dependencies have been packaged for most popular Linux
distributions, including Arch Linux, Debian, Fedora, GNU Guix, NixOS, and Ubuntu.
|python-igraph| and its underlying |igraph| C core are usually in two different packages, but
your package manager should take care of that dependency for you.

.. note:: Distribution packages can be outdated: if you find that's the case for you, you may
   choose to install |igraph| from the `Python Package Index <http://pypi.python.org/pypi/python-igraph>`_
   instead to get a more recent release (see `Installing igraph from the Python Package Index`_).

Compiling |python-igraph| from source
=====================================

|python-igraph| binds itself into the main |igraph| library using some glue code written in C, so you'll need
both a C compiler and the library itself. Source tarballs of |python-igraph| obtained from PyPI already
contain a matching version of the C core of |igraph|.

There are two common scenarios to compile |python-igraph| from source:

1. Your would like to use the latest development version from Github, usually to try out some recently
   added features

2. The PyPI repository does not include precompiled binaries for your system. This can happen if your operating
   system is not covered by our continuous development.

Both will be covered in the next sections.

Compiling using pip
-------------------

If you want the development version of |python-igraph|, call::

  $ pip install git+https://github.com/igraph/python-igraph

``pip`` is smart enough to download the sources from Github, initialize the submodule for the |igraph| C core,
compile it, and then compile |python-igraph| against it and install it. As above, a virtual environment is
a commonly used sandbox to test experimental packages.

If you want the latest release from PyPI but prefer to (or have to) install from source, call::

  $ pip install --no-binary ':all:' python-igraph

.. note:: If there is no binary for your system anyway, you can just try without the ``--no-binary`` option and
   obtain the same result.

Compiling step by step
----------------------

This section should be rarely used in practice but explains how to compile and install |python-igraph| step
by step without ``pip``.

First, obtain the bleeding-edge source code from Github::

  $ git clone https://github.com/igraph/python-igraph.git

or download a recent release from `PyPI <https://pypi.org/project/python-igraph/#files>`_ or from the
`Github releases page <https://github.com/igraph/python-igraph/releases/>`_. Decompress the archive if
needed.

Second, go into the folder::

  $ cd python-igraph

(it might have a slightly different name depending on the release).

Third, if you cloned the source from Github, initialize the ``git`` submodule for the |igraph| C core::

  $ git submodule update --init

.. note:: If you prefer to compile and link |python-igraph| against an existing |igraph| C core, for instance
   the one you installed with your package manager, you can skip the ``git`` submodule initialization step. If you
   downloaded a tarball, you also need to remove the ``vendor/source/igraph`` folder because the setup script
   will look for the vendored |igraph| copy first. However, a particular version of |python-igraph| is guaranteed
   to work only with the version of the C core that is bundled with it (or with the revision that the ``git``
   submodule points to).

Fourth, call the standard Python ``setup.py`` script, e.g. for compiling::

  $ python setup.py build

(press Enter when prompted). That will compile the |python-igraph| package in a subfolder called
``build/lib.<your system-your Python version>``, e.g. `build/lib.linux-x86_64-3.8`. You can add
that folder to your ``PYTHONPATH`` if you want to import directly from it, or you can call the ``setup.py``
script to install it from there::

  $ python setup.py install

.. note:: The ``setup.py`` script takes a number of options to customize the install location.

Testing your installation
-------------------------

The unit tests of ``python-igraph`` are implemented with the standard ``unittest`` module so you can
run them like this from your the source folder::

  $ python -m unittest discover
