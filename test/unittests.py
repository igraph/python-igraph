#!/usr/bin/env python
"""
Simple script that runs the unit tests of igraph.
"""

import sys

def run_unittests():
    from igraph.test import run_tests
    if "-v" in sys.argv:
        verbosity = 2
    else:
        verbosity = 1
    run_tests(verbosity=verbosity)

if __name__ == "__main__":
    run_unittests()
