
[![Build and test with tox](https://github.com/igraph/python-igraph/actions/workflows/build.yml/badge.svg)](https://github.com/igraph/python-igraph/actions/workflows/build.yml)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/igraph)](https://pypi.python.org/pypi/igraph)
[![PyPI wheels](https://img.shields.io/pypi/wheel/igraph.svg)](https://pypi.python.org/pypi/igraph)
[![Documentation Status](https://readthedocs.org/projects/igraph/badge/?version=latest)](https://igraph.readthedocs.io/)

# Python interface for the igraph library

igraph is a library for creating and manipulating graphs.
It is intended to be as powerful (ie. fast) as possible to enable the
analysis of large graphs.

This repository contains the source code to the Python interface of
igraph.

Since version 0.10.2, the documentation is hosted on
[readthedocs](https://igraph.readthedocs.io). Earlier versions are documented
on [our old website](https://igraph.org/python/versions/0.10.1/).

igraph is a collaborative work of many people from all around the world —
see the [list of contributors here](./CONTRIBUTORS.md).

## Citation

If you use igraph in your research, please cite

> Csardi, G., & Nepusz, T. (2006). The igraph software package for complex network research. InterJournal, Complex Systems, 1695.

# Installation

We aim to provide wheels on PyPI for most of the stock Python versions;
typically at least the three most recent minor releases from Python 3.x.
Therefore, running the following command should work without having to compile
anything during installation:

```
pip install igraph
```

See details in [Installing Python Modules](https://docs.python.org/3/installing/).

## Installation from source with pip on Debian / Ubuntu and derivatives

If you need to compile igraph from source for some reason, you need to
install some dependencies first:

```
sudo apt install build-essential python-dev libxml2 libxml2-dev zlib1g-dev
```

and then run

```
pip install igraph
```

This should compile the C core of igraph as well as the Python extension
automatically.

## Installation from source on Windows

It is now also possible to compile `igraph` from source under Windows for
Python 3.7 and later. Make sure that you have Microsoft Visual Studio 2015 or
later installed, and of course Python 3.7 or later. First extract the source to
a suitable directory. If you launch the Developer command prompt and navigate to
the directory where you extracted the source code, you should be able to build
and install igraph using `pip install .`, assuming that you have `pip`
installed in your Python environment.

You may need to set the architecture that you are building on explicitly by setting the environment variable

```
set IGRAPH_CMAKE_EXTRA_ARGS=-A [arch]
```

where `[arch]` is either `Win32` for 32-bit builds or `x64` for 64-bit builds.
Also, when building in MSYS2, you need to set the `SETUPTOOLS_USE_DISTUTILS`
environment variable to `stdlib`; this is because MSYS2 uses a patched version
of `distutils` that conflicts with `setuptools >= 60.0`.

> [!TIP]
> You need the following packages:
> `$MINGW_PACKAGE_PREFIX-python-pip $MINGW_PACKAGE_PREFIX-python-setuptools $MINGW_PACKAGE_PREFIX-cc $MINGW_PACKAGE_PREFIX-cmake`

### Enabling GraphML

By default, GraphML is disabled, because `libxml2` is not available on Windows in
the standard installation. You can install `libxml2` on Windows using
[`vcpkg`](https://github.com/Microsoft/vcpkg). After installation of `vcpkg` you
can install `libxml2` as follows

```
vcpkg.exe install libxml2:x64-windows-static-md
```

for 64-bit version (for 32-bit versions you can use the `x86-windows-static-md`
triplet). You need to integrate `vcpkg` in the build environment using

```
vcpkg.exe integrate install
```

This mentions that

> CMake projects should use: `-DCMAKE_TOOLCHAIN_FILE=[vcpkg build script]`

which we will do next. In order to build `igraph` correctly, you also
need to set some other environment variables before building `igraph`:

```
set IGRAPH_CMAKE_EXTRA_ARGS=-DVCPKG_TARGET_TRIPLET=x64-windows-static-md -DCMAKE_TOOLCHAIN_FILE=[vcpkg build script]
set IGRAPH_EXTRA_LIBRARY_PATH=[vcpkg directory]/installed/x64-windows-static-md/lib/
set IGRAPH_STATIC_EXTENSION=True
set IGRAPH_EXTRA_LIBRARIES=libxml2,lzma,zlib,iconv,charset
set IGRAPH_EXTRA_DYNAMIC_LIBRARIES: wsock32,ws2_32
```

You can now build and install `igraph` again by simply running `pip install .`.
Please make sure to use a clean source tree, if you built previously without
GraphML, it will not update the build.

## Linking to an existing igraph installation

The source code of the Python package includes the source code of the matching
igraph version that the Python interface should compile against. However, if
you want to link the Python interface to a custom installation of the C core
that has already been compiled and installed on your system, you can ask our
build system to use the pre-compiled version. This option requires that your
custom installation of igraph is discoverable with `pkg-config`. First, check
whether `pkg-config` can tell you the required compiler and linker flags for
igraph:

```bash
pkg-config --cflags --libs igraph
```

If `pkg-config` responds with a set of compiler and linker flags and not an
error message, you are probably okay. You can then proceed with the
installation using pip after setting the environment variable named
`IGRAPH_USE_PKG_CONFIG` to `1` to indicate that you want to use an
igraph instance discoverable with `pkg-config`:

```bash
IGRAPH_USE_PKG_CONFIG=1 pip install igraph
```

Alternatively, if you have already downloaded and extracted the source code
of igraph, you can run `pip install` on the source tree directly:

```bash
IGRAPH_USE_PKG_CONFIG=1 pip install .
```

(Note that you need the `IGRAPH_USE_PKG_CONFIG=1` environment variable
for both invocations, otherwise the call to `pip install` would still
build the vendored C core instead of linking to an existing installation).

This option is primarily intended for package maintainers in Linux
distributions so they can ensure that the packaged Python interface links to
the packaged igraph library instead of bringing its own copy.

It is also useful on macOS if you want to link to the igraph library installed
from Homebrew.

Due to the lack of support of `pkg-config` on MSVC, it is currently not
possible to build against an external library on MSVC.

In case you are already using a MSYS2/[MinGW](https://www.mingw-w64.org/) and already have
[mingw-w64-igraph](https://packages.msys2.org/base/mingw-w64-igraph) installed,
simply type:
```
IGRAPH_USE_PKG_CONFIG=1 SETUPTOOLS_USE_DISTUTILS=stdlib pip install igraph
```
to build.

**Warning:** the Python interface is guaranteed to work only with the same
version of the C core that is vendored inside the `vendor/source/igraph`
folder. While we try hard not to break API or ABI in the C core of igraph
between minor versions in the 0.x branch and we will keep on doing so for major
versions once 1.0 is released, there are certain functions in the C API that
are marked as _experimental_ (see the documentation of the C core for details),
and we reserve the right to break the APIs of those functions, even if they are
already exposed in a higher-level interface. This is because the easiest way to
test these functions in real-life research scenarios is to expose them in one
of the higher level interfaces. Therefore, if you unbundle the vendored source
code of igraph and link to an external version instead, we can make no
guarantees about stability unless you link to the exact same version as the
one we have vendored in this source tree.

If you are curious about which version of the Python interface is compatible
with which version of the C core, you can look up the corresponding tag in
Github and check which revision of the C core the repository points to in
the `vendor/source/igraph` submodule.

## Compiling the development version

If you want to install the development version, the easiest way to do so is to
install it using

```bash
pip install git+https://github.com/igraph/python-igraph
```

This automatically fetches the development version from the repository, builds
the package and installs it. By default, this will install the Python interface
from the `main` branch, which is used as the basis for the development of the
current release series. Unstable and breaking changes are being made in the
`develop` branch. You can install this similarly by doing

```bash
pip install git+https://github.com/igraph/python-igraph@develop
```

In addition to `git`, the installation of the development version requires some
additional dependencies, read further below for details.

For more information about installing directly from `git` using `pip` see
https://pip.pypa.io/en/stable/topics/vcs-support/#git.

Alternatively, you can clone this repository locally. This repository contains a
matching version of the C core of `igraph` as a git submodule. In order to
install the development version from source, you need to instruct git to check
out the submodules first:

```bash
git submodule update --init
```

Compiling the development version additionally requires `flex` and `bison`. You
can install those on Ubuntu using

```bash
sudo apt install bison flex
```

On macOS you can install these from Homebrew or MacPorts. On Windows you can
install `winflexbison3` from Chocolatey.

Then you can install the package directly with `pip` (see also the previous section):

```bash
pip install .
```

If you would like to create a source distribution or a Python wheel instead of
installing the module directly in your Python environment, use a standard build
frontend like [build](https://pypa-build.readthedocs.io/en/stable/). If you
use [pipx](https://pypa.github.io/pipx/) to isolate command-line Python tools
in their own separate virtualenvs, you can simply run:

```bash
pipx run build
```

### Running unit tests

Unit tests can be executed from within the repository directory with `tox` or
with the built-in `unittest` module:

```bash
python -m unittest
```

Note that unit tests have additional dependencies like NumPy, PIL or
`matplotlib`. The unit test suite will try to do its best to skip tests
requiring external dependencies, but if you want to make sure that all the unit
tests are executed, either use `tox` (which will take care of installing the
test dependencies in a virtualenv), or install the module with the `test`
extras:

```bash
pip install '.[test]'
```

# Contributing

Contributions to `igraph` are welcome!

If you want to add a feature, fix a bug, or suggest an improvement, open an
issue on this repository and we'll try to answer. If you have a piece of code
that you would like to see included in the main tree, open a PR on this repo.

To start developing `igraph`, follow the steps above about installing the development version. Make sure that you do so by cloning the repository locally so that you are able to make changes.

For easier development, you can install `igraph` in "editable" (i.e.
development) mode so your changes in the Python source code are picked up
automatically by Python:

```bash
pip install -e .
```

Changes that you make to the Python code do not need any extra action. However,
if you adjust the source code of the C extension, you need to rebuild it by running
`pip install -e .` again. Compilation of the C core of `igraph` is
cached in ``vendor/build`` and ``vendor/install`` so subsequent builds are much
faster than the first one as the C core does not need to be recompiled.

# Notes

## Supported Python versions

We aim to keep up with the development cycle of Python and support all official
Python versions that have not reached their end of life yet. Currently this
means that we support Python 3.9 to 3.13, inclusive. Please refer to [this
page](https://devguide.python.org/versions/) for the status of Python
branches and let us know if you encounter problems with `igraph` on any
of the non-EOL Python versions.

Continuous integration tests are regularly executed on all non-EOL Python
branches.

## PyPy

This version of igraph is compatible with [PyPy](http://pypy.org/) and
is regularly tested on [PyPy](http://pypy.org/) with ``tox``. However, the
PyPy version falls behind the CPython version in terms of performance; for
instance, running all the tests takes ~5 seconds on my machine with CPython and
~15 seconds with PyPy. This can probably be attributed to the need for
emulating CPython reference counting, and does not seem to be alleviated by the
JIT.

There are also some subtle differences between the CPython and PyPy versions:

- Docstrings defined in the C source code are not visible from PyPy.

- ``GraphBase`` is hashable and iterable in PyPy but not in CPython. Since
  ``GraphBase`` is internal anyway, this is likely to stay this way.
