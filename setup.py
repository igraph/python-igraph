#!/usr/bin/env python

import os
import platform
import sys

###########################################################################

# Global version number. Keep the format of the next line intact.
VERSION = "0.7.1.post6"

# Check Python's version info and exit early if it is too old
if sys.version_info < (2, 7):
    print("This module requires Python >= 2.7")
    sys.exit(0)

# Check whether we are compiling for PyPy. Headers will not be installed
# for PyPy.
SKIP_HEADER_INSTALL = (platform.python_implementation() == "PyPy") or (
    "SKIP_HEADER_INSTALL" in os.environ
)

###########################################################################

from setuptools import setup, Extension

import distutils.ccompiler
import glob
import shutil
import subprocess
import sys

from select import select

###########################################################################

LIBIGRAPH_FALLBACK_INCLUDE_DIRS = ["/usr/include/igraph", "/usr/local/include/igraph"]
LIBIGRAPH_FALLBACK_LIBRARIES = ["igraph"]
LIBIGRAPH_FALLBACK_LIBRARY_DIRS = []

###########################################################################


def create_dir_unless_exists(*args):
    """Creates a directory unless it exists already."""
    path = os.path.join(*args)
    if not os.path.isdir(path):
        os.makedirs(path)


def ensure_dir_does_not_exist(*args):
    """Ensures that the given directory does not exist."""
    path = os.path.join(*args)
    if os.path.isdir(path):
        shutil.rmtree(path)


def exclude_from_list(items, items_to_exclude):
    """Excludes certain items from a list, keeping the original order of
    the remaining items."""
    itemset = set(items_to_exclude)
    return [item for item in items if item not in itemset]


def find_static_library(library_name, library_path):
    """Given the raw name of a library in `library_name`, tries to find a
    static library with this name in the given `library_path`. `library_path`
    is automatically extended with common library directories on Linux and Mac
    OS X."""

    variants = ["lib{0}.a", "{0}.a", "{0}.lib", "lib{0}.lib"]
    if is_unix_like():
        extra_libdirs = [
            "/usr/local/lib64",
            "/usr/local/lib",
            "/usr/lib64",
            "/usr/lib",
            "/lib64",
            "/lib",
        ]
    else:
        extra_libdirs = []

    for path in extra_libdirs:
        if path not in library_path and os.path.isdir(path):
            library_path.append(path)

    for path in library_path:
        for variant in variants:
            full_path = os.path.join(path, variant.format(library_name))
            if os.path.isfile(full_path):
                return full_path


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


def is_unix_like(platform=None):
    """Returns whether the given platform is a Unix-like platform with the usual
    Unix filesystem. When the parameter is omitted, it defaults to ``sys.platform``
    """
    platform = platform or sys.platform
    platform = platform.lower()
    return (
        platform.startswith("linux")
        or platform.startswith("darwin")
        or platform.startswith("cygwin")
    )


def preprocess_fallback_config():
    """Preprocesses the fallback include and library paths depending on the
    platform."""
    global LIBIGRAPH_FALLBACK_INCLUDE_DIRS
    global LIBIGRAPH_FALLBACK_LIBRARY_DIRS
    global LIBIGRAPH_FALLBACK_LIBRARIES

    if os.name == "nt" and distutils.ccompiler.get_default_compiler() == "msvc":
        # if this setup is run in the source checkout *and* the igraph msvc was build,
        # this code adds the right library and include dir
        all_msvc_dirs = glob.glob(os.path.join("..", "..", "igraph-*-msvc"))
        if len(all_msvc_dirs) > 0:
            if len(all_msvc_dirs) > 1:
                print(
                    "More than one MSVC build directory (..\\..\\igraph-*-msvc) found!"
                )
                print(
                    "It could happen that setup.py uses the wrong one! Please remove all but the right one!\n\n"
                )

            msvc_builddir = all_msvc_dirs[-1]
            if not os.path.exists(os.path.join(msvc_builddir, "Release")):
                print(
                    "There is no 'Release' dir in the MSVC build directory\n(%s)"
                    % msvc_builddir
                )
                print("Please build the MSVC build first!\n")
            else:
                print("Using MSVC build dir as a fallback: %s\n\n" % msvc_builddir)
                LIBIGRAPH_FALLBACK_INCLUDE_DIRS = [
                    os.path.join(msvc_builddir, "include")
                ]
                LIBIGRAPH_FALLBACK_LIBRARY_DIRS = [
                    os.path.join(msvc_builddir, "Release")
                ]


