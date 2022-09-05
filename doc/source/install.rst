.. include:: include/global.rst

.. Installing igraph

.. _installing-igraph:

===================
Installing |igraph|
===================

Binary package (recommended)
============================
It is recommended to install a binary package that includes both C core and Python interface. You can choose either of `PyPI <http://pypi.python.org/pypi/igraph>`_ or `Conda <https://anaconda.org/conda-forge/python-igraph>`_. Linux users can also use their package manager.

PyPI
----
PyPI has installers for Windows, Linux, and macOS. We aim to provide binary packages for the three latest minor versions of Python 3.x.

To install the Python interface of |igraph| globally, use the following command
(you might need administrator/root privileges)::

  $ pip install igraph

If you prefer to install |igraph| in a user folder using a `virtual environment
<https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments>`_, use the following commands instead::

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

Linux package managers
----------------------
|igraph|'s Python interface and its dependencies have been packaged for most popular Linux
distributions, including Arch Linux, Debian, Fedora, GNU Guix, NixOS, and Ubuntu.
|igraph| and its underlying C core are usually in two different packages, but
your package manager should take care of that dependency for you.

.. note:: |igraph| is updated quite often: if you need a more recent version than your
   package manager offers, use ``pip`` or ``conda`` as shown above. For bleeding-edge
   versions, compile from source (see below).

Compiling |igraph| from source
==============================
You might want to compile |igraph| to test a recently added feature ahead of release or
to install |igraph| on architectures not covered by our continuous development pipeline.

.. note:: In all cases, the Python interface needs to be compiled against a **matching** version of
  the |igraph| core C library.

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
install |igraph| step by step without ``pip``.

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

Fourth, call the standard Python ``setup.py`` script, e.g. for compiling::

  $ python setup.py build

(press Enter when prompted). That will compile the Python interface in a subfolder called
``build/lib.<your system-your Python version>``, e.g. `build/lib.linux-x86_64-3.8`. You can add
that folder to your ``PYTHONPATH`` if you want to import directly from it, or you can call the ``setup.py``
script to install it from there::

  $ python setup.py install

.. note:: The ``setup.py`` script takes a number of options to customize the install location.

Testing your installation
-------------------------

The unit tests are implemented with the standard ``unittest`` module so you can
run them like this from your the source folder::

  $ python -m unittest discover

Troubleshooting
===============

Q: I am trying to install |igraph| on Windows but am getting DLL import errors
------------------------------------------------------------------------------
A: The most common reason for this error is that you do not have the Visual C++
Redistributable library installed on your machine. Python's own installer is
supposed to install it, but in case it was not installed on your system, you can
`download it from Microsoft <https://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist>`_.

Q: I am trying to use |igraph| but get errors about something called Cairo
----------------------------------------------------------------------------------
A: |igraph| by default uses a third-party called `Cairo <http://www.cairographics.org>`_ for plotting.
If Cairo is not installed on your computer, you might get an import error. This error is most commonly
encountered on Windows machines.

There are two solutions to this problem: installing Cairo or, if you are using a recent versions of
|igraph|, switching to the :mod:`matplotlib` plotting backend.

**1. Install Cairo**: As explained `here <https://pycairo.readthedocs.io/en/latest/getting_started.html>`_,
you need to install Cairo headers using your package manager (Linux) or `homebrew <https://brew.sh/>`_
(macOS) and then::

  $ pip install pycairo

The Cairo project does not provide pre-compiled binaries for Windows, but Christoph Gohlke
maintains a site containing unofficial Windows binaries for several Python extension packages,
including Cairo. Therefore, the easiest way to install Cairo on Windows along with its Python bindings
is simply to download it from `Christoph's site <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo>`_.
Make sure you use an installer that is suitable for your Windows platform (32-bit or 64-bit) and the
version of Python you are using.

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
