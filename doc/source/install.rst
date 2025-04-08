.. include:: include/global.rst

.. Installing igraph

.. _installing-igraph:

===================
Installing |igraph|
===================

Binary package (recommended)
============================
It is recommended to install a binary package that includes both C core and Python interface. You can choose either of `PyPI <https://pypi.org/project/igraph/>`_ or `Conda <https://anaconda.org/conda-forge/python-igraph>`_. Linux users can also use their package manager.

PyPI
----
PyPI has installers for Windows, Linux, and macOS. We aim to provide binary packages for the three latest minor versions of Python 3.x.

To install the Python interface of |igraph| globally, use the following command
(you might need administrator/root privileges)::

  $ pip install igraph

If you prefer to install |igraph| in a user folder using a `virtual environment
<https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-virtual-environments>`_, use the following commands instead::

  $ python -m venv my_environment
  $ source my_environment/bin/activate
  $ pip install igraph

As usual, if you do not want to activate the virtualenv, you can call the ``pip``
executable in it directly::

  $ python -m venv my_environment
  $ my_environment/bin/pip install igraph

Conda
-----
Packages are kindly provided by `conda-forge <https://conda-forge.org/>`_::

  $ conda install -c conda-forge python-igraph

Like virtualenv, Conda also offers virtual environments. If you prefer that option::

  $ conda create -n my_environment
  $ conda activate my_environment
  $ conda install -c conda-forge python-igraph

Package managers on Linux and other systems
-------------------------------------------
|igraph|'s Python interface and its dependencies are included in several package management
systems, including those of the most popular Linux distributions (Arch Linux,
Debian and Ubuntu, Fedora, etc.) as well as some cross-platform systems like
NixPkgs or MacPorts.

.. note:: |igraph| is updated quite often: if you need a more recent version than your
   package manager offers, use ``pip`` or ``conda`` as shown above. For bleeding-edge
   versions, compile from source (see below).

Compiling |igraph| from source
==============================
You might want to compile |igraph| to test a recently added feature ahead of release or
to install |igraph| on architectures not covered by our continuous development pipeline.

.. note:: In all cases, the Python interface needs to be compiled against
   a **matching** version of the |igraph| core C library. If you used ``git``
   to check out the source tree, ``git`` was probably smart enough to check out
   the matching version of igraph's C core as a submodule into
   ``vendor/source/igraph``. You can use ``git submodule update --init
   --recursive`` to check out the submodule manually, or you can run ``git
   submodule status`` to print the exact revision of igraph's C core that
   should be used with the Python interface.

Compiling using pip
-------------------

If you want the development version of |igraph|, call::

  $ pip install git+https://github.com/igraph/python-igraph

``pip`` is smart enough to download the sources from Github, initialize the
submodule for the |igraph| C core, compile it, and then compile the Python
interface against it and install it. As above, a virtual environment is
a commonly used sandbox to test experimental packages.

If you want the latest release from PyPI but prefer to (or have to) install from source, call::

  $ pip install --no-binary ':all:' igraph

.. note:: If there is no binary for your system anyway, you can just try without the ``--no-binary`` option and
   obtain the same result.

Compiling step by step
----------------------

This section should be rarely used in practice but explains how to compile and
install |igraph| step by step from a local checkout, i.e. _not_ relying on
``pip`` to fetch the sources. (You would still need ``pip`` to install from
source, or a PEP 517-compliant build frontend like
`build <https://pypa-build.readthedocs.io/en/stable/>`_ to build an installable
Python wheel.

First, obtain the bleeding-edge source code from Github::

  $ git clone https://github.com/igraph/python-igraph.git

or download a recent `release from PyPI <https://pypi.org/project/python-igraph/#files>`_ or from the
`Github releases page <https://github.com/igraph/python-igraph/releases/>`_. Decompress the archive if
needed.

Second, go into the folder::

  $ cd python-igraph

(it might have a slightly different name depending on the release).

Third, if you cloned the source from Github, initialize the ``git`` submodule for the |igraph| C core::

  $ git submodule update --init

.. note:: If you prefer to compile and link |igraph| against an existing |igraph| C core, for instance
   the one you installed with your package manager, you can skip the ``git`` submodule initialization step. If you
   downloaded a tarball, you also need to remove the ``vendor/source/igraph`` folder because the setup script
   will look for the vendored |igraph| copy first. However, a particular
   version of the Python interface is guaranteed to work only with the version
   of the C core that is bundled with it (or with the revision that the ``git``
   submodule points to).

Fourth, call ``pip`` to compile and install the package from source::

  $ pip install .

Alternatively, you can call ``build`` or another PEP 517-compliant build frontend
to build an installable Python wheel. Here we use `pipx <https://pipx.pypa.io>`_
to invoke ``build`` in a separate virtualenv::

  $ pipx run build

Testing your installation
-------------------------

Use ``tox`` or another standard test runner tool to run all the unit tests.
Here we use `pipx <https://pipx.pypa.io>`_ to invoke ``tox``::

  $ pipx run tox

You can also call ``tox`` directly from the root folder of the igraph source
tree if you already installed ``tox`` system-wide::

  $ tox

Troubleshooting
===============

Q: I am trying to install |igraph| on Windows but am getting DLL import errors
------------------------------------------------------------------------------
A: The most common reason for this error is that you do not have the Visual C++
Redistributable library installed on your machine. Python's own installer is
supposed to install it, but in case it was not installed on your system, you can
`download it from Microsoft <https://learn.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170>`_.

Q: I am trying to use |igraph| but get errors about something called Cairo
----------------------------------------------------------------------------------
A: |igraph| by default uses a third-party called `Cairo <https://www.cairographics.org>`_ for plotting.
If Cairo is not installed on your computer, you might get an import error. This error is most commonly
encountered on Windows machines.

There are two solutions to this problem: installing Cairo or, if you are using a recent versions of
|igraph|, switching to the :mod:`matplotlib` plotting backend.

**1. Install Cairo**: As explained `here <https://pycairo.readthedocs.io/en/latest/getting_started.html>`_,
you need to install Cairo headers using your package manager (Linux) or `homebrew <https://brew.sh/>`_
(macOS) and then::

  $ pip install pycairo

To check if Cairo is installed correctly on your system, run the following example::

  >>> import igraph as ig
  >>> g = ig.Graph.Famous("petersen")
  >>> ig.plot(g)

If PyCairo was successfully installed, this will display a Petersen graph.

**2. Switch to matplotlib**: You can :doc:`configure <configuration>` |igraph| to use matplotlib
instead of Cairo. First, install it::

  $ pip install matplotlib

To use matplotlib for a single plot, create a :class:`matplotlib.figure.Figure` and
:class:`matplotlib.axes.Axes` beforehand (e.g. using :func:`matplotlib.pyplot.subplots`)::

  >>> import matplotlib.pyplot as plt
  >>> import igraph as ig
  >>> fig, ax = plt.subplots()
  >>> g = ig.Graph.Famous("petersen")
  >>> ig.plot(g, target=ax)
  >>> plt.show()

To use matplotlib for a whole session/notebook::

  >>> import matplotlib.pyplot as plt
  >>> import igraph as ig
  >>> ig.config["plotting.backend"] = "matplotlib"
  >>> g = ig.Graph.Famous("petersen")
  >>> ig.plot(g)
  >>> plt.show()

To preserve this preference across sessions/notebooks, you can store it in the default
configuration file used by |igraph|::

  >>> import igraph as ig
  >>> ig.config["plotting.backend"] = "matplotlib"
  >>> ig.config.save()

From now on, |igraph| will default to matplotlib for plotting.
