#!/bin/sh

set -e

echo "Compile and install igraph into venv. This might take a few minutes..."
/home/docs/checkouts/readthedocs.org/user_builds/igraph/envs/${READTHEDOCS_VERSION}/bin/pip wheel -q -w dist .
/home/docs/checkouts/readthedocs.org/user_builds/igraph/envs/${READTHEDOCS_VERSION}/bin/pip install -q --force-reinstall dist/*.whl

echo "Modularize pure Python modules"
/home/docs/checkouts/readthedocs.org/user_builds/igraph/envs/${READTHEDOCS_VERSION}/bin/python3 scripts/patch_modularized_graph_methods.py

echo "NOTE: Patch pydoctor to trigger build-finished before RTD extension"
# see https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx.application.Sphinx.connect
# see also https://github.com/readthedocs/readthedocs.org/pull/4054 - might or might not be exactly what we are seeing here
sed -i 's/on_build_finished)/on_build_finished, priority=490)/' /home/docs/checkouts/readthedocs.org/user_builds/igraph/envs/${READTHEDOCS_VERSION}/lib/python3.11/site-packages/pydoctor/sphinx_ext/build_apidocs.py
