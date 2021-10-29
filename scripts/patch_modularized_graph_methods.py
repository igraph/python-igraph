import os
import sys
import inspect

import igraph


# Get instance and classmethods
g = igraph.Graph()
methods = inspect.getmembers(g, predicate=inspect.ismethod)

# Get the source code for each method and replace the method name
# in the signature
methodsources = {}
for mname, method in methods:
    source = inspect.getsourcelines(method)[0]
    fname = source[0][source[0].find('def ') + 4: source[0].find('(')]
    newsource = [source[0].replace(fname, mname)] + source[1:]
    methodsources[mname] = newsource

# Make .new file with replacements
newmodule = igraph.__file__ + '.new'
with open(newmodule, 'wt') as fout:
    with open(igraph.__file__, 'rt') as f:
        for line in f:
            for mname in methodsources:
                # Catch the methods, excluding factories (e.g. 3d layouts)
                if (mname + ' = _' in line) and ('(' not in line):
                    break
            else:
                fout.write(line)
                continue

            # Method found, substitute
            fout.write('\n')
            for mline in methodsources[mname]:
                # Correct indentation
                fout.write('    ' + mline)

# Move the new file back
with open(igraph.__file__, 'wt') as fout:
    with open(newmodule, 'rt') as f:
        fout.write(f.read())

# Delete .new file
os.remove(newmodule)
