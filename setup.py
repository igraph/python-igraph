#!/usr/bin/env python

import os
import platform
import sys

###########################################################################

# Global version number. Keep the format of the next line intact.
VERSION = "0.7.1.post6"

# Check Python's version info and exit early if it is too old
if sys.version_info < (2, 5):
    print("This module requires Python >= 2.5")
    sys.exit(0)

# Check whether we are running inside tox -- if so, we will use a non-logging
# URL to download the C core of igraph to avoid inflating download counts
TESTING_IN_TOX = "TESTING_IN_TOX" in os.environ

# Check whether we are running in a CI environment like Travis -- if so,
# we will download the master tarball of igraph when needed
TESTING_IN_CI = "CONTINUOUS_INTEGRATION" in os.environ

# Check whether we are compiling for PyPy. Headers will not be installed
# for PyPy.
IS_PYPY = platform.python_implementation() == "PyPy"

###########################################################################
# Here be ugly workarounds. These must be run before setuptools
# is imported.


class Workaround(object):
    """Base class for platform-specific workarounds and hacks that are
    needed to get the Python interface compile with as little user
    intervention as possible."""

    def required(self):
        """Returns ``True`` if the workaround is required on the platform
        of the user and ``False`` otherwise."""
        raise NotImplementedError

    def hack(self):
        """Installs the workaround. This method will get called if and only
        if the ``required()`` method returns ``True``.
        """
        pass

    def update_buildcfg(self, cfg):
        """Allows the workaround to update the build configuration of the
        igraph extension. This method will get called if and only if the
        ``required()`` method returns ``True``.
        """
        pass

    def _extend_compiler_customization(self, func):
        """Helper function that extends ``distutils.sysconfig.customize_compiler``
        and ``setuptools.command.build_ext.customize_compiler`` with new,
        user-defined code at the end."""
        from distutils import sysconfig

        old_func = sysconfig.customize_compiler

        def replaced(*args, **kwds):
            old_func(*args, **kwds)
            return func(*args, **kwds)

        self._replace_compiler_customization_distutils(replaced)
        self._replace_compiler_customization_setuptools(replaced)

    def _replace_compiler_customization_distutils(self, new_func):
        from distutils import ccompiler, sysconfig

        sysconfig.customize_compiler = new_func
        ccompiler.customize_compiler = new_func

    def _replace_compiler_customization_setuptools(self, new_func):
        if "setuptools.command.build_ext" in sys.modules:
            sys.modules["setuptools.command.build_ext"].customize_compiler = new_func


class OSXClangAndSystemPythonWorkaround(Workaround):
    """Removes ``-mno-fused-madd`` from the arguments used to compile
    Python extensions if the user is running OS X."""

    @staticmethod
    def remove_compiler_args(compiler):
        while "-mno-fused-madd" in compiler.compiler:
            compiler.compiler.remove("-mno-fused-madd")
        while "-mno-fused-madd" in compiler.compiler_so:
            compiler.compiler_so.remove("-mno-fused-madd")
        while "-mno-fused-madd" in compiler.linker_so:
            compiler.linker_so.remove("-mno-fused-madd")

    def required(self):
        return sys.platform.startswith("darwin")

    def hack(self):
        self._extend_compiler_customization(self.remove_compiler_args)


class OSXAnacondaPythonIconvWorkaround(Workaround):
    """Anaconda Python contains a file named libxml2.la which refers to
    /usr/lib/libiconv.la -- but such a file does not exist in OS X. This
    hack ensures that we link to libxml2 from OS X itself and not from
    Anaconda Python (after all, this is what would have happened if the
    C core of igraph was compiled independently)."""

    def required(self):
        from distutils.spawn import find_executable

        if not sys.platform.startswith("darwin"):
            return False
        if "Anaconda" not in sys.version:
            return False
        self.xml2_config_path = find_executable("xml2-config")
        if not self.xml2_config_path:
            return False
        xml2_config_path_abs = os.path.abspath(self.xml2_config_path)
        return xml2_config_path_abs.startswith(os.path.abspath(sys.prefix))

    def hack(self):
        path = os.environ["PATH"].split(os.pathsep)
        dir_to_remove = os.path.dirname(self.xml2_config_path)
        if dir_to_remove in path:
            path.remove(dir_to_remove)
            os.environ["PATH"] = os.pathsep.join(path)

    def update_buildcfg(self, cfg):
        anaconda_libdir = os.path.join(sys.prefix, "lib")
        cfg.extra_link_args.append("-Wl,-rpath,%s" % anaconda_libdir)
        cfg.post_build_hooks.append(self.fix_install_name)

    def fix_install_name(self, cfg):
        """Fixes the install name of the libxml2 library in _igraph.so
        to ensure that it loads libxml2 from Anaconda Python."""
        for outputfile in cfg.get_outputs():
            lines, retcode = get_output(["otool", "-L", outputfile])
            if retcode:
                raise OSError(
                    "otool -L %s failed with error code: %s" % (outputfile, retcode)
                )

            for line in lines.split("\n"):
                if "libxml2" in line:
                    libname = line.strip().split(" ")[0]
                    subprocess.call(
                        [
                            "install_name_tool",
                            "-change",
                            libname,
                            "@rpath/" + os.path.basename(libname),
                            outputfile,
                        ]
                    )


