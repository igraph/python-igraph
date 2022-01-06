#!/bin/bash
# Patches PyDoctor to make it suitable to build python-igraph's documentation
# until our patches get upstreamed

if [ "x$1" = x ]; then
    echo "Usage: $0 ROOT_FOLDER PATCH_FOLDER"
    exit 1
fi

set -e

ROOT_FOLDER=$1
PATCH_FOLDER=$(realpath $2)
${ROOT_FOLDER}/.venv/bin/pip uninstall -y pydoctor
#${ROOT_FOLDER}/.venv/bin/pip install pydoctor==21.2.2
${ROOT_FOLDER}/.venv/bin/pip install pydoctor==21.12.0
PYDOCTOR_DIR=`.venv/bin/python -c 'import os,pydoctor;print(os.path.dirname(pydoctor.__file__))'`

cd "${PYDOCTOR_DIR}"
## patch is confirmed to work with pydoctor 21.2.2
#echo "First patch"
#patch -r deleteme.rej -N -p2 <${PATCH_FOLDER}/pydoctor-21.2.2.patch 2>/dev/null
#rm -f deleteme.rej
#
## patch sphinx extension
#echo "Second patch"
#patch -r deleteme.rej -N -p2 <${PATCH_FOLDER}/pydoctor-21.2.2_sphinx_ext.patch 2>/dev/null
#rm -f deleteme.rej

echo "New patch against 21.12.0"
patch -r deleteme.rej -N -p2 <${PATCH_FOLDER}/0001-Old-patch-renewed.patch 2>/dev/null
rm -f deleteme.rej
