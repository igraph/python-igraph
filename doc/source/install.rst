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
install |igraph| from a precompiled binary package on various platforms. `Compiling igraph
from source`_ tells you how to compile |igraph| from the source package.

Installation from a binary package
==================================

Installing |igraph| from the Python Package Index
-------------------------------------------------

To ensure getting the latest binary release of |igraph|'s Python interface, it is recommended
that you install it from the `Python Package Index
<http://pypi.python.org/pypi/python-igraph>`_ (PyPI), which has installers for Windows, Linux,
and macOS. Currently there are binary packages for Python 2.7, and Python 3.5 through 3.8, but
note that support for Python 2.7 will be discontinued with the version 0.9.0 release of
|igraph|'s Python interface.

To install |python-igraph| globally, use the followig command (you probably need
administrator/root priviledges):

  $ pip install python-igraph

Many users like to install packages into a project-specific `virtual environment
<https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments>`_.
A variation of the following commands should work on most platforms:

  $ python -m venv venv
  $ source venv/bin/activate
  $ pip install python-igraph

To test the installed package, launch Python within the virtual environment and run the
following:

  >>> import igraph.test
  >>> igraph.test.run_tests()

The above commands run the bundled test cases to ensure that everything is fine with your
|igraph| installation.

Installing |igraph| via Conda
-----------------------------

Users of the `Anaconda Python distribution <https://www.anaconda.com/distribution/>`_ or the
`conda package manager <https://conda.io/>`_ may opt to install |igraph|'s Python interface
using conda. That can be achieved by running the following command:

  $ conda install -c conda-forge python-igraph

To test the installed package, launch Python and run the following:

  >>> import igraph.test
  >>> igraph.test.run_tests()

The above commands run the bundled test cases to ensure that everything is fine with your
|igraph| installation.

|igraph| on Windows
-------------------

There is a Windows installer for |igraph|'s Python interface on the `Python Package Index
<http://pypi.python.org/pypi/python-igraph>`_ (see `Installing igraph from the Python Package
Index`_).

TODO: Check if Windows still requires special steps to get PyCairo running.

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

The Mac installer for |igraph|'s Python interface on the `Python Package Index
<http://pypi.python.org/pypi/python-igraph>`_ works for Intel-based Macs only. PowerPC
users should compile the package themselves (see `Compiling igraph from source`_).

TODO: Check if PyCairo on Mac still requires using Brew

Graph plotting in |igraph| is implemented using a third-party package called `Cairo
<http://www.cairographics.org>`_. If you want to create publication-quality plots in |igraph|
on macOS, you must also install Cairo and its Python bindings. The Cairo project does not
provide pre-compiled binaries for macOS, but the `Homebrew package manager
<https://brew.sh/>`, so you can use it to install Cairo. After installing Homebrew itself, you
can run:

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
========================================

|python-igraph| has C Python binding into the main |igraph| library, so you'll need both a C compiler
and the library itself. However, the |python-igraph| installer is able to fetch and compile the |igraph|
C library on the fly.

There are two common scenarios to compile |python-igraph| from source:

1. Your would like to use the latest development version from Github, usually to try out some recently
   added features
2. The Pypi repository does not include precompiled binaries for your system. This can happen if your operating
   system is not covered by our continuous development.

Both will be covered in the next sections.

Compiling using pip
-------------------
If you want the development version of |python-igraph|, call:

  $ pip install git+https://github.com/igraph/python-igraph

Pip is smart enough to download the sources from Github, initialize the submodule for the |igraph| C core,
compile it, and then compile |python-igraph| against it and install it. As above, a virtual environment is
a commonly used sandbox to test experimental packages.

If you want the latest release from Pypi but prefer to (or have to) install from source, call:

  $ pip install --no-binary ':all:' python-igraph

.. note:: If there is no binary for your system anyway, you can just try without the `--no-binary` option and
   obtain the same result.

Compiling step by step
----------------------
This section should be rarely used in practice but explains how to compile and install |python-igraph| step
by step without pip.

First, obtain the source code either from Github:

  $ git clone https://github.com/igraph/python-igraph.git

or from `Pypi <https://pypi.org/project/python-igraph/#files>` or
`Github <https://github.com/igraph/python-igraph/releases/>`. In the latter case, decompress the archive.

Second, go into the folder:

  $ cd python-igraph

(it might have a slightly different name depending on the release).

Third, initialze the git submodule for the |igraph| C core:

  $ git submodule update --init

.. note:: If you prefer to compile and link |python-igraph| against an existing |igraph| C core, for instance
   one you installed with your package manager, you can skip this step (git submodule) and proceed to the
   next step.

Fourth, call the standard python `setup.py` script, e.g. for compiling:

  $ python setup.py build

(press Enter when prompted). That will compile the |python-igraph| package in a subfolder called
`build/lib.<your system-your Python version>`, e.g. `build/lib.linux-x86_64-3.8`. You can add
that folder to your `PYTHONPATH` if you want to import directly from it, or you can call the `setup.py`
script to install it from there:

  $ python setup.py install

.. note:: The `setup.py` script takes a number of options to customize the install location.
