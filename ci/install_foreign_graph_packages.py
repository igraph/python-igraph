# Install foreign graph packages to test import/export functions on CI
import sys
import subprocess as sp

# Networkx via pip
call = 'pip install networkx'
call = call.split()
try:
    sp.run(call)
except AttributeError:
    sp.call(call)


# Graph-tool (TODO)
