#!/bin/sh
#
# Creates the API documentation for igraph's Python interface using PyDoctor
#
# Usage: ./mkdoc.sh [--sync] [directory]

SCRIPTS_FOLDER=`dirname $0`

cd ${SCRIPTS_FOLDER}/..
ROOT_FOLDER=`pwd`
DOC_API_FOLDER=${ROOT_FOLDER}/doc/api

cd ${ROOT_FOLDER}

if [ ! -d ".venv" ]; then
    # Create a virtual environment for pydoctor
    python3 -m venv .venv
    .venv/bin/pip install -U pydoctor wheel
fi

PYDOCTOR=.venv/bin/pydoctor
if [ ! -f ${PYDOCTOR} ]; then
  echo "PyDoctor not installed in the virtualenv of the project, exiting..."
  exit 1
fi

PWD=`pwd`

echo "Removing existing documentation..."
rm -rf "${DOC_API_FOLDER}/html" "${DOC_API_FOLDER}/pdf"

echo "Removing existing python-igraph eggs from virtualenv..."
SITE_PACKAGES_DIR=`.venv/bin/python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'`
rm -rf "${SITE_PACKAGES_DIR}"/python_igraph*.egg
rm -rf "${SITE_PACKAGES_DIR}"/python_igraph*.egg-link

echo "Installing python-igraph in virtualenv..."
rm -f dist/*.whl && .venv/bin/python setup.py bdist_wheel && .venv/bin/pip install dist/*.whl

IGRAPHDIR=`.venv/bin/python3 -c 'import igraph, os; print(os.path.dirname(igraph.__file__))'`

echo "Generating HTML documentation..."
"$PYDOCTOR" \
    --project-name "python-igraph" \
    --project-url "https://igraph.org/python" \
    --introspect-c-modules \
    --make-html \
    --html-output "${DOC_API_FOLDER}/html" \
	${IGRAPHDIR}

# PDF not supported by PyDoctor

cd "$PWD"

