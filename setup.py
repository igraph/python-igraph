#!usr/bin/env python

import os
import platform
import sys

###########################################################################

# Check Python's version info and exit early if it is too old
if sys.version_info < (3, 6):
    print("This module requires Python >= 3.6")
    sys.exit(0)

###########################################################################

from setuptools import setup, Command, Extension

import glob
import shlex
import shutil
import subprocess
import sys
import sysconfig

from contextlib import contextmanager
from pathlib import Path
from select import select
from shutil import which
from time import sleep
from typing import List, Iterable, Iterator, Optional, Tuple, TypeVar, Union

###########################################################################

LIBIGRAPH_FALLBACK_INCLUDE_DIRS = ["/usr/include/igraph", "/usr/local/include/igraph"]
LIBIGRAPH_FALLBACK_LIBRARIES = ["igraph"]
LIBIGRAPH_FALLBACK_LIBRARY_DIRS = []

# Check whether we are compiling for PyPy. Headers will not be installed
# for PyPy.
SKIP_HEADER_INSTALL = (platform.python_implementation() == "PyPy") or (
    "SKIP_HEADER_INSTALL" in os.environ
)

###########################################################################


T = TypeVar("T")


def building_on_windows_msvc() -> bool:
    """Returns True when using the non-MinGW CPython interpreter on Windows"""
    return platform.system() == "Windows" and sysconfig.get_platform() != "mingw"


def exclude_from_list(items: Iterable[T], items_to_exclude: Iterable[T]) -> List[T]:
    """Excludes certain items from a list, keeping the original order of
    the remaining items."""
    itemset = set(items_to_exclude)
    return [item for item in items if item not in itemset]


