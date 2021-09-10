#!/bin/bash

PYTHON=python3

###############################################################################

set -e

CLEAN=0
VENV_DIR=.venv

while getopts ":ce:" OPTION; do
    case $OPTION in
        c)
            CLEAN=1
            ;;
        e)
			VENV_DIR=$OPTARG
            ;;
        \?)
            echo "Usage: $0 [-c]"
            ;;
    esac
    shift $((OPTIND -1))
done

if [ ! -d $VENV_DIR ]; then
    $PYTHON -m venv $VENV_DIR
    $VENV_DIR/bin/pip install -U pip wheel
fi

rm -rf build/
if [ x$CLEAN = x1 ]; then
    rm -rf vendor/build vendor/install
fi

$VENV_DIR/bin/python setup.py build
$VENV_DIR/bin/pip install --use-feature=in-tree-build .[plotting,test]
$VENV_DIR/bin/pytest tests

