#!/usr/bin/env python
"""
Runs all the doctests in the igraph module
"""

import doctest
import sys


def run_doctests():
    import igraph

    num_failed = 0
    modules = [
        igraph,
        igraph.clustering,
        igraph.cut,
        igraph.datatypes,
        igraph.drawing.utils,
        igraph.formula,
        igraph.statistics,
        igraph.utils,
    ]
    for module in modules:
        num_failed += doctest.testmod(module)[0]
    return num_failed == 0


if __name__ == "__main__":
    if run_doctests():
        sys.exit(0)
    else:
        sys.exit(1)