def find_static_library(library_name: str, library_path: List[str]) -> Optional[str]:
    """Given the raw name of a library in `library_name`, tries to find a
    static library with this name in the given `library_path`. `library_path`
    is automatically extended with common library directories on Linux and Mac
    OS X."""

    variants = ["lib{0}.a", "{0}.a", "{0}.lib", "lib{0}.lib"]
    if is_unix_like():
        extra_libdirs = [
            "/usr/local/lib64",
            "/usr/local/lib",
            "/usr/lib/x86_64-linux-gnu",
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


def first(iterable: Iterable[T]) -> T:
    """Returns the first element from the given iterable."""
    for item in iterable:
        return item
    raise ValueError("iterable is empty")


def get_output(args, encoding: str = "utf-8") -> Tuple[str, int]:
    """Returns the output of a command returning a single line of output, and
    the exit code of the command.
    """
    PIPE = subprocess.PIPE
    try:
        p = subprocess.Popen(args, shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        returncode = p.returncode
    except OSError:
        stdout, stderr = None, None
        returncode = 77
    if isinstance(stdout, bytes):
        stdout = str(stdout, encoding=encoding)
    if isinstance(stderr, bytes):
        stderr = str(stderr, encoding=encoding)
    return (stdout or ""), returncode


def get_output_single_line(args, encoding: str = "utf-8") -> Tuple[str, int]:
    """Returns the first line of the output of a command, stripped from any
    trailing newlines, and the exit code of the command.
    """
    stdout, returncode = get_output(args, encoding=encoding)
    line, _, _ = stdout.partition("\n")
    return line, returncode


def is_unix_like(platform: str = sys.platform) -> bool:
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


def wait_for_keypress(seconds: float) -> None:
    """Wait for a keypress or until the given number of seconds have passed,
    whichever happens first.
    """
    while seconds > 0:
        if seconds > 1:
            plural = "s"
        else:
            plural = ""

        sys.stdout.write(
            "\rContinuing in %2d second%s; press Enter to continue "
            "immediately. " % (seconds, plural)
        )
        sys.stdout.flush()

        if platform.system() == "Windows":
            from msvcrt import kbhit  # type: ignore

            for _ in range(10):
                if kbhit():
                    seconds = 0
                    break
                sleep(0.1)
        else:
            rlist, _, _ = select([sys.stdin], [], [], 1)
            if rlist:
                sys.stdin.readline()
                seconds = 0
                break

        seconds -= 1

    sys.stdout.write("\r" + " " * 65 + "\r")


@contextmanager
def working_directory(dir: Union[str, Path]) -> Iterator[None]:
    cwd = os.getcwd()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(cwd)


###########################################################################


class IgraphCCoreCMakeBuilder:
    """Class responsible for downloading and building the C core of igraph
    if it is not installed yet, assuming that the C core uses CMake as the
    build tool. This is the case from igraph 0.9.
    """

    def compile_in(
        self, source_folder: Path, build_folder: Path, install_folder: Path
    ) -> Union[bool, List[str]]:
        """Compiles igraph from its source code in the given folder.

        Parameters:
            source_folder: absolute path to the folder that contains igraph's
                source files
            build_folder: absolute path to the folder where the build should be
                executed
            install_folder: absolute path to the folder where the built library
                should be installed

        Returns:
            False if the build failed or the list of libraries to link to when
            linking the Python interface to igraph
        """
        with working_directory(build_folder):
            return self._compile_in(source_folder, build_folder, install_folder)

    def _compile_in(
        self, source_folder: Path, build_folder: Path, install_folder: Path
    ) -> Union[bool, List[str]]:
        cmake = which("cmake")
        if not cmake:
            print(
                "igraph uses CMake as the build system. You need to install CMake "
                "before compiling igraph."
            )
            return False

        build_to_source_folder = os.path.relpath(source_folder, build_folder)

        print("Configuring build...")
        args = [cmake]

        # Build the Python interface with vendored libraries
        for deps in "ARPACK BLAS CXSPARSE GLPK GMP LAPACK".split():
            args.append("-DIGRAPH_USE_INTERNAL_" + deps + "=ON")

        # -fPIC is needed on Linux so we can link to a static igraph lib from a
        # Python shared library
        args.append("-DCMAKE_POSITION_INDEPENDENT_CODE=ON")

        # Add any extra CMake args from environment variables
        if "IGRAPH_CMAKE_EXTRA_ARGS" in os.environ:
            args.extend(shlex.split(os.environ["IGRAPH_CMAKE_EXTRA_ARGS"]))

        # Finally, add the source folder path
        args.append(str(build_to_source_folder))

        retcode = subprocess.call(args)
        if retcode:
            return False

        print("Running build...")
        # We are _not_ using a parallel build; this is intentional, see igraph/igraph#1755
        retcode = subprocess.call([cmake, "--build", ".", "--config", "Release"])
        if retcode:
            return False

        print("Installing build...")
        retcode = subprocess.call(
            [
                cmake,
                "--install",
                ".",
                "--prefix",
                str(install_folder),
                "--config",
                "Release",
            ]
        )
        if retcode:
            return False

        pkgconfig_candidates = [
            install_folder / "lib" / "pkgconfig" / "igraph.pc",
            install_folder / "lib64" / "pkgconfig" / "igraph.pc",
        ]
        for candidate in pkgconfig_candidates:
            if candidate.exists():
                return self._parse_pkgconfig_file(candidate)

        raise RuntimeError(
            "no igraph.pc was found in the installation folder of igraph"
        )

    def create_build_config_file(
        self, install_folder: Path, libraries: List[str]
    ) -> None:
        with (install_folder / "build.cfg").open("w") as fp:
            fp.write(repr(libraries))

    def _parse_pkgconfig_file(self, filename: Path) -> List[str]:
        building_on_windows = building_on_windows_msvc()

        if building_on_windows:
            libraries = ["igraph"]
        else:
            libraries = []
            with filename.open("r") as fp:
                for line in fp:
                    if line.startswith("Libs: ") or line.startswith("Libs.private: "):
                        words = line.strip().split()
                        libraries.extend(
                            word[2:] for word in words if word.startswith("-l")
                        )

            if not libraries:
                # Educated guess
                libraries = ["igraph"]

        return libraries


###########################################################################


class BuildConfiguration:
    def __init__(self):
        self.include_dirs = []
        self.library_dirs = []
        self.runtime_library_dirs = []
        self.libraries = []
        self.extra_compile_args = []
        self.extra_link_args = []
        self.define_macros = []
        self.extra_objects = []
        self.static_extension = False
        self.use_pkgconfig = False
        self.c_core_built = False
        self._has_pkgconfig = None
        self.excluded_include_dirs = []
        self.excluded_library_dirs = []
        self.wait = platform.system() != "Windows"

    @property
    def has_pkgconfig(self) -> bool:
        """Returns whether ``pkg-config`` is available on the current system
        and it knows about igraph or not."""
        if self._has_pkgconfig is None:
            if self.use_pkgconfig:
                _, exit_code = get_output_single_line(["pkg-config", "igraph"])
                self._has_pkgconfig = exit_code == 0
            else:
                self._has_pkgconfig = False
        return self._has_pkgconfig

    @property
    def build_c_core(self) -> Command:
        """Returns a class representing a custom setup.py command that builds
        the C core of igraph.

        This is used in CI environments where we want to build the C core of
        igraph once and then build the Python interface for various Python
        versions without having to recompile the C core all the time.

        If is also used as a custom building block of `build_ext`.
        """

        buildcfg = self

        class build_c_core(Command):
            description = "Compile the C core of igraph only"
            user_options = []

            def initialize_options(self):
                pass

            def finalize_options(self):
                pass

            def run(self):
                buildcfg.c_core_built = buildcfg.compile_igraph_from_vendor_source()

        return build_c_core

    @property
    def build_ext(self) -> Command:
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

                # Check whether the user asked us to discover a pre-built igraph
                # with pkg-config
                detected = False
                if buildcfg.use_pkgconfig:
                    detected = buildcfg.detect_from_pkgconfig()
                    if not detected:
                        print(
                            "Cannot find the C core of igraph on this system using pkg-config."
                        )
                        sys.exit(1)
                else:
                    # Build the C core from the vendored igraph source
                    self.run_command("build_c_core")
                    if not buildcfg.c_core_built:
                        # Fall back to an educated guess if everything else failed
                        if not detected:
                            buildcfg.use_educated_guess()

                # Add any extra library paths if needed; this is needed for the
                # Appveyor CI build
                if "IGRAPH_EXTRA_LIBRARY_PATH" in os.environ:
                    buildcfg.library_dirs = (
                        list(os.environ["IGRAPH_EXTRA_LIBRARY_PATH"].split(os.pathsep))
                        + buildcfg.library_dirs
                    )

                # Add extra libraries that may have been specified
                if "IGRAPH_EXTRA_LIBRARIES" in os.environ:
                    extra_libraries = os.environ["IGRAPH_EXTRA_LIBRARIES"].split(",")
                    buildcfg.libraries.extend(extra_libraries)

                # Override static specification based on environment variable
                if "IGRAPH_STATIC_EXTENSION" in os.environ:
                    if os.environ["IGRAPH_STATIC_EXTENSION"].lower() in [
                        "true",
                        "1",
                        "on",
                    ]:
                        buildcfg.static_extension = True
                    else:
                        buildcfg.static_extension = False

                # Replaces library names with full paths to static libraries
                # where possible. libm.a is excluded because it caused problems
                # on Sabayon Linux where libm.a is probably not compiled with
                # -fPIC
                if buildcfg.static_extension:
                    if buildcfg.static_extension == "only_igraph":
                        buildcfg.replace_static_libraries(only=["igraph"])
                    else:
                        buildcfg.replace_static_libraries(exclusions=["m"])

                # Add extra libraries that may have been specified
                if "IGRAPH_EXTRA_DYNAMIC_LIBRARIES" in os.environ:
                    extra_libraries = os.environ[
                        "IGRAPH_EXTRA_DYNAMIC_LIBRARIES"
                    ].split(",")
                    buildcfg.libraries.extend(extra_libraries)

                # Remove C++ standard library as we will use the C++ linker
                for lib in ("c++", "stdc++"):
                    if lib in buildcfg.libraries:
                        buildcfg.libraries.remove(lib)

                # Prints basic build information
                buildcfg.print_build_info()

                # Find the igraph extension and configure it with the settings
                # of this build configuration
                ext = first(
                    extension
                    for extension in self.extensions
                    if extension.name == "igraph._igraph"
                )
                buildcfg.configure(ext)

                # Run the original build_ext command
                build_ext.run(self)

        return custom_build_ext

    @property
    def sdist(self):
        """Returns a class that can be used as a replacement for the
        ``sdist`` command in ``setuptools`` and that will clean up
        ``vendor/source/igraph`` before running the original ``sdist``
        command.
        """
        from setuptools.command.sdist import sdist

        def is_git_repo(folder) -> bool:
            return (Path(folder) / ".git").exists()

        def cleanup_git_repo(folder) -> None:
            with working_directory(folder):
                if os.path.exists(".git"):
                    retcode = subprocess.call("git clean -dfx", shell=True)
                    if retcode:
                        raise RuntimeError(f"Failed to clean {folder} with git")

        class custom_sdist(sdist):
            def run(self):
                igraph_source_repo = Path("vendor", "source", "igraph")
                igraph_build_dir = Path("vendor", "build", "igraph")
                version_file = igraph_source_repo / "IGRAPH_VERSION"
                version = None

                # Check whether the source repo contains an IGRAPH_VERSION file,
                # and extract the version number from that
                if version_file.exists():
                    version = version_file.read_text().strip().split("\n")[0]

                # If no IGRAPH_VERSION file exists, but we have a git repo, try
                # git describe
                if not version and is_git_repo(igraph_source_repo):
                    with working_directory(igraph_source_repo):
                        version = (
                            subprocess.check_output("git describe", shell=True)
                            .decode("utf-8")
                            .strip()
                        )

                # If we still don't have a version number, try to parse it from
                # include/igraph_version.h
                if not version:
                    version_header = igraph_build_dir / "include" / "igraph_version.h"
                    if not version_header.exists():
                        raise RuntimeError(
                            "You need to build the C core of igraph first before generating a source tarball of python-igraph"
                        )

                    with version_header.open("r") as fp:
                        lines = [
                            line.strip()
                            for line in fp
                            if line.startswith("#define IGRAPH_VERSION ")
                        ]
                        if len(lines) == 1:
                            version = lines[0].split('"')[1]

                if not isinstance(version, str) or len(version) < 5:
                    raise RuntimeError(
                        f"Cannot determine the version number of the C core in {igraph_source_repo}"
                    )

                if not is_git_repo(igraph_source_repo):
                    # python-igraph was extracted from an official tarball so
                    # there is no need to tweak anything
                    return sdist.run(self)
                else:
                    # Clean up vendor/source/igraph with git
                    cleanup_git_repo(igraph_source_repo)

                    # Copy the generated parser sources from the build folder
                    parser_dir = igraph_build_dir / "src" / "io" / "parsers"
                    if parser_dir.is_dir():
                        shutil.copytree(
                            parser_dir,
                            igraph_source_repo / "src" / "io" / "parsers"
                        )
                    else:
                        raise RuntimeError(
                            "You need to build the C core of igraph first before "
                            "generating a source tarball of python-igraph"
                        )

                    # Add a version file to the tarball
                    version_file.write_text(version)

                    # Run the original sdist command
                    retval = sdist.run(self)

                    # Clean up vendor/source/igraph with git again
                    cleanup_git_repo(igraph_source_repo)

                    return retval

        return custom_sdist

    def compile_igraph_from_vendor_source(self) -> bool:
        """Compiles igraph from the vendored source code inside `vendor/source/igraph`.
        This folder typically comes from a git submodule.
        """
        vendor_folder = Path("vendor")
        source_folder = vendor_folder / "source" / "igraph"
        build_folder = vendor_folder / "build" / "igraph"
        install_folder = vendor_folder / "install" / "igraph"

        if install_folder.exists():
            # Vendored igraph already compiled and installed, just use it
            self.use_vendored_igraph()
            return True

        if (source_folder / "CMakeLists.txt").exists():
            igraph_builder = IgraphCCoreCMakeBuilder()
        else:
            print("Cannot find vendored igraph source in {0}".format(source_folder))
            print("")
            return False

        print("We are going to build the C core of igraph.")
        print("  Source folder: {0}".format(source_folder))
        print("  Build folder: {0}".format(build_folder))
        print("  Install folder: {0}".format(install_folder))
        print("")

        source_folder = source_folder.resolve()
        build_folder = build_folder.resolve()
        install_folder = install_folder.resolve()

        Path(build_folder).mkdir(parents=True, exist_ok=True)

        libraries = igraph_builder.compile_in(
            source_folder=source_folder,
            build_folder=build_folder,
            install_folder=install_folder,
        )

        if libraries is False:
            print("Build failed for the C core of igraph.")
            print("")
            sys.exit(1)

        assert not isinstance(libraries, bool)

        igraph_builder.create_build_config_file(install_folder, libraries)

        self.use_vendored_igraph()
        return True

    def configure(self, ext) -> None:
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
        ext.define_macros = self.define_macros

    def detect_from_pkgconfig(self) -> bool:
        """Detects the igraph include directory, library directory and the
        list of libraries to link to using ``pkg-config``."""
        if not buildcfg.has_pkgconfig:
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

    def print_build_info(self) -> None:
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
            elif option == "--use-pkg-config":
                opts_to_remove.append(idx)
                self.use_pkgconfig = True

        for idx in reversed(opts_to_remove):
            sys.argv[idx : (idx + 1)] = []

    def replace_static_libraries(self, only=None, exclusions=None):
        """Replaces references to libraries with full paths to their static
        versions if the static version is to be found on the library path."""
        if exclusions is None:
            exclusions = []

        for library_name in set(self.libraries) - set(exclusions):
            if only is not None and library_name not in only:
                continue

            static_lib = find_static_library(library_name, self.library_dirs)
            if static_lib:
                print(f"Found {library_name} as static library in {static_lib}.")
                self.libraries.remove(library_name)
                self.extra_objects.append(static_lib)
            else:
                print(f"Warning: could not find static library of {library_name}.")

    def use_vendored_igraph(self) -> None:
        """Assumes that igraph is installed already in ``vendor/install/igraph`` and sets up
        the include and library paths and the library names accordingly."""
        building_on_windows = building_on_windows_msvc()

        vendor_dir = Path("vendor") / "install" / "igraph"

        buildcfg.include_dirs = [str(vendor_dir / "include" / "igraph")]
        buildcfg.library_dirs = []

        for candidate in ("lib", "lib64"):
            candidate = vendor_dir / candidate
            if candidate.exists():
                buildcfg.library_dirs.append(str(candidate))
                break
        else:
            raise RuntimeError(
                "cannot detect igraph library dir within " + str(vendor_dir)
            )

        if not buildcfg.static_extension:
            buildcfg.static_extension = "only_igraph"
            if building_on_windows:
                buildcfg.define_macros.append(("IGRAPH_STATIC", "1"))

        buildcfg_file = vendor_dir / "build.cfg"
        if buildcfg_file.exists():
            buildcfg.libraries = eval(buildcfg_file.open("r").read())

    def use_educated_guess(self) -> None:
        """Tries to guess the proper library names, include and library paths
        if everything else failed."""

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

        if self.wait:
            wait_for_keypress(seconds=10)

        self.libraries = LIBIGRAPH_FALLBACK_LIBRARIES[:]
        if self.static_extension:
            self.libraries.extend(["xml2", "z", "m", "stdc++"])
        self.include_dirs = LIBIGRAPH_FALLBACK_INCLUDE_DIRS[:]
        self.library_dirs = LIBIGRAPH_FALLBACK_LIBRARY_DIRS[:]


###########################################################################

# Import version number from version.py so we only need to change it in
# one place when a new release is created
__version__ = None
exec(open("src/igraph/version.py").read())

# Process command line options
buildcfg = BuildConfiguration()
buildcfg.process_args_from_command_line()

# Define the extension
sources = glob.glob(os.path.join("src", "_igraph", "*.c"))
sources.append(os.path.join("src", "_igraph", "force_cpp_linker.cpp"))
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
"""

headers = ["src/_igraph/igraphmodule_api.h"] if not SKIP_HEADER_INSTALL else []

options = dict(
    name="python-igraph",
    version=__version__,
    url="https://igraph.org/python",
    description="High performance graph data structures and algorithms",
    long_description=description,
    license="GNU General Public License (GPL)",
    author="Tamas Nepusz",
    author_email="ntamas@gmail.com",
    project_urls={
        "Bug Tracker": "https://github.com/igraph/python-igraph/issues",
        "CI": "https://github.com/igraph/python-igraph/actions",
        "Documentation": "https://igraph.org/python/doc",
        "Source Code": "https://github.com/igraph/python-igraph",
    },
    ext_modules=[igraph_extension],
    package_dir={"igraph": "src/igraph"},
    packages=["igraph", "igraph.app", "igraph.drawing", "igraph.remote"],
    scripts=["scripts/igraph"],
    install_requires=["texttable>=1.6.2"],
    extras_require={
        "plotting": ["cairocffi>=1.2.0"],
        "test": [
            "networkx>=2.5",
            "pytest>=6.2.5",
            "numpy>=1.19.0; platform_python_implementation != 'PyPy'",
            "pandas>=1.1.0,<1.3.1; platform_python_implementation != 'PyPy'",
            "scipy>=1.5.0; platform_python_implementation != 'PyPy'",
        ],
        "doc": [
            "Sphinx>=4.2.0",
            "sphinxbootstrap4theme>=0.6.0"
        ]
    },
    python_requires=">=3.6",
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
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    cmdclass={
        "build_c_core": buildcfg.build_c_core,  # used by CI
        "build_ext": buildcfg.build_ext,
        "sdist": buildcfg.sdist,
    },
)

setup(**options)
