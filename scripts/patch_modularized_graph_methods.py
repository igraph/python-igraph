import os
import inspect

import igraph


# FIXME: there must be a better way to do this
auxiliary_imports = [
    ("typing", "*"),
    ("igraph.io.files", "_identify_format"),
    ("igraph.community", "_optimal_cluster_count_from_merges_and_modularity"),
]


def main():
    # Get instance and classmethods
    g = igraph.Graph()
    methods = inspect.getmembers(g, predicate=inspect.ismethod)

    # Get the source code for each method and replace the method name
    # in the signature
    methodsources = {}
    underscore_functions = set()
    for mname, method in methods:
        # Source code of the function that uses the method
        source = inspect.getsourcelines(method)[0]

        # Find function name for this modularized method
        fname = source[0][source[0].find("def ") + 4 : source[0].find("(")]

        # FIXME: this also swaps in methods that are already there. While
        # that should be fine, we could check

        # Make new source code, which is the same but with the name swapped
        newsource = [source[0].replace(fname, mname)] + source[1:]
        methodsources[mname] = newsource

        # Prepare to delete the import for underscore functions
        if fname.startswith("_"):
            underscore_functions.add(fname)

    newmodule = igraph.__file__ + ".new"
    with open(newmodule, "wt") as fout:
        # FIXME: whitelisting all cases is not great, try to improve
        for origin, value in auxiliary_imports:
            fout.write(f"from {origin} import {value}\n")

        with open(igraph.__file__, "rt") as f:
            # Swap in the method sources
            for line in f:
                mtype = None

                for mname in methodsources:
                    # Class methods (constructors)
                    if " " + mname + " = classmethod(_" in line:
                        mtype = "class"
                        break

                    # Instance methods (excluding factories e.g. 3d layouts)
                    if (" " + mname + " = _" in line) and ("(" not in line):
                        mtype = "instance"
                        break

                else:
                    fout.write(line)
                    continue

                # Method found, substitute and remove from dict
                fout.write("\n")
                if mtype == "class":
                    fout.write("    @classmethod\n")
                for mline in methodsources[mname]:
                    # Correct indentation
                    fout.write("    " + mline)

                del methodsources[mname]

    # Move the new file back
    with open(igraph.__file__, "wt") as fout:
        with open(newmodule, "rt") as f:
            fout.write(f.read())

    # Delete .new file
    os.remove(newmodule)


if __name__ == "__main__":
    main()
