
[![](https://travis-ci.org/igraph/python-igraph.svg?branch=master)](https://travis-ci.org/igraph/python-igraph)

Python interface for the igraph library
---------------------------------------

igraph is a library for creating and manipulating graphs. 
It is intended to be as powerful (ie. fast) as possible to enable the
analysis of large graphs. 

This repository contains the source code to the Python interface of
igraph.

## Install
```
$ sudo python setup.py install
```
See details in [Installing Python Modules](https://docs.python.org/2/install/).

## Notes

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
