#!/bin/bash
#
# Creates the API documentation for igraph's Python interface using PyDoctor
#
# Usage: ./mkdoc.sh (makes API and tutorial docs)
#        ./mkdoc.sh -s (makes standalone docs that require no further processing)

STANDALONE=0
SERVE=0

while getopts ":s:j" OPTION; do
  case $OPTION in
    s)
      STANDALONE=1
      ;;
    j)
      SERVE=1
      ;;      
    \?)
      echo "Usage: $0 [-sj]"
      ;;
    esac
done
shift $((OPTIND -1))

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
  .venv/bin/pip install sphinx sphinxbootstrap4theme matplotlib
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
if [ "x$STANDALONE" = "x1" ]; then
  .venv/bin/sphinx-build \
   -Dtemplates_path='' \
   -Dhtml_theme='alabaster' \
   ${DOC_SOURCE_FOLDER} ${DOC_HTML_FOLDER}
else
  .venv/bin/sphinx-build ${DOC_SOURCE_FOLDER} ${DOC_HTML_FOLDER}

  if [ "x$SERVE" = "x1" ]; then
    cd doc/html

    # Copy jekyll build environment
    cp -r ../jekyll_tools/* ./

    # Install jekyll infra
    bundle config set --local path 'vendor/bundle'
    bundle install

    # TODO: copy back?

    # Build website via templates
    bundle exec jekyll serve
  
  fi
fi

  

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