def version_variants(version):
    """Given an igraph version number, returns a list of possible version
    number variants to try when looking for a suitable nightly build of the
    C core to download from igraph.org."""

    result = [version]

    # Strip any release tags
    version, _, _ = version.partition(".post")
    result.append(version)

    # Add trailing ".0" as needed to ensure that we have at least
    # major.minor.patch
    parts = version.split(".")
    while len(parts) < 3:
        parts.append("0")
        result.append(".".join(parts))

    return result


###########################################################################


class IgraphCCoreBuilder(object):
    """Class responsible for downloading and building the C core of igraph
    if it is not installed yet."""

    def compile_in(self, folder):
        """Compiles igraph from its source code in the given folder."""
        cwd = os.getcwd()
        try:
            os.chdir(folder)

            # Run the bootstrap script if we have downloaded a tarball from
            # Github
            if os.path.isfile("bootstrap.sh") and not os.path.isfile("configure"):
                print("Bootstrapping igraph...")
                retcode = subprocess.call("sh bootstrap.sh", shell=True)
                if retcode:
                    return False

            # Patch ltmain.sh so it does not freak out on OS X when the build
            # directory contains spaces
            with open("ltmain.sh") as infp:
                with open("ltmain.sh.new", "w") as outfp:
                    for line in infp:
                        if line.endswith("cd $darwin_orig_dir\n"):
                            line = line.replace(
                                "cd $darwin_orig_dir\n", 'cd "$darwin_orig_dir"\n'
                            )
                        outfp.write(line)
            os.rename("ltmain.sh.new", "ltmain.sh")

            print("Configuring igraph...")
            retcode = subprocess.call(
                ["./configure", "--disable-tls", "--disable-gmp"],
                env=self.enhanced_env(CFLAGS="-fPIC", CXXFLAGS="-fPIC"),
            )
            if retcode:
                return False

            print("Building igraph...")
            retcode = subprocess.call("make", shell=True)
            if retcode:
                return False

            libraries = []
            for line in open("igraph.pc"):
                if line.startswith("Libs: ") or line.startswith("Libs.private: "):
                    words = line.strip().split()
                    libraries.extend(
                        word[2:] for word in words if word.startswith("-l")
                    )

            if not libraries:
                # Educated guess
                libraries = ["igraph"]

            return libraries

        finally:
            os.chdir(cwd)

    def copy_build_artifacts_from(self, source, to, libraries):
        create_dir_unless_exists(to)
        ensure_dir_does_not_exist(to, "include")
        ensure_dir_does_not_exist(to, "lib")
        shutil.copytree(os.path.join(source, "include"), os.path.join(to, "include"))
        shutil.copytree(os.path.join(source, "src", ".libs"), os.path.join(to, "lib"))
        with open(os.path.join(to, "build.cfg"), "w") as f:
            f.write(repr(libraries))

        return True

    @staticmethod
    def enhanced_env(**kwargs):
        env = os.environ.copy()
        for k, v in kwargs.items():
            prev = os.environ.get(k)
            env[k] = "{0} {1}".format(prev, v) if prev else v
        return env


