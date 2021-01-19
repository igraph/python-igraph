#!usr/bin/env python

import os
import platform
import sys

###########################################################################

# Check Python's version info and exit early if it is too old
if sys.version_info < (3, 6):
    print("This module requires Python >= 3.6")
    sys.exit(0)

# Check whether we are compiling for PyPy. Headers will not be installed
# for PyPy.
SKIP_HEADER_INSTALL = (platform.python_implementation() == "PyPy") or (
    "SKIP_HEADER_INSTALL" in os.environ
)

###########################################################################

from setuptools import setup, Command, Extension

import distutils.ccompiler
import glob
import shutil
import subprocess
import sys
import sysconfig

from select import select
from time import sleep

###########################################################################

LIBIGRAPH_FALLBACK_INCLUDE_DIRS = ["/usr/include/igraph", "/usr/local/include/igraph"]
LIBIGRAPH_FALLBACK_LIBRARIES = ["igraph"]
LIBIGRAPH_FALLBACK_LIBRARY_DIRS = []

###########################################################################


def building_on_windows_msvc():
    """Returns True when using the non-MinGW CPython interpreter on Windows"""
    return platform.system() == "Windows" and sysconfig.get_platform() != "mingw"


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


def find_executable(name):
    """Finds an executable with the given name on the system PATH and returns
    its full path.
    """
    try:
        from shutil import which

        return which(name)  # Python 3.3 and above
    except ImportError:
        import distutils.spawn

        return distutils.spawn.find_executable(name)  # Earlier than Python 3.3


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


def find_msvc_source_folder(folder=".", requires_built=False):
    """Finds the folder that contains the MSVC-specific source of igraph if there
    is any. Returns `None` if no such folder is found. Prints a warning if the
    choice is ambiguous.
    """
    all_msvc_dirs = glob.glob(os.path.join(folder, "igraph-*-msvc"))
    if len(all_msvc_dirs) > 0:
        if len(all_msvc_dirs) > 1:
            print("More than one MSVC build directory (..\\..\\igraph-*-msvc) found!")
            print(
                "It could happen that setup.py uses the wrong one! Please remove all but the right one!\n\n"
            )

        msvc_builddir = all_msvc_dirs[-1]
        if requires_built and not os.path.exists(
            os.path.join(msvc_builddir, "Release")
        ):
            print(
                "There is no 'Release' dir in the MSVC build directory\n(%s)"
                % msvc_builddir
            )
            print("Please build the MSVC build first!\n")
            return None

        return msvc_builddir
    else:
        return None


def preprocess_fallback_config():
    """Preprocesses the fallback include and library paths depending on the
    platform."""
    global LIBIGRAPH_FALLBACK_INCLUDE_DIRS
    global LIBIGRAPH_FALLBACK_LIBRARY_DIRS
    global LIBIGRAPH_FALLBACK_LIBRARIES

    if (
        platform.system() == "Windows"
        and distutils.ccompiler.get_default_compiler() == "msvc"
    ):
        # if this setup is run in the source checkout *and* the igraph msvc was build,
        # this code adds the right library and include dir
        msvc_builddir = find_msvc_source_folder(
            os.path.join("..", ".."), requires_built=True
        )

        if msvc_builddir is not None:
            print("Using MSVC build dir: %s\n\n" % msvc_builddir)
            LIBIGRAPH_FALLBACK_INCLUDE_DIRS = [os.path.join(msvc_builddir, "include")]
            LIBIGRAPH_FALLBACK_LIBRARY_DIRS = [os.path.join(msvc_builddir, "Release")]
            return True
        else:
            return False

    else:
        return True


def quote_path_for_shell(s):
    # On MinGW / MSYS, we need to use forward slash style and remove unsafe
    # characters in order not to trip up the configure script
    if "MSYSTEM" in os.environ:
        s = s.replace("\\", "/")
        if s[1:3] == ":/":
            s = "/" + s[0] + s[2:]

    # Now the proper quoting
    return "'" + s.replace("'", "'\\''") + "'"


def wait_for_keypress(seconds):
    """Wait for a keypress or until the given number of seconds have passed,
    whichever happens first.
    """
    is_windows = platform.system() == "windows"

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

        if is_windows:
            from msvcrt import kbhit

            for i in range(10):
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


###########################################################################


