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
    .venv/bin/pip install pydoctor
fi

PYDOCTOR=.venv/bin/pydoctor
if [ ! -f ${PYDOCTOR} ]; then
  echo "PyDoctor not installed in the virtualenv of the project, exiting..."
  exit 1
fi

PWD=`pwd`

echo "Removing existing documentation..."
rm -rf "${DOC_API_FOLDER}/html" "${DOC_API_FOLDER}/pdf"

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