class BuildConfiguration(object):
    def __init__(self):
        self.include_dirs = []
        self.library_dirs = []
        self.runtime_library_dirs = []
        self.libraries = []
        self.extra_compile_args = []
        self.extra_link_args = []
        self.extra_objects = []
        self.static_extension = False
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
        ``build_ext`` command in ``setuptools`` and that will compile the C core
        of igraph before compiling the Python extension.
        """
        from setuptools.command.build_ext import build_ext
        from distutils.sysconfig import get_python_inc

        buildcfg = self

        class custom_build_ext(build_ext):
            def run(self):
                # Bail out if we don't have the Python include files
                include_dir = get_python_inc()
                if not os.path.isfile(os.path.join(include_dir, "Python.h")):
                    print("You will need the Python headers to compile this extension.")
                    sys.exit(1)

                # Check whether we have already compiled igraph in a previous run.
                # If so, it should be found in vendor/build/igraph/include and
                # vendor/build/igraph/lib
                if os.path.exists(os.path.join("vendor", "build", "igraph")):
                    buildcfg.use_vendored_igraph()
                    detected = True
                else:
                    detected = False

                # If igraph is provided as a git submodule, use that
                if not detected:
                    if os.path.isfile(
                        os.path.join("vendor", "source", "igraph", "configure.ac")
                    ):
                        detected = buildcfg.compile_igraph_from_vendor_source()
                        if detected:
                            buildcfg.use_vendored_igraph()
                        else:
                            sys.exit(1)

                # Try detecting with pkg-config if we haven't found the submodule
                if not detected:
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
                    if buildcfg.static_extension == "only_igraph":
                        buildcfg.replace_static_libraries(only=["igraph"])
                    else:
                        buildcfg.replace_static_libraries(exclusions=["m"])

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

    def compile_igraph_from_vendor_source(self):
        """Compiles igraph from the vendored source code inside `vendor/igraph/source`.
        This folder typically comes from a git submodule.
        """
        path = os.path.join("vendor", "source", "igraph")
        print("We are going to compile the C core of igraph from %s" % path)
        print("")

        igraph_builder = IgraphCCoreBuilder()
        libraries = igraph_builder.compile_in(path)
        if not libraries or not igraph_builder.copy_build_artifacts_from(
            path, to=os.path.join("vendor", "build", "igraph"), libraries=libraries
        ):
            print("Could not compile the C core of igraph.")
            print("")
            return False
        else:
            return True

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
        if self.static_extension == "only_igraph":
            build_type = "dynamic extension with vendored igraph source"
        elif self.static_extension:
            build_type = "static extension"
        else:
            build_type = "dynamic extension"
        print("Build type: %s" % build_type)
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
            if option == "--static":
                opts_to_remove.append(idx)
                self.static_extension = True
            elif option == "--no-pkg-config":
                opts_to_remove.append(idx)
                self.use_pkgconfig = False
            elif option == "--no-wait":
                opts_to_remove.append(idx)
                self.wait = False

        for idx in reversed(opts_to_remove):
            sys.argv[idx : (idx + 1)] = []

    def replace_static_libraries(self, only=None, exclusions=None):
        """Replaces references to libraries with full paths to their static
        versions if the static version is to be found on the library path."""
        if "stdc++" not in self.libraries:
            self.libraries.append("stdc++")

        if exclusions is None:
            exclusions = []

        for library_name in set(self.libraries) - set(exclusions):
            if only is not None and library_name not in only:
                continue

            static_lib = find_static_library(library_name, self.library_dirs)
            if static_lib:
                self.libraries.remove(library_name)
                self.extra_objects.append(static_lib)

    def use_vendored_igraph(self):
        """Assumes that igraph is built already in ``vendor/build/igraph`` and sets up
        the include and library paths and the library names accordingly."""
        buildcfg.include_dirs = [os.path.join("vendor", "build", "igraph", "include")]
        buildcfg.library_dirs = [os.path.join("vendor", "build", "igraph", "lib")]
        if not buildcfg.static_extension:
            buildcfg.static_extension = "only_igraph"

        buildcfg_file = os.path.join("vendor", "build", "igraph", "build.cfg")
        if os.path.exists(buildcfg_file):
            buildcfg.libraries = eval(open(buildcfg_file).read())

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

# Define the extension
sources = glob.glob(os.path.join("src", "*.c"))
igraph_extension = Extension("igraph._igraph", sources)

description = """Python interface to the igraph high performance graph
library, primarily aimed at complex network research and analysis.

Graph plotting functionality is provided by the Cairo library, so make
sure you install the Python bindings of Cairo if you want to generate
publication-quality graph plots. You can try either `pycairo
<http://cairographics.org/pycairo>`_ or `cairocffi <http://cairocffi.readthedocs.io>`_,
``cairocffi`` is recommended, in particular if you are on Python 3.x because
there were bug reports affecting igraph graph plots in Jupyter notebooks
when using ``pycairo`` (but not with ``cairocffi``).

Unofficial installers for 64-bit Windows machines and/or different Python
versions can also be found `here <http://www.lfd.uci.edu/~gohlke/pythonlibs>`_.
Many thanks to the maintainers of this page!
"""

headers = ["src/igraphmodule_api.h"] if not SKIP_HEADER_INSTALL else []

options = dict(
    name="python-igraph",
    version=VERSION,
    url="http://pypi.python.org/pypi/python-igraph",
    description="High performance graph data structures and algorithms",
    long_description=description,
    license="GNU General Public License (GPL)",
    author="Tamas Nepusz",
    author_email="ntamas@gmail.com",
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

if sys.version_info > (3, 0):
    options["use_2to3"] = True

setup(**options)
