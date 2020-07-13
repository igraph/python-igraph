#!/bin/sh
#
# Creates documentation for igraph's Python interface using epydoc
#
# Usage: ./mkdoc.sh [--sync] [directory]

SCRIPTS_FOLDER=`dirname $0`

cd ${SCRIPTS_FOLDER}/..
ROOT_FOLDER=`pwd`
DOC_API_FOLDER=${ROOT_FOLDER}/doc/api
CONFIG=${ROOT_FOLDER}/scripts/epydoc.cfg

cd ${ROOT_FOLDER}
mkdir -p ${DOC_API_FOLDER}/pdf
mkdir -p ${DOC_API_FOLDER}/html

EPYDOC="${ROOT_FOLDER}/scripts/epydoc-patched"
python -m epydoc.__init__
if [ $? -gt 0 ]; then
  echo "Epydoc not installed, exiting..."
  exit 1
fi

PWD=`pwd`

echo "Checking symlinked _igraph.so in ${ROOT_FOLDER}/src/igraph..."
if [ ! -e ${ROOT_FOLDER}/src/igraph/_igraph.so -o ! -L ${ROOT_FOLDER}/src/igraph/_igraph.so ]; then
	rm -f ${ROOT_FOLDER}/src/igraph/_igraph.so
	cd ${ROOT_FOLDER}/src/igraph
	ln -s ../../build/lib*/igraph/_igraph.so .
	cd ${ROOT_FOLDER}
fi

echo "Removing existing documentation..."
rm -rf html

echo "Generating HTML documentation..."
PYTHONPATH=src ${EPYDOC} --html -v -o ${DOC_API_FOLDER}/html --config ${CONFIG}

PDF=0
which latex >/dev/null && PDF=1

if [ $PDF -eq 1 ]; then
  echo "Generating PDF documentation..."
  PYTHONPATH=src ${EPYDOC} --pdf -v -o ${DOC_API_FOLDER}/pdf --config ${CONFIG}
fi

cd "$PWD"
