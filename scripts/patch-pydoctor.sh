#!/bin/bash
# Patches PyDoctor to make it suitable to build python-igraph's documentation
# until our patches get upstreamed

set -e

SCRIPTS_FOLDER=`dirname $0`

cd ${SCRIPTS_FOLDER}/..
ROOT_FOLDER=`pwd`
PATCH_FOLDER=${ROOT_FOLDER}/scripts

${ROOT_FOLDER}/.venv/bin/pip uninstall -y pydoctor
${ROOT_FOLDER}/.venv/bin/pip install pydoctor==21.12.0
PYDOCTOR_DIR=`.venv/bin/python -c 'import os,pydoctor;print(os.path.dirname(pydoctor.__file__))'`

cd "${PYDOCTOR_DIR}"
echo "Patch against 21.12.0 to fix a bug with C extensions"
patch -r deleteme.rej -N -p2 <${PATCH_FOLDER}/pydoctor-21.12.0.patch 2>/dev/null
rm -f deleteme.rej
