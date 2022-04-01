#!/bin/sh
#
# Creates the API documentation for igraph's Python interface using PyDoctor
#
# Usage: ./mkdoc.sh

SCRIPTS_FOLDER=`dirname $0`

cd ${SCRIPTS_FOLDER}/..
ROOT_FOLDER=`pwd`
SCRIPTS_FOLDER=${ROOT_FOLDER}/scripts
DOC_API_FOLDER=${ROOT_FOLDER}/doc/api

cd ${ROOT_FOLDER}

if [ ! -d ".venv" ]; then
  python3 -m venv .venv

  # Install sphinx, matplotlib, wheel, and pydoctor into the venv
  .venv/bin/pip install -U pip sphinx sphinxbootstrap4theme matplotlib wheel pydoctor
fi

PYDOCTOR=.venv/bin/pydoctor
if [ ! -f ${PYDOCTOR} ]; then
  echo "PyDoctor not installed in the virtualenv of the project, exiting..."
  exit 1
fi

PWD=`pwd`

echo "Removing existing documentation..."
rm -rf "${DOC_API_FOLDER}/html" "${DOC_API_FOLDER}/pdf"

echo "Removing existing igraph and python-igraph eggs from virtualenv..."
SITE_PACKAGES_DIR=`.venv/bin/python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'`
rm -rf "${SITE_PACKAGES_DIR}"/igraph*.egg
rm -rf "${SITE_PACKAGES_DIR}"/igraph*.egg-link
rm -rf "${SITE_PACKAGES_DIR}"/python_igraph*.egg
rm -rf "${SITE_PACKAGES_DIR}"/python_igraph*.egg-link

echo "Installing igraph in virtualenv..."
rm -f dist/*.whl && .venv/bin/pip install .

IGRAPHDIR=`.venv/bin/python3 -c 'import igraph, os; print(os.path.dirname(igraph.__file__))'`

echo "Generating HTML documentation..."
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

