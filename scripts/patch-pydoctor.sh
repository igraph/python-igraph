#!/bin/bash
# Patches PyDoctor to make it suitable to build python-igraph's documentation
# until our patches get upstreamed

set -e

SCRIPTS_FOLDER=`dirname $0`

cd ${SCRIPTS_FOLDER}/..
ROOT_FOLDER=`pwd`
PATCH_FOLDER=${ROOT_FOLDER}/scripts

${ROOT_FOLDER}/.venv/bin/pip uninstall -y pydoctor
${ROOT_FOLDER}/.venv/bin/pip install pydoctor==21.2.2
PYDOCTOR_DIR=`.venv/bin/python -c 'import os,pydoctor;print(os.path.dirname(pydoctor.__file__))'`

cd "${PYDOCTOR_DIR}"
# patch is confirmed to work with pydoctor 21.2.2
patch -r deleteme.rej -N -p2 <${PATCH_FOLDER}/pydoctor-21.2.2.patch 2>/dev/null
rm -f deleteme.rej


