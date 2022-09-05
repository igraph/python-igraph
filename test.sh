#!/bin/bash

PYTHON=python3

###############################################################################

set -e

CLEAN=0
VENV_DIR=.venv

while getopts ":ce:k:" OPTION; do
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
        \?)
            echo "Usage: $0 [-c] [-e VIRTUALENV]"
			exit 1
            ;;
    esac
done
shift $((OPTIND -1))

if [ ! -d $VENV_DIR ]; then
    $PYTHON -m venv $VENV_DIR
    $VENV_DIR/bin/pip install -U pip wheel
fi

rm -rf build/
if [ x$CLEAN = x1 ]; then
    rm -rf vendor/build vendor/install
fi

# pip install is called in verbose mode so we can see the compiler warnings
$VENV_DIR/bin/pip install -v .[plotting,test]
$VENV_DIR/bin/pytest tests ${PYTEST_ARGS}