class IgraphCCoreAutotoolsBuilder(object):
    """Class responsible for downloading and building the C core of igraph
    if it is not installed yet, assuming that the C core uses `configure.ac`
    and its friends. This used to be the case before igraph 0.9.
    """

    def compile_in(self, source_folder, build_folder, install_folder):
        """Compiles igraph from its source code in the given folder.

        source_folder is the name of the folder that contains igraph's source
        files. build_folder is the name of the folder where the build should
        be executed. Both must be absolute paths.

        Returns:
            False if the build failed or the list of libraries to link to when
            linking the Python interface to igraph
        """
        build_to_source_folder = os.path.relpath(source_folder, build_folder)

        os.chdir(source_folder)

        # Run the bootstrap script if we have downloaded a tarball from
        # Github
        if os.path.isfile("bootstrap.sh") and not os.path.isfile("configure"):
            print("Bootstrapping igraph...")
            retcode = subprocess.call("sh bootstrap.sh", shell=True)
            if retcode:
                return False

        # Patch ltmain.sh so it does not freak out when the build directory
        # contains spaces
        with open("ltmain.sh") as infp:
            with open("ltmain.sh.new", "w") as outfp:
                for line in infp:
                    if line.endswith("cd $darwin_orig_dir\n"):
                        line = line.replace(
                            "cd $darwin_orig_dir\n", 'cd "$darwin_orig_dir"\n'
                        )
                    outfp.write(line)
        shutil.move("ltmain.sh.new", "ltmain.sh")

        os.chdir(build_folder)

        print("Configuring igraph...")
        configure_args = ["--disable-tls", "--enable-silent-rules"]
        if "IGRAPH_EXTRA_CONFIGURE_ARGS" in os.environ:
            configure_args.extend(os.environ["IGRAPH_EXTRA_CONFIGURE_ARGS"].split(" "))
        retcode = subprocess.call(
            "sh {0} {1}".format(
                quote_path_for_shell(os.path.join(build_to_source_folder, "configure")),
                " ".join(configure_args),
            ),
            env=self.enhanced_env(CFLAGS="-fPIC", CXXFLAGS="-fPIC"),
            shell=True,
        )
        if retcode:
            return False

        building_on_windows = building_on_windows_msvc()

        if building_on_windows:
            print("Creating Microsoft Visual Studio project...")
            retcode = subprocess.call("make msvc", shell=True)
            if retcode:
                return False

        print("Building igraph...")
        if building_on_windows:
            msvc_source = find_msvc_source_folder()
            if not msvc_source:
                return False

            devenv = os.environ.get("DEVENV_EXECUTABLE")
            os.chdir(msvc_source)
            if devenv is None:
                retcode = subprocess.call("devenv /upgrade igraph.vcproj", shell=True)
            else:
                retcode = subprocess.call([devenv, "/upgrade", "igraph.vcproj"])
            if retcode:
                return False

            retcode = subprocess.call(
                "msbuild.exe igraph.vcxproj /p:configuration=Release"
            )
        else:
            retcode = subprocess.call("make", shell=True)

        if retcode:
            return False

        if building_on_windows:
            libraries = ["igraph"]
        else:
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

    def copy_build_artifacts(
        self, source_folder, build_folder, install_folder, libraries
    ):
        building_on_windows = building_on_windows_msvc()

        create_dir_unless_exists(install_folder)

        ensure_dir_does_not_exist(install_folder, "include")
        ensure_dir_does_not_exist(install_folder, "lib")

        shutil.copytree(
            os.path.join(source_folder, "include"),
            os.path.join(install_folder, "include"),
        )
        create_dir_unless_exists(install_folder, "lib")

        for fname in glob.glob(os.path.join(build_folder, "include", "*.h")):
            shutil.copy(fname, os.path.join(install_folder, "include"))

        if building_on_windows:
            msvc_builddir = find_msvc_source_folder(build_folder, requires_built=True)
            if msvc_builddir is not None:
                print("Using MSVC build dir: %s\n\n" % msvc_builddir)
                for fname in glob.glob(os.path.join(msvc_builddir, "Release", "*.lib")):
                    shutil.copy(fname, os.path.join(install_folder, "lib"))
            else:
                print("Cannot find MSVC build dir in %s\n\n" % build_folder)
                return False
        else:
            for fname in glob.glob(
                os.path.join(build_folder, "src", ".libs", "libigraph.*")
            ):
                shutil.copy(fname, os.path.join(install_folder, "lib"))

        with open(os.path.join(install_folder, "build.cfg"), "w") as f:
            f.write(repr(libraries))

        return True

    @staticmethod
    def enhanced_env(**kwargs):
        env = os.environ.copy()
        for k, v in kwargs.items():
            prev = os.environ.get(k)
            env[k] = "{0} {1}".format(prev, v) if prev else v
        return env


###########################################################################


class IgraphCCoreCMakeBuilder(object):
    """Class responsible for downloading and building the C core of igraph
    if it is not installed yet, assuming that the C core uses CMake as the
    build tool. This is the case from igraph 0.9.

    Returns:
        False if the build failed or the list of libraries to link to when
        linking the Python interface to igraph
    """

    def compile_in(self, source_folder, build_folder, install_folder):
        """Compiles igraph from its source code in the given folder.

        source_folder is the name of the folder that contains igraph's source
        files. build_folder is the name of the folder where the build should
        be executed. Both must be absolute paths.
        """
        cmake = find_executable("cmake")
        if not cmake:
            print(
                "igraph uses CMake as the build system. You need to install CMake "
                "before compiling igraph."
            )
            return False

        build_to_source_folder = os.path.relpath(source_folder, build_folder)
        os.chdir(build_folder)

        print("Configuring build...")
        args = [cmake, build_to_source_folder]
        for deps in "ARPACK BLAS CXSPARSE GLPK LAPACK".split():
            args.append("-DIGRAPH_USE_INTERNAL_" + deps + "=ON")

        retcode = subprocess.call(args)
        if retcode:
            return False

        print("Running build...")
        retcode = subprocess.call(
            [cmake, "--build", ".", "--parallel", "--config", "Release"]
        )
        if retcode:
            return False

        print("Installing build...")
        retcode = subprocess.call([cmake, "--install", ".", "--prefix", install_folder])
        if retcode:
            return False

    def copy_build_artifacts(
        self, source_folder, build_folder, install_folder, libraries
    ):
        raise NotImplementedError


