#!/bin/bash
#
# Creates the API documentation for igraph's Python interface using PyDoctor
#
# Usage: ./mkdoc.sh (makes API docs)
#        ./mkdoc.sh -t (makes tutorials)


DOC_TYPE=api

while getopts ":t::" OPTION; do
  case $OPTION in
    t)
      DOC_TYPE=tutorial
    ;;
    \?)
      echo "Usage: $0 [-t]"
	;;
  esac
done


SCRIPTS_FOLDER=`dirname $0`

cd ${SCRIPTS_FOLDER}/..
ROOT_FOLDER=`pwd`
DOC_SOURCE_FOLDER=${ROOT_FOLDER}/doc/source
DOC_API_FOLDER=${ROOT_FOLDER}/doc/api
DOC_TUTORIAL_FOLDER=${ROOT_FOLDER}/doc/tutorial

cd ${ROOT_FOLDER}

# Create a virtual environment
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Make tutorial only if requested
if [ ${DOC_TYPE} == "tutorial" ]; then
    # Install pydoctor into the venv
    .venv/bin/pip install sphinx sphinxbootstrap4theme

    # Make sphinx tutorials
    .venv/bin/python -m sphinx.cmd.build ${DOC_SOURCE_FOLDER} ${DOC_TUTORIAL_FOLDER}
    exit $?
fi

# Install pydoctor into the venv
.venv/bin/pip install -U pydoctor wheel
PYDOCTOR=.venv/bin/pydoctor
if [ ! -f ${PYDOCTOR} ]; then
  echo "PyDoctor not installed in the virtualenv of the project, exiting..."
  exit 1
fi

PWD=`pwd`

echo "Patching PyDoctor..."
$SCRIPTS_FOLDER/patch-pydoctor.sh ${ROOT_FOLDER} ${SCRIPTS_FOLDER}

echo "Removing existing documentation..."
rm -rf "${DOC_API_FOLDER}/html" "${DOC_API_FOLDER}/pdf"

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

echo "Generating HTML documentation..."
IGRAPHDIR=`.venv/bin/python3 -c 'import igraph, os; print(os.path.dirname(igraph.__file__))'`
"$PYDOCTOR" \
    --project-name "igraph" \
    --project-url "https://igraph.org/python" \
    --introspect-c-modules \
    --make-html \
    --html-output "${DOC_API_FOLDER}/html" \
	${IGRAPHDIR}

# PDF not supported by PyDoctor

DOC2DASH=`which doc2dash 2>/dev/null || true`
if [ "x$DOC2DASH" != x ]; then
    echo "Generating Dash docset..."
    "$DOC2DASH" \
        --online-redirect-url "https://igraph.org/python/doc/api" \
        --name "python-igraph" \
        -d "${DOC_API_FOLDER}" \
	    -f \
        "${DOC_API_FOLDER}/html"
    DASH_READY=1
else 
    echo "WARNING: doc2dash not installed, skipping Dash docset generation."
    DASH_READY=0
fi

echo ""
echo "HTML API documentation generated in ${DOC_API_FOLDER}/html"
if [ "x${DASH_READY}" = x1 ]; then
    echo "Dash docset generated in ${DOC_API_FOLDER}/python-igraph.docset"
fi

cd "$PWD"

