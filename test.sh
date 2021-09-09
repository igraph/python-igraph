#!/bin/bash

VENV_DIR=.venv
PYTHON=python3

###############################################################################

set -e

if [ ! -d $VENV_DIR ]; then
	$PYTHON -m venv $VENV_DIR
    $VENV_DIR/bin/pip install -U pip wheel
fi

rm -rf build/
$VENV_DIR/bin/python setup.py build
$VENV_DIR/bin/pip install --use-feature=in-tree-build .[plotting,test]
$VENV_DIR/bin/pytest tests


