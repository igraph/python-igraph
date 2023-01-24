#!/bin/bash
#
# Creates the API documentation for igraph's Python interface
#
# Usage: ./mkdoc.sh (makes API and tutorial docs)
#        ./mkdoc.sh -s (makes standalone docs that require no further processing)
#        ./mkdoc.sh -sd (makes a Dash docset based on standalone docs, requires doc2dash)

# Make sure we bail out on build errors
set -e

STANDALONE=0
SERVE=0
DOC2DASH=0
LINKCHECK=0

while getopts ":sjdl" OPTION; do
  case $OPTION in
    s)
      STANDALONE=1
      ;;
    j)
      SERVE=1
      ;;
    d)
      DOC2DASH=1
      ;;
    l)
      LINKCHECK=1
      ;;
    \?)
      echo "Usage: $0 [-sjd]"
      exit 1
      ;;
    esac
done
shift $((OPTIND -1))

SCRIPTS_FOLDER=`dirname $0`

cd ${SCRIPTS_FOLDER}/..
ROOT_FOLDER=`pwd`
DOC_SOURCE_FOLDER=${ROOT_FOLDER}/doc/source
DOC_HTML_FOLDER=${ROOT_FOLDER}/doc/html
DOC_LINKCHECK_FOLDER=${ROOT_FOLDER}/doc/linkcheck
SCRIPTS_FOLDER=${ROOT_FOLDER}/scripts

cd ${ROOT_FOLDER}

# Create a virtual environment
if [ ! -d ".venv" ]; then
  python3 -m venv .venv

  # Install sphinx, matplotlib, wheel and pydoctor into the venv.
  # doc2dash is optional; it will be installed when -d is given
  .venv/bin/pip install -U pip sphinx sphinxbootstrap4theme matplotlib wheel pydoctor
fi

# Make sure that Sphinx, PyDoctor (and maybe doc2dash) are up-to-date in the virtualenv
.venv/bin/pip install -U sphinx pydoctor sphinxbootstrap4theme sphinx-gallery sphinxcontrib-jquery
if [ x$DOC2DASH = x1 ]; then
    .venv/bin/pip install -U doc2dash
fi

#echo "Set PyDoctor theme"
#$SCRIPTS_FOLDER/set-pydoctor-theme.sh ${ROOT_FOLDER} ${STANDALONE}

echo "Removing existing igraph and python-igraph eggs from virtualenv..."
SITE_PACKAGES_DIR=`.venv/bin/python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'`
rm -rf "${SITE_PACKAGES_DIR}"/igraph*.egg
rm -rf "${SITE_PACKAGES_DIR}"/igraph*.egg-link
rm -rf "${SITE_PACKAGES_DIR}"/python_igraph*.egg
rm -rf "${SITE_PACKAGES_DIR}"/python_igraph*.egg-link

echo "Installing igraph in virtualenv..."
rm -f dist/*.whl && .venv/bin/pip wheel -q -w dist . && .venv/bin/pip install -q --force-reinstall dist/*.whl

echo "Patching modularized Graph methods"
.venv/bin/python3 ${SCRIPTS_FOLDER}/patch_modularized_graph_methods.py


echo "Clean previous docs"
rm -rf "${DOC_HTML_FOLDER}"


if [ "x$LINKCHECK" = "x1" ]; then
  echo "Check for broken links"
  .venv/bin/python -m sphinx \
   -T \
   -b linkcheck \
   -Dtemplates_path='' \
   -Dhtml_theme='alabaster' \
   ${DOC_SOURCE_FOLDER} ${DOC_LINKCHECK_FOLDER}
fi


echo "Generating HTML documentation..."
if [ "x$STANDALONE" = "x1" ]; then
  echo "Build standalone docs"
  .venv/bin/pip install -U sphinx-rtd-theme
  READTHEDOCS="True" .venv/bin/python -m sphinx \
   -T \
   -b html \
   ${DOC_SOURCE_FOLDER} ${DOC_HTML_FOLDER}
else
  echo "Build Jekyll-style docs"
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

echo "HTML documentation generated in ${DOC_HTML_FOLDER}"


# doc2dash
if [ "x$DOC2DASH" = "x1" ]; then
  PWD=`pwd`
  # Output folder of sphinx (before Jekyll if requested)
  DOC_API_FOLDER=${ROOT_FOLDER}/doc/html/api
  DOC2DASH=`which doc2dash 2>/dev/null || true`
  DASH_FOLDER=${ROOT_FOLDER}/doc/dash
  if [ "x$DOC2DASH" != x ]; then
      echo "Generating Dash docset..."
      "$DOC2DASH" \
          --online-redirect-url "https://igraph.org/python/api/latest" \
          --name "python-igraph" \
          -d "${DASH_FOLDER}" \
          -f \
          -j \
          -I "index.html" \
          "${DOC_API_FOLDER}"
      DASH_READY=1
  else
      echo "WARNING: doc2dash not installed, skipping Dash docset generation."
      DASH_READY=0
  fi

  echo ""
  if [ "x${DASH_READY}" = x1 ]; then
      echo "Dash docset generated in ${DASH_FOLDER}/python-igraph.docset"
  fi

  cd "$PWD"
fi
