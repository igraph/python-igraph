#!/bin/sh

echo "Compile and install igraph into venv. This might take a few minutes..."
/home/docs/checkouts/readthedocs.org/user_builds/igraph/envs/${READTHEDOCS_VERSION}/bin/pip wheel -q -w dist .
/home/docs/checkouts/readthedocs.org/user_builds/igraph/envs/${READTHEDOCS_VERSION}/bin/pip install -q --force-reinstall dist/*.whl

echo "Modularize pure Python modules"
/home/docs/checkouts/readthedocs.org/user_builds/igraph/envs/${READTHEDOCS_VERSION}/bin/python3 scripts/patch_modularized_graph_methods.py

echo "NOTE (sigh!): Patch pydoctor to trigger build-finished before RTD extension"
sed -i 's/on_build_finished)/on_build_finished, priority=490)/' /home/docs/checkouts/readthedocs.org/user_builds/igraph/envs/${READTHEDOCS_VERSION}/lib/python3.9/site-packages/pydoctor/sphinx_ext/build_apidocs.py
