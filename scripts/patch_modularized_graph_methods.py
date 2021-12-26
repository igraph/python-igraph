import os
import sys
import inspect

import igraph


def main():

    # Get instance and classmethods
    g = igraph.Graph()
    methods = inspect.getmembers(g, predicate=inspect.ismethod)

    # Get the source code for each method and replace the method name
    # in the signature
    methodsources = {}
    underscore_functions= set()
    for mname, method in methods:
        # Source code of the function that uses the method
        source = inspect.getsourcelines(method)[0]

        # Find function name for this modularized method
        fname = source[0][source[0].find('def ') + 4: source[0].find('(')]

        # FIXME: this also swaps in methods that are already there. While
        # that should be fine, we could check

        # Make new source code, which is the same but with the name swapped
        newsource = [source[0].replace(fname, mname)] + source[1:]

        methodsources[mname] = newsource

        # Prepare to delete the import for underscore functions
        if fname.startswith('_'):
            underscore_functions.add(fname)

    # Make .new file with replacements
    def write_import_lines(fout, curmodule):
        if curmodule['name'] is None:
            return
        lines = curmodule['imports']
        fnames_new = []
        for line in lines:
            fnames = line.lstrip().rstrip('\n').split(',')
            for fname in fnames:
                fname = fname.strip()
                if fname in ('', '(', ')'):
                    continue
                if fname in underscore_functions:
                    underscore_functions.remove(fname)
                else:
                    fnames_new.append(fname)

        lines_out = []
        if len(fnames_new):
            lines_out.append('from '+curmodule['name']+' import (')
            for fname in fnames_new:
                lines_out.append('    '+fname+',')
            lines_out.append(')')
            lines_out.append('')
        lines_out = '\n'.join(lines_out)
        if lines_out:
            fout.write(lines_out)

    newmodule = igraph.__file__ + '.new'
    with open(newmodule, 'wt') as fout:
        with open(igraph.__file__, 'rt') as f:
            # Delete imported underscore functions
            curmodule = {'name': None, 'imports': []}
            for line in f:
                if line.startswith('# END OF IMPORTS'):
                    write_import_lines(fout, curmodule)
                    break

                # Vanilla imports
                if line.startswith('import'):
                    write_import_lines(fout, curmodule)
                    curmodule = {'name': None, 'imports': []}
                    fout.write(line)
                    continue

                if line.startswith('from'):
                    write_import_lines(fout, curmodule)
                    idx = line.find('import')
                    modname = line[:idx].split()[1]
                    line = line[idx + len('import') + 1:]
                    curmodule = {'name': modname, 'imports': [line]}
                    continue

                curmodule['imports'].append(line)

            # Swap in the method sources
            for line in f:
                if '# Remove modular methods from namespace' in line:
                    break

                mtype = None
                for mname in methodsources:
                    # Class methods (constructors)
                    if mname + ' = classmethod(_' in line:
                        mtype = 'class'
                        break

                    # Instance methods (excluding factories e.g. 3d layouts)
                    if (mname + ' = _' in line) and ('(' not in line):
                        mtype = 'instance'
                        break

                else:
                    fout.write(line)
                    continue

                # Method found, substitute
                fout.write('\n')
                if mtype == 'class':
                    fout.write('    @classmethod\n')
                for mline in methodsources[mname]:
                    # Correct indentation
                    fout.write('    ' + mline)

    # Move the new file back
    with open(igraph.__file__, 'wt') as fout:
        with open(newmodule, 'rt') as f:
            fout.write(f.read())

    # Delete .new file
    os.remove(newmodule)


if __name__ == '__main__':
    main()
