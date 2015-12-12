
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
~15 seconds with PyPy.

There are also some subtle differences between the CPython and PyPy versions:

- There is only limited support for saving and loading graphs in PyPy --
  loading and saving works only if the file is specified as a string
  containing a filename. File-like objects are not supported as the PyPy API
  does not implement ``PyFile_AsFile``.

- Docstrings defined in the C source code are not visible from PyPy.

- ``GraphBase`` is hashable and iterable in PyPy but not in CPython. Since
  ``GraphBase`` is internal anyway, this is likely to stay this way.
