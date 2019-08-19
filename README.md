
[![](https://travis-ci.org/igraph/python-igraph.svg?branch=master)](https://travis-ci.org/igraph/python-igraph)

Python interface for the igraph library
---------------------------------------

igraph is a library for creating and manipulating graphs. 
It is intended to be as powerful (ie. fast) as possible to enable the
analysis of large graphs. 

This repository contains the source code to the Python interface of
igraph.

You can learn more about python-igraph [on our website](http://igraph.org/python/).

## Installation

```
$ sudo python setup.py install
```
See details in [Installing Python Modules](https://docs.python.org/2/install/).

### Installation with pip on Debian / Ubuntu and derivatives

Install dependencies
```
$ sudo apt install build-essential python-dev libxml2 libxml2-dev zlib1g-dev
```
and then
```
$ pip install python-igraph
```

## Compiling the development version

If you have downloaded the source code from Github and not PyPI, chances are
that you have the latest development version, which might not be compatible
with the latest release of the C core of igraph. Therefore, to install the
bleeding edge version, you need to instruct the setup script to download the
latest development version of the C core as well:

```
$ sudo python setup.py develop --no-pkg-config --c-core-url https://github.com/igraph/igraph/archive/master.tar.gz
```

## Contributing

Contributions to `python-igraph` are welcome!

If you want to add a feature, fix a bug, or suggest an improvement, open an
issue on this repository and we'll try to answer. If you have a piece of code
that you would like to see included in the main tree, open a PR on this repo.

To start developing `python-igraph`, follow the steps below (these are
for UNIX, Windows users should change the system commands a little).

First, clone this repo (e.g. via https) and enter the folder:
```bash
git clone https://github.com/igraph/python-igraph.git
cd python-igraph
```
Second, build both `igraph` and `python-igraph` at the same time:
```bash
python setup.py build --c-core-url https://github.com/igraph/igraph/archive/master.tar.gz --no-pkg-config
```
**NOTE**: Building requires `autotools`, a C compiler, and a few more dependencies.

This command creates a subfolder within `build` which you can insert into your
`PYTHONPATH` to import. You need to move out of the main folder to import
because there is a subfolder called `igraph` too. For instance on Linux:
```bash
cd ..
PYTHONPATH=$(pwd)/python-igraph/build/lib.linux-x86_64-3.7:$PYTHONPATH python
>>> import igraph
>>> g = igraph.Graph.Full(10)
...
```
You can now play with your changes and see the results. Every time you
make changes to the `python-graph` code, you need to rebuild by calling
the second step above. After the first build, your `igraph` C core library
is compiled already so rebuilding is much faster.

## Notes

### Pypy
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