###########################################################################


class BuildConfiguration(object):
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
        self._has_pkgconfig = None
        self.excluded_include_dirs = []
        self.excluded_library_dirs = []
        self.wait = platform.system() != "Windows"

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
    def build_c_core(self):
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

        class custom_sdist(sdist):
            def run(self):
                # Clean up vendor/source/igraph with git
                cwd = os.getcwd()
                try:
                    os.chdir(os.path.join("vendor", "source", "igraph"))
                    if os.path.exists(".git"):
                        retcode = subprocess.call("git clean -dfx", shell=True)
                        if retcode:
                            print("Failed to clean vendor/source/igraph with git")
                            print("")
                            return False
                finally:
                    os.chdir(cwd)

                # Run the original sdist command
                sdist.run(self)

        return custom_sdist

    def compile_igraph_from_vendor_source(self):
        """Compiles igraph from the vendored source code inside `vendor/igraph/source`.
        This folder typically comes from a git submodule.
        """
        if os.path.exists(os.path.join("vendor", "install", "igraph")):
            # Vendored igraph already compiled and installed, just use it
            self.use_vendored_igraph()
            return True

        vendor_source_path = os.path.join("vendor", "source", "igraph")
        if os.path.isfile(os.path.join(vendor_source_path, "CMakeLists.txt")):
            igraph_builder = IgraphCCoreCMakeBuilder()
        elif os.path.isfile(os.path.join(vendor_source_path, "configure.ac")):
            igraph_builder = IgraphCCoreAutotoolsBuilder()
        else:
            # No git submodule present with vendored source
            print("Cannot find vendored igraph source in " + vendor_source_path)
            print("")
            return False

        source_folder = os.path.join("vendor", "source", "igraph")
        build_folder = os.path.join("vendor", "build", "igraph")
        install_folder = os.path.join("vendor", "install", "igraph")

        print("We are going to build the C core of igraph.")
        print("  Source folder: %s" % source_folder)
        print("  Build folder: %s" % build_folder)
        print("  Install folder: %s" % install_folder)
        print("")

        source_folder = os.path.abspath(source_folder)
        build_folder = os.path.abspath(build_folder)
        install_folder = os.path.abspath(install_folder)

        create_dir_unless_exists(build_folder)

        cwd = os.getcwd()
        try:
            libraries = igraph_builder.compile_in(
                source_folder=source_folder,
                build_folder=build_folder,
                install_folder=install_folder,
            )
        finally:
            os.chdir(cwd)

        if not libraries or not igraph_builder.copy_build_artifacts(
            source_folder=source_folder,
            build_folder=build_folder,
            install_folder=install_folder,
            libraries=libraries,
        ):
            print("Could not compile the C core of igraph.")
            print("")
            sys.exit(1)

        self.use_vendored_igraph()
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
        ext.define_macros = self.define_macros

    def detect_from_pkgconfig(self):
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
            elif option == "--use-pkg-config":
                opts_to_remove.append(idx)
                self.use_pkgconfig = True

        for idx in reversed(opts_to_remove):
            sys.argv[idx : (idx + 1)] = []

    def replace_static_libraries(self, only=None, exclusions=None):
        """Replaces references to libraries with full paths to their static
        versions if the static version is to be found on the library path."""
        building_on_windows = building_on_windows_msvc()

        if not building_on_windows and "stdc++" not in self.libraries:
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
        """Assumes that igraph is installed already in ``vendor/install/igraph`` and sets up
        the include and library paths and the library names accordingly."""
        building_on_windows = building_on_windows_msvc()

        buildcfg.include_dirs = [os.path.join("vendor", "install", "igraph", "include")]
        buildcfg.library_dirs = [os.path.join("vendor", "install", "igraph", "lib")]
        if not buildcfg.static_extension:
            buildcfg.static_extension = "only_igraph"
            if building_on_windows:
                buildcfg.define_macros.append(("IGRAPH_STATIC", "1"))

        buildcfg_file = os.path.join("vendor", "install", "igraph", "build.cfg")
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
    ext_modules=[igraph_extension],
    package_dir={"igraph": "src/igraph"},
    packages=["igraph", "igraph.app", "igraph.drawing", "igraph.remote"],
    scripts=["scripts/igraph"],
    install_requires=["texttable>=1.6.2"],
    extras_require={"plotting": ["pycairo>=1.18.0"]},
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
