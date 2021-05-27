"""Utility functions for unit testing."""

import os
import platform
import tempfile

from contextlib import contextmanager
from textwrap import dedent

__all__ = ("temporary_file", )


@contextmanager
def temporary_file(content=None, mode=None, binary=False):
    tmpf, tmpfname = tempfile.mkstemp()
    os.close(tmpf)

    if mode is None:
        if content is None:
            mode = "rb"
        else:
            mode = "wb"

    tmpf = open(tmpfname, mode)
    if content is not None:
        if hasattr(content, "encode") and not binary:
            tmpf.write(dedent(content).encode("utf8"))
        else:
            tmpf.write(content)

    tmpf.close()
    yield tmpfname
    os.unlink(tmpfname)


is_pypy = platform.python_implementation() == "PyPy"