class ContinuousIntegrationSetup(Workaround):
    """Prepares the build configuration for a CI environment like Travis."""

    def required(self):
        return TESTING_IN_CI

    def update_buildcfg(self, cfg):
        cfg.c_core_url = "https://github.com/igraph/igraph/archive/master.tar.gz"


class WorkaroundSet(object):
    def __init__(self, workaround_classes):
        self.each = [cls() for cls in workaround_classes]
        self.executed = []

    def execute(self):
        for workaround in self.each:
            if workaround.required():
                workaround.hack()
                self.executed.append(workaround)


workarounds = WorkaroundSet(
    [
        OSXClangAndSystemPythonWorkaround,
        OSXAnacondaPythonIconvWorkaround,
        ContinuousIntegrationSetup,
    ]
)
workarounds.execute()

###########################################################################

try:
    from setuptools import setup

    build_py = None
except ImportError:
    from distutils.core import setup

    try:
        from distutils.command.build_py import build_py_2to3 as build_py
    except ImportError:
        from distutils.command.build_py import build_py

import atexit
import distutils.ccompiler
import glob
import shutil
import subprocess
import sys
import tarfile
import tempfile

from select import select
from shutil import copyfileobj

try:
    from urllib2 import Request, urlopen, URLError
except ImportError:
    # Maybe Python 3?
    from urllib.request import Request, urlopen
    from urllib.error import URLError

from distutils.core import Extension
from distutils.util import get_platform

###########################################################################

LIBIGRAPH_FALLBACK_INCLUDE_DIRS = ["/usr/include/igraph", "/usr/local/include/igraph"]
LIBIGRAPH_FALLBACK_LIBRARIES = ["igraph"]
LIBIGRAPH_FALLBACK_LIBRARY_DIRS = []

###########################################################################

def exclude_from_list(items, items_to_exclude):
    """Excludes certain items from a list, keeping the original order of
    the remaining items."""
    itemset = set(items_to_exclude)
    return [item for item in items if item not in itemset]

def first(iterable):
    """Returns the first element from the given iterable."""
    for item in iterable:
        return item
    raise ValueError("iterable is empty")

