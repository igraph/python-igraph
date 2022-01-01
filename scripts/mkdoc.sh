#!/bin/bash
#
# Creates the API documentation for igraph's Python interface using PyDoctor
#
# Usage: ./mkdoc.sh (makes API and tutorial docs)

SCRIPTS_FOLDER=`dirname $0`

cd ${SCRIPTS_FOLDER}/..
ROOT_FOLDER=`pwd`
DOC_SOURCE_FOLDER=${ROOT_FOLDER}/doc/source
DOC_HTML_FOLDER=${ROOT_FOLDER}/doc/html

cd ${ROOT_FOLDER}

# Create a virtual environment
if [ ! -d ".venv" ]; then
  python3 -m venv .venv

  # Install sphinx, matplotlib, wheel, and pydoctor into the venv
  .venv/bin/pip install sphinx sphinxbootstrap4theme sphinx-panels matplotlib
  .venv/bin/pip install -U pydoctor wheel 
  
  echo "Patching PyDoctor..."
  $SCRIPTS_FOLDER/patch-pydoctor.sh ${ROOT_FOLDER} ${SCRIPTS_FOLDER}

fi

echo "Removing existing igraph and python-igraph eggs from virtualenv..."
SITE_PACKAGES_DIR=`.venv/bin/python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'`
rm -rf "${SITE_PACKAGES_DIR}"/igraph*.egg
rm -rf "${SITE_PACKAGES_DIR}"/igraph*.egg-link
rm -rf "${SITE_PACKAGES_DIR}"/python_igraph*.egg
rm -rf "${SITE_PACKAGES_DIR}"/python_igraph*.egg-link

echo "Installing igraph in virtualenv..."
rm -f dist/*.whl && .venv/bin/python setup.py bdist_wheel && .venv/bin/pip install --force-reinstall dist/*.whl

echo "Patching modularized Graph methods"
.venv/bin/python3 ${SCRIPTS_FOLDER}/patch_modularized_graph_methods.py


# Remove previous docs
rm -rf "${DOC_HTML_FOLDER}"


# Make sphinx
echo "Generating HTML documentation..."
.venv/bin/python -m sphinx.cmd.build ${DOC_SOURCE_FOLDER} ${DOC_HTML_FOLDER}

#PWD=`pwd`
#DOC_API_FOLDER=${ROOT_FOLDER}/doc/api
#DOC2DASH=`which doc2dash 2>/dev/null || true`
#if [ "x$DOC2DASH" != x ]; then
#    echo "Generating Dash docset..."
#    "$DOC2DASH" \
#        --online-redirect-url "https://igraph.org/python/doc/api" \
#        --name "python-igraph" \
#        -d "${DOC_API_FOLDER}" \
#	    -f \
#        "${DOC_API_FOLDER}/html"
#    DASH_READY=1
#else 
#    echo "WARNING: doc2dash not installed, skipping Dash docset generation."
#    DASH_READY=0
#fi
#
#echo ""
#echo "HTML documentation generated in ${DOC_HTML_FOLDER}/html"
#if [ "x${DASH_READY}" = x1 ]; then
#    echo "Dash docset generated in ${DOC_API_FOLDER}/python-igraph.docset"
#fi
#
#cd "$PWD"

