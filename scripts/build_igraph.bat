@echo off

set IGRAPH_VERSION=0.10.13

set ROOT_DIR=%cd%
echo Using root dir %ROOT_DIR%

if not exist "%ROOT_DIR%\build-deps\src\" (
  md %ROOT_DIR%\build-deps\src
)

cd "%ROOT_DIR%\build-deps\src"
if not exist "igraph\" (
  echo.
  echo Cloning igraph into %ROOT_DIR%\build-deps\src\igraph
  REM Clone repository if it does not exist yet
  git clone --depth 1 --branch %IGRAPH_VERSION% https://github.com/igraph/igraph.git
)

REM Make sure the git repository points to the correct version
echo.
echo Checking out %IGRAPH_VERSION} in ${ROOT_DIR%\build-deps\src\igraph
cd "%ROOT_DIR%\build-deps\src\igraph"
git fetch origin tag %IGRAPH_VERSION% --no-tags
git checkout %IGRAPH_VERSION%

REM Make build directory
if not exist "%ROOT_DIR%\build-deps\build\igraph\" (
  echo.
  echo Make directory %ROOT_DIR%\build-deps\build\igraph
  md %ROOT_DIR%\build-deps\build\igraph
)

REM Configure, build and install
cd "%ROOT_DIR%\build-deps\build\igraph"

echo.
echo Configure igraph build
cmake %ROOT_DIR%\build-deps\src\igraph ^
  -DCMAKE_INSTALL_PREFIX=%ROOT_DIR%\build-deps\install\ ^
  -DBUILD_SHARED_LIBS=ON ^
  -DIGRAPH_GLPK_SUPPORT=ON ^
  -DIGRAPH_GRAPHML_SUPPORT=ON ^
  -DIGRAPH_OPENMP_SUPPORT=ON ^
  -DIGRAPH_USE_INTERNAL_BLAS=ON ^
  -DIGRAPH_USE_INTERNAL_LAPACK=ON ^
  -DIGRAPH_USE_INTERNAL_ARPACK=ON ^
  -DIGRAPH_USE_INTERNAL_GLPK=ON ^
  -DIGRAPH_USE_INTERNAL_GMP=ON ^
  -DIGRAPH_WARNINGS_AS_ERRORS=OFF ^
  -DCMAKE_BUILD_TYPE=Release ^
  -DBUILD_TESTING=OFF ^
  %EXTRA_CMAKE_ARGS%

echo.
echo Build igraph
cmake --build . --config Release

echo.
echo Install igraph to %ROOT_DIR%\build-deps\install\
cmake --build . --target install --config Release

cd "%ROOT_DIR%"