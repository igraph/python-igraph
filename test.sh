#!/bin/bash

PYTHON=python3

###############################################################################

set -e

CLEAN=0
VENV_DIR=.venv

while getopts ":ce:k:s" OPTION; do
    case $OPTION in
        c)
            CLEAN=1
            ;;
        e)
            VENV_DIR=$OPTARG
            ;;
        k)
            PYTEST_ARGS="${PYTEST_ARGS} -k $OPTARG"
            ;;
        s)
            USE_SANITIZERS=1
            ;;
        \?)
            echo "Usage: $0 [-c] [-e VIRTUALENV] [-s]"
            echo ""
            echo "Options:"
            echo "  -c: clean igraph's already-built C core before running tests"
            echo "  -e VIRTUALENV: use the given virtualenv instead of .venv"
            echo "  -s: compile the C core and the Python module with sanitizers enabled"
			exit 1
            ;;
    esac
done
shift $((OPTIND -1))

if [ "x$USE_SANITIZERS" = x1 ]; then
  if [ "`python3 -c 'import platform; print(platform.system())'`" != "Linux" ]; then
    echo "Compiling igraph with sanitizers is currently supported on Linux only."
    exit 1
  fi
fi

if [ ! -d $VENV_DIR ]; then
    $PYTHON -m venv $VENV_DIR
    $VENV_DIR/bin/pip install -U pip wheel
fi

rm -rf build/
if [ x$CLEAN = x1 ]; then
    rm -rf vendor/build vendor/install
fi

# pip install is called in verbose mode so we can see the compiler warnings
if [ "x$USE_SANITIZERS" = x1 ]; then
  # Do not run plotting tests -- they tend to have lots of false positives in
  # the sanitizer output
  IGRAPH_USE_SANITIZERS=1 $VENV_DIR/bin/pip install -v .[test]
  LD_PRELOAD=$(gcc -print-file-name=libasan.so) \
  LSAN_OPTIONS=suppressions=etc/lsan-suppr.txt:print_suppressions=false \
  ASAN_OPTIONS=detect_stack_use_after_return=1 \
  $VENV_DIR/bin/pytest tests ${PYTEST_ARGS}
else
  $VENV_DIR/bin/pip install -v .[plotting,test]
  $VENV_DIR/bin/pytest tests ${PYTEST_ARGS}
fi