def get_output(args, encoding="utf-8"):
    """Returns the output of a command returning a single line of output."""
    PIPE = subprocess.PIPE
    try:
        p = subprocess.Popen(args, shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        returncode = p.returncode
    except OSError:
        stdout, stderr = None, None
        returncode = 77
    if encoding and type(stdout).__name__ == "bytes":
        stdout = str(stdout, encoding=encoding)
    if encoding and type(stderr).__name__ == "bytes":
        stderr = str(stderr, encoding=encoding)
    return stdout, returncode

def get_output_single_line(args, encoding="utf-8"):
    """Returns the output of a command returning a single line of output,
    stripped from any trailing newlines."""
    stdout, returncode = get_output(args, encoding=encoding)
    if stdout is not None:
        line, _, _ = stdout.partition("\n")
    else:
        line = None
    return line, returncode

class BuildConfiguration(object):
    def __init__(self):
        global VERSION
        self.include_dirs = []
        self.library_dirs = []
        self.runtime_library_dirs = []
        self.libraries = []
        self.extra_compile_args = []
        self.extra_link_args = []
        self.extra_objects = []
        self.static_extension = False
        self.external_igraph = False
        self.use_pkgconfig = True
        self._has_pkgconfig = None
        self.excluded_include_dirs = []
        self.excluded_library_dirs = []
        self.pre_build_hooks = []
        self.post_build_hooks = []
        self.wait = True

    @property
    def has_pkgconfig(self):
        """Returns whether ``pkg-config`` is available on the current system
        and it knows about igraph or not."""
        if self._has_pkgconfig is None:
            if self.use_pkgconfig:
                line, exit_code = get_output_single_line(["pkg-config", "igraph"])
                self._has_pkgconfig = exit_code == 0
            else:
                self._has_pkgconfig = False
        return self._has_pkgconfig

    @property
    def build_ext(self):
        """Returns a class that can be used as a replacement for the
        ``build_ext`` command in ``distutils`` and that will download and
        compile the C core of igraph if needed."""
        try:
            from setuptools.command.build_ext import build_ext
        except ImportError:
            from distutils.command.build_ext import build_ext
        from distutils.sysconfig import get_python_inc

        buildcfg = self

        class custom_build_ext(build_ext):
            def run(self):
                # Bail out if we don't have the Python include files
                include_dir = get_python_inc()
                if not os.path.isfile(os.path.join(include_dir, "Python.h")):
                    print("You will need the Python headers to compile this extension.")
                    sys.exit(1)

                if buildcfg.external_igraph:
                    buildcfg.libraries = ['igraph']
                    if buildcfg.use_pkgconfig:
                        detected = buildcfg.detect_from_pkgconfig()
                    else:
                        detected = False

                    # Fall back to an educated guess if everything else failed
                    if not detected:
                        buildcfg.use_educated_guess()

                    # Replaces library names with full paths to static libraries
                    # where possible. libm.a is excluded because it caused problems
                    # on Sabayon Linux where libm.a is probably not compiled with
                    # -fPIC
                    if buildcfg.static_extension:
                        buildcfg.replace_static_libraries(exclusions=["m"])                    
                else:
                    # Check whether source code from C core is available
                    source_dir = os.path.join("src", "core")
                    if not os.path.exists(source_dir):
                        print("C core files are missing.")
                        sys.exit(1)                                
                    # Specify include dirs and library dirs for using internal compilation
                    buildcfg.libraries = ['xml2', 'gmp', 'z', 'm']
                    buildcfg.library_dirs = ['/usr/lib/x86_64-linux-gnu']
                    buildcfg.include_dirs = ['/usr/include/libxml2',
                                            os.path.join(source_dir),
                                            os.path.join(source_dir, 'include'),
                                            os.path.join(source_dir, 'src'),
                                            os.path.join(source_dir, 'src', 'AMD', 'Include'),
                                            os.path.join(source_dir, 'src', 'bliss'),
                                            os.path.join(source_dir, 'src', 'cliquer'),
                                            os.path.join(source_dir, 'src', 'cs'),
                                            os.path.join(source_dir, 'src', 'COLAMD', 'Include'),
                                            os.path.join(source_dir, 'src', 'CHOLMOD', 'Include'),
                                            os.path.join(source_dir, 'src', 'f2c'),
                                            os.path.join(source_dir, 'src', 'lapack'),
                                            os.path.join(source_dir, 'src', 'plfit'),
                                            os.path.join(source_dir, 'src', 'prpack'),
                                            os.path.join(source_dir, 'src', 'SuiteSparse_config'),
                                            os.path.join(source_dir, 'optional', 'glpk')
                                            ]
                    buildcfg.extra_compile_args = ['-DNPARTITION',
                                                '-DNTIMER',
                                                '-DNCAMD',
                                                '-DPRPACK_IGRAPH_SUPPORT']

                # Prints basic build information
                buildcfg.print_build_info()

                ext = first(
                    extension
                    for extension in self.extensions
                    if extension.name == "igraph._igraph"
                )
                buildcfg.configure(ext)

                # Run any pre-build hooks
                for hook in buildcfg.pre_build_hooks:
                    hook(self)

                # Run the original build_ext command
                build_ext.run(self)

                # Run any post-build hooks
                for hook in buildcfg.post_build_hooks:
                    hook(self)

        return custom_build_ext

    def configure(self, ext):
        """Configures the given Extension object using this build configuration."""
        ext.include_dirs = exclude_from_list(
            self.include_dirs, self.excluded_include_dirs
        )
        ext.library_dirs = exclude_from_list(
            self.library_dirs, self.excluded_library_dirs
        )
        ext.runtime_library_dirs = self.runtime_library_dirs
        ext.libraries = self.libraries
        ext.extra_compile_args = self.extra_compile_args
        ext.extra_link_args = self.extra_link_args
        ext.extra_objects = self.extra_objects
    
    def prepare_sources(self):

        # Define the extension
        self.sources = glob.glob(os.path.join("src", "*.c"))

        if not self.external_igraph:
            # Check whether source code from C core is available
            source_dir = os.path.join("src", "core")
            if not os.path.exists(source_dir):
                print("C core files are missing.")
                sys.exit(1)

            # Add igraph source files
            match_ext = ['c', 'cpp', 'cc']
            for root, dirnames, filenames in os.walk(os.path.join(source_dir, 'src')):
                for filename in filenames:
                    ext = filename.split('.')[-1]
                    if ext in match_ext and \
                    not filename.startswith('t_cholmod') and \
                    not filename == 'arithchk.c':
                        self.sources.append(os.path.join(root, filename))

            # Add internal glpk
            for root, dirnames, filenames in os.walk(os.path.join(source_dir, 'optional')):
                for filename in filenames:
                    ext = filename.split('.')[-1]
                    if ext in match_ext and not filename.startswith('t_cholmod'):
                        self.sources.append(os.path.join(root, filename))        

    def detect_from_pkgconfig(self):
        """Detects the igraph include directory, library directory and the
        list of libraries to link to using ``pkg-config``."""
        if not buildcfg.has_pkgconfig:
            print("Cannot find the C core of igraph on this system using pkg-config.")
            return False

        cmd = ["pkg-config", "igraph", "--cflags", "--libs"]
        if self.static_extension:
            cmd += ["--static"]
        line, exit_code = get_output_single_line(cmd)
        if exit_code > 0 or len(line) == 0:
            return False

        opts = line.strip().split()
        self.libraries = [opt[2:] for opt in opts if opt.startswith("-l")]
        self.library_dirs = [opt[2:] for opt in opts if opt.startswith("-L")]
        self.include_dirs = [opt[2:] for opt in opts if opt.startswith("-I")]
        return True

    def print_build_info(self):
        """Prints the include and library path being used for debugging purposes."""
        if self.static_extension:
            build_type = "static extension"
        else:
            build_type = "dynamic extension"
        print("Build type: %s" % build_type)
        print("Building with " + ("external" if self.external_igraph else "internal") + " C core igraph")
        print("Include path: %s" % " ".join(self.include_dirs))
        if self.excluded_include_dirs:
            print("  - excluding: %s" % " ".join(self.excluded_include_dirs))
        print("Library path: %s" % " ".join(self.library_dirs))
        if self.excluded_library_dirs:
            print("  - excluding: %s" % " ".join(self.excluded_library_dirs))
        print("Runtime library path: %s" % " ".join(self.runtime_library_dirs))
        print("Linked dynamic libraries: %s" % " ".join(self.libraries))
        print("Linked static libraries: %s" % " ".join(self.extra_objects))
        print("Extra compiler options: %s" % " ".join(self.extra_compile_args))
        print("Extra linker options: %s" % " ".join(self.extra_link_args))

    def process_args_from_command_line(self):
        """Preprocesses the command line options before they are passed to
        setup.py and sets up the build configuration."""
        # Yes, this is ugly, but we don't want to interfere with setup.py's own
        # option handling
        opts_to_remove = []
        for idx, option in enumerate(sys.argv):
            if not option.startswith("--"):
                continue
            if option == "--with-external-igraph":
                opts_to_remove.append(idx)
                self.external_igraph = True
            elif option == "--static":
                opts_to_remove.append(idx)
                self.static_extension = True

        for idx in reversed(opts_to_remove):
            sys.argv[idx : (idx + 1)] = []

    def use_educated_guess(self):
        """Tries to guess the proper library names, include and library paths
        if everything else failed."""

        preprocess_fallback_config()

        global LIBIGRAPH_FALLBACK_LIBRARIES
        global LIBIGRAPH_FALLBACK_INCLUDE_DIRS
        global LIBIGRAPH_FALLBACK_LIBRARY_DIRS

        print("WARNING: we were not able to detect where igraph is installed on")
        print("your machine (if it is installed at all). We will use the fallback")
        print("library and include paths hardcoded in setup.py and hope that the")
        print("C core of igraph is installed there.")
        print("")
        print("If the compilation fails and you are sure that igraph is installed")
        print("on your machine, adjust the following two variables in setup.py")
        print("accordingly and try again:")
        print("")
        print("- LIBIGRAPH_FALLBACK_INCLUDE_DIRS")
        print("- LIBIGRAPH_FALLBACK_LIBRARY_DIRS")
        print("")

        seconds_remaining = 10 if self.wait else 0
        while seconds_remaining > 0:
            if seconds_remaining > 1:
                plural = "s"
            else:
                plural = ""

            sys.stdout.write(
                "\rContinuing in %2d second%s; press Enter to continue "
                "immediately. " % (seconds_remaining, plural)
            )
            sys.stdout.flush()

            rlist, _, _ = select([sys.stdin], [], [], 1)
            if rlist:
                sys.stdin.readline()
                break

            seconds_remaining -= 1
        sys.stdout.write("\r" + " " * 65 + "\r")

        self.libraries = LIBIGRAPH_FALLBACK_LIBRARIES[:]
        if self.static_extension:
            self.libraries.extend(["xml2", "z", "m", "stdc++"])
        self.include_dirs = LIBIGRAPH_FALLBACK_INCLUDE_DIRS[:]
        self.library_dirs = LIBIGRAPH_FALLBACK_LIBRARY_DIRS[:]
###########################################################################

# Process command line options
buildcfg = BuildConfiguration()
buildcfg.process_args_from_command_line()
for workaround in workarounds.executed:
    workaround.update_buildcfg(buildcfg)

buildcfg.prepare_sources()

igraph_extension = Extension("igraph._igraph", buildcfg.sources)
# library_dirs=library_dirs,
# libraries=libraries,
# include_dirs=include_dirs,
# extra_objects=extra_objects,
# extra_link_args=extra_link_args

description = """Python interface to the igraph high performance graph
library, primarily aimed at complex network research and analysis.

Graph plotting functionality is provided by the Cairo library, so make
sure you install the Python bindings of Cairo if you want to generate
publication-quality graph plots. You can try either `pycairo
<http://cairographics.org/pycairo>`_ or `cairocffi <http://cairocffi.readthedocs.io>`_,
``cairocffi`` is recommended, in particular if you are on Python 3.x because
there were bug reports affecting igraph graph plots in Jupyter notebooks
when using ``pycairo`` (but not with ``cairocffi``).

From release 0.5, the C core of the igraph library is **not** included
in the Python distribution - you must compile and install the C core
separately. Windows installers already contain a compiled igraph DLL,
so they should work out of the box. Linux users should refer to the
`igraph homepage <http://igraph.org>`_ for
compilation instructions (but check your distribution first, maybe
there are pre-compiled packages available). OS X users may
benefit from the disk images in the Python Package Index.

Unofficial installers for 64-bit Windows machines and/or different Python
versions can also be found `here <http://www.lfd.uci.edu/~gohlke/pythonlibs>`_.
Many thanks to the maintainers of this page!
"""

headers = ["src/igraphmodule_api.h"] if not IS_PYPY else []

options = dict(
    name="python-igraph",
    version=VERSION,
    url="http://pypi.python.org/pypi/python-igraph",
    description="High performance graph data structures and algorithms",
    long_description=description,
    license="GNU General Public License (GPL)",
    author="Tamas Nepusz",
    author_email="tamas@cs.rhul.ac.uk",
    ext_modules=[igraph_extension],
    package_dir={"igraph": "igraph"},
    packages=[
        "igraph",
        "igraph.test",
        "igraph.app",
        "igraph.drawing",
        "igraph.remote",
        "igraph.vendor",
    ],
    scripts=["scripts/igraph"],
    test_suite="igraph.test.suite",
    headers=headers,
    platforms="ALL",
    keywords=[
        "graph",
        "network",
        "mathematics",
        "math",
        "graph theory",
        "discrete mathematics",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    cmdclass={"build_ext": buildcfg.build_ext},
)

if "macosx" in get_platform() and "bdist_mpkg" in sys.argv:
    # OS X specific stuff to build the .mpkg installer
    options["data_files"] = [
        (
            "/usr/local/lib",
            [os.path.join("..", "igraph", "fatbuild", "libigraph.0.dylib")],
        )
    ]

if sys.version_info > (3, 0):
    if build_py is None:
        options["use_2to3"] = True
    else:
        options["cmdclass"]["build_py"] = build_py

setup(**options)
