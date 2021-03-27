
[![Build and test with tox](https://github.com/igraph/python-igraph/actions/workflows/build.yml/badge.svg)](https://github.com/igraph/python-igraph/actions/workflows/build.yml)
[![PyPI pyversions](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-blue)](https://pypi.python.org/pypi/python-igraph)
[![PyPI wheels](https://img.shields.io/pypi/wheel/python-igraph.svg)](https://pypi.python.org/pypi/python-igraph)

Python interface for the igraph library
---------------------------------------

igraph is a library for creating and manipulating graphs.
It is intended to be as powerful (ie. fast) as possible to enable the
analysis of large graphs.

This repository contains the source code to the Python interface of
igraph.

You can learn more about python-igraph [on our website](http://igraph.org/python/).

## Installation from PyPI

We aim to provide wheels on PyPI for most of the stock Python versions;
typically the three most recent minor releases from Python 3.x. Therefore,
running the following command should work without having to compile anything
during installation:

```
pip install python-igraph
```

See details in [Installing Python Modules](https://docs.python.org/3/installing/).

### Installation from source with pip on Debian / Ubuntu and derivatives

If you need to compile python-igraph from source for some reason, you need to
install some dependencies first:

```
sudo apt install build-essential python-dev libxml2 libxml2-dev zlib1g-dev
```

and then run

```
pip install python-igraph
```

This should compile the C core of igraph as well as the Python extension
automatically.

### Installation from source on Windows

It is now also possible to compile `python-igraph` from source under Windows for
Python 3.6 and later. Make sure that you have Microsoft Visual Studio 2015 or
later installed, and of course Python 3.6 or later. First extract the source to
a suitable directory. If you launch the Developer command prompt and navigate to
the directory where you extracted the source code, you should be able to build
and install python-igraph using `python setup.py install`

You may need to set the architecture that you are building on explicitly by setting the environment variable

```
set IGRAPH_CMAKE_EXTRA_ARGS=-A [arch]
```

where `[arch]` is either `Win32` for 32-bit builds or `x64` for 64-bit builds.

#### Enabling GraphML

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

which we will do next. In order to build `python-igraph` correctly, you also
need to set some other environment variables before building `python-igraph`:

```
set IGRAPH_CMAKE_EXTRA_ARGS=-DVCPKG_TARGET_TRIPLET=x64-windows-static-md -DCMAKE_TOOLCHAIN_FILE=[vcpkg build script]
set IGRAPH_EXTRA_LIBRARY_PATH=[vcpkg directory]/installed/x64-windows-static-md/lib/
set IGRAPH_STATIC_EXTENSION=True
set IGRAPH_EXTRA_LIBRARIES=libxml2,lzma,zlib,iconv,charset
set IGRAPH_EXTRA_DYNAMIC_LIBRARIES: wsock32,ws2_32
```

You can now build and install `python-igraph` again by simply running `python
setup.py build`. Please make sure to use a clean source tree, if you built
previously without GraphML, it will not update the build.

### Linking to an existing igraph installation

The source code of the Python package includes the source code of the matching
igraph version that the Python interface should compile against. However, if
you want to link the Python interface to a custom installation of the C core
that has already been compiled and installed on your system, you can ask
`setup.py` to use the pre-compiled version. This option requires that your
custom installation of igraph is discoverable with `pkg-config`. First, check
whether `pkg-config` can tell you the required compiler and linker flags for
igraph:

```bash
pkg-config --cflags --libs igraph
```

If `pkg-config` responds with a set of compiler and linker flags and not an
error message, you are probably okay. You can then proceed with the
installation using pip:

```bash
pip install python-igraph --install-option="--use-pkg-config"
```

Alternatively, if you have already downloaded and extracted the source code
of igraph, you can run `setup.py` directly:

```bash
python setup.py build --use-pkg-config
```

This option is primarily intended for package maintainers in Linux
distributions so they can ensure that the packaged Python interface links to
the packaged igraph library instead of bringing its own copy.

It is also useful on macOS if you want to link to the igraph library installed
from Homebrew.

Due to the lack of support of `pkg-config` on Window, it is currently not
possible to build against an external library on Windows.

## Compiling the development version

If you have downloaded the source code from Github and not PyPI, chances are
that you have the latest development version, which contains a matching version
of the C core of igraph as a git submodule. Therefore, to install the bleeding
edge version, you need to instruct git to check out the submodules first:

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

Then, running the setup script should work if you have a C compiler and the
necessary build dependencies (see the previous section):

```bash
python setup.py build
```

## Running unit tests

Unit tests can be executed from the project directory with `tox` or with the
built-in unittest module:

```bash
python -m unittest
```

## Contributing

Contributions to `python-igraph` are welcome!

If you want to add a feature, fix a bug, or suggest an improvement, open an
issue on this repository and we'll try to answer. If you have a piece of code
that you would like to see included in the main tree, open a PR on this repo.

To start developing `python-igraph`, follow the steps below (these are
for Linux, Windows users should change the system commands a little).

First, clone this repo (e.g. via https) and enter the folder:

```bash
git clone https://github.com/igraph/python-igraph.git
cd python-igraph
```

Second, check out the necessary git submodules:

```bash
git submodule update --init
```

and install igraph in development mode so your changes in the Python source
code are picked up automatically by Python:

```bash
python setup.py develop
```

**NOTE**: Building requires `CMake`, a C compiler, and a few more dependencies.

Changes that you make to the Python code do not need any extra action. However,
if you adjust the source code of the C extension, you need to rebuild it by running
`python setup.py develop` again. However, compilation of igraph's C core is
cached in ``vendor/build`` and ``vendor/install`` so subsequent builds are much
faster than the first one as the C core does not need to be recompiled.

## Notes

### Supported Python versions

We aim to keep up with the development cycle of Python and support all official
Python versions that have not reached their end of life yet. Currently this
means that we support Python 3.6 to 3.9, inclusive. Please refer to [this
page](https://devguide.python.org/#branchstatus) for the status of Python
branches and let us know if you encounter problems with `python-igraph` on any
of the non-EOL Python versions.

Continuous integration tests are regularly executed on all non-EOL Python
branches.

Python 2 support has been dropped with the release of `python-igraph` 0.9.

### PyPy

This version of python-igraph is compatible with [PyPy](http://pypy.org/) and
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

