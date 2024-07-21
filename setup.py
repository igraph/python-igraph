#!usr/bin/env python

import os
import platform
import sys
import glob

###########################################################################

# Check Python's version info and exit early if it is too old
if sys.version_info < (3, 8):
    print("This module requires Python >= 3.8")
    sys.exit(0)

###########################################################################

from setuptools import find_packages, setup, Extension

try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    bdist_wheel = None


import sysconfig


# Check whether we are compiling for PyPy or wasm with emscripten. Headers will
# not be installed in these cases, or when the SKIP_HEADER_INSTALL envvar is
# set explicitly.
SKIP_HEADER_INSTALL = (
    platform.python_implementation() == "PyPy"
    or (sysconfig.get_config_var("HOST_GNU_TYPE") or "").endswith("emscripten")
    or "SKIP_HEADER_INSTALL" in os.environ
)

if bdist_wheel is not None:

    class bdist_wheel_abi3(bdist_wheel):
        def get_tag(self):
            python, abi, plat = super().get_tag()
            if python.startswith("cp"):
                # on CPython, our wheels are abi3 and compatible back to 3.9
                return "cp39", "abi3", plat

            return python, abi, plat

else:
    bdist_wheel_abi3 = None

# We are going to build an abi3 wheel if we are at least on CPython 3.9.
# This is because the C code contains conditionals for CPython 3.8 so we cannot
# use an abi3 wheel built with CPython 3.8 on CPython 3.9
should_build_abi3_wheel = (
    bdist_wheel_abi3
    and platform.python_implementation() == "CPython"
    and sys.version_info >= (3, 9)
)

###########################################################################

# Import version number from version.py so we only need to change it in
# one place when a new release is created
__version__: str = ""
exec(open("src/igraph/version.py").read())

# Define the extension
sources = glob.glob(os.path.join("src", "_igraph", "*.c"))
sources.append(os.path.join("src", "_igraph", "force_cpp_linker.cpp"))
macros = []
if should_build_abi3_wheel:
    macros.append(("Py_LIMITED_API", "0x03090000"))
igraph_extension = Extension(
    "igraph._igraph",
    libraries=["igraph"],
    include_dirs=['build-deps/install/include'],
    library_dirs=['build-deps/install/lib'],
    sources=sources,
    py_limited_api=should_build_abi3_wheel,
    define_macros=macros,
)

description = """Python interface to the igraph high performance graph
library, primarily aimed at complex network research and analysis.

Graph plotting functionality is provided by the Cairo library, so make
sure you install the Python bindings of Cairo if you want to generate
publication-quality graph plots. You can try either `pycairo
<http://cairographics.org/pycairo>`_ or `cairocffi <http://cairocffi.readthedocs.io>`_,
``cairocffi`` is recommended because there were bug reports affecting igraph
graph plots in Jupyter notebooks when using ``pycairo`` (but not with
``cairocffi``).
"""

headers = ["src/_igraph/igraphmodule_api.h"] if not SKIP_HEADER_INSTALL else []

cmdclass = {}

if should_build_abi3_wheel:
    cmdclass["bdist_wheel"] = bdist_wheel_abi3

options = {
    "name": "igraph",
    "version": __version__,
    "url": "https://igraph.org/python",
    "description": "High performance graph data structures and algorithms",
    "long_description": description,
    "license": "GNU General Public License (GPL)",
    "author": "Tamas Nepusz",
    "author_email": "ntamas@gmail.com",
    "project_urls": {
        "Bug Tracker": "https://github.com/igraph/python-igraph/issues",
        "Changelog": "https://github.com/igraph/python-igraph/blob/main/CHANGELOG.md",
        "CI": "https://github.com/igraph/python-igraph/actions",
        "Documentation": "https://igraph.readthedocs.io",
        "Source Code": "https://github.com/igraph/python-igraph",
    },
    "ext_modules": [igraph_extension],
    "package_dir": {
        # make sure to use the next line and not the more logical and restrictive
        # "igraph": "src/igraph" because that one breaks 'setup.py develop'.
        # See: https://github.com/igraph/python-igraph/issues/464
        "": "src"
    },
    "packages": find_packages(where="src"),
    "install_requires": ["texttable>=1.6.2"],
    "entry_points": {"console_scripts": ["igraph=igraph.app.shell:main"]},
    "extras_require": {
        # Dependencies needed for plotting with Cairo
        "cairo": ["cairocffi>=1.2.0"],
        # Dependencies needed for plotting with Matplotlib
        "matplotlib": [
            "matplotlib>=3.6.0; platform_python_implementation != 'PyPy'"
        ],
        # Dependencies needed for plotting with Plotly
        "plotly": ["plotly>=5.3.0"],
        # Compatibility alias to 'cairo' for python-igraph <= 0.9.6
        "plotting": ["cairocffi>=1.2.0"],
        # Dependencies needed for testing only
        "test": [
            "cairocffi>=1.2.0",
            "networkx>=2.5",
            "pytest>=7.0.1",
            "pytest-timeout>=2.1.0",
            "numpy>=1.19.0; platform_python_implementation != 'PyPy'",
            "pandas>=1.1.0; platform_python_implementation != 'PyPy'",
            "scipy>=1.5.0; platform_python_implementation != 'PyPy'",
            "matplotlib>=3.6.0; platform_python_implementation != 'PyPy'",
            "plotly>=5.3.0",
            "Pillow>=9; platform_python_implementation != 'PyPy'",
        ],
        # Dependencies needed for testing on musllinux; only those that are either
        # pure Python or have musllinux wheels as we don't want to compile wheels
        # in CI
        "test-musl": [
            "cairocffi>=1.2.0",
            "networkx>=2.5",
            "pytest>=7.0.1",
            "pytest-timeout>=2.1.0",
        ],
        # Dependencies needed for building the documentation
        "doc": [
            "Sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "sphinx-gallery>=0.14.0",
            "pydoctor>=23.4.0",
        ],
    },
    "python_requires": ">=3.8",
    "headers": headers,
    "platforms": "ALL",
    "keywords": [
        "graph",
        "network",
        "mathematics",
        "math",
        "graph theory",
        "discrete mathematics",
    ],
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    "cmdclass": cmdclass,
}

setup(**options)
