IGRAPH_VERSION=0.10.13

ROOT_DIR=`pwd`
echo "Using root dir ${ROOT_DIR}"

# Create source directory
if [ ! -d "${ROOT_DIR}/build-deps/src" ]; then
  echo ""
  echo "Make directory ${ROOT_DIR}/build-deps/src"
  mkdir -p ${ROOT_DIR}/build-deps/src
fi

cd ${ROOT_DIR}/build-deps/src
if [ ! -d "igraph" ]; then
  echo ""
  echo "Cloning igraph into ${ROOT_DIR}/build-deps/src/igraph"
  # Clone repository if it does not exist yet
  git clone --branch ${IGRAPH_VERSION} https://github.com/igraph/igraph.git --single-branch
fi

# Make sure the git repository points to the correct version
echo ""
echo "Checking out ${IGRAPH_VERSION} in ${ROOT_DIR}/build-deps/src/igraph"
cd ${ROOT_DIR}/build-deps/src/igraph
git fetch origin tag ${IGRAPH_VERSION} --no-tags
git checkout ${IGRAPH_VERSION}

# Make build directory
if [ ! -d "${ROOT_DIR}/build-deps/build/igraph" ]; then
  echo ""
  echo "Make directory ${ROOT_DIR}/build-deps/build/igraph"
  mkdir -p ${ROOT_DIR}/build-deps/build/igraph
fi

# Configure, build and install
cd ${ROOT_DIR}/build-deps/build/igraph

echo ""
echo "Configure igraph build"
cmake ${ROOT_DIR}/build-deps/src/igraph \
  -DCMAKE_INSTALL_PREFIX=${ROOT_DIR}/build-deps/install/ \
  -DBUILD_SHARED_LIBS=ON \
  -DIGRAPH_GLPK_SUPPORT=ON \
  -DIGRAPH_GRAPHML_SUPPORT=ON \
  -DIGRAPH_OPENMP_SUPPORT=ON \
  -DIGRAPH_USE_INTERNAL_BLAS=ON \
  -DIGRAPH_USE_INTERNAL_LAPACK=ON \
  -DIGRAPH_USE_INTERNAL_ARPACK=ON \
  -DIGRAPH_USE_INTERNAL_GLPK=ON \
  -DIGRAPH_USE_INTERNAL_GMP=ON \
  -DIGRAPH_WARNINGS_AS_ERRORS=OFF \
  -DCMAKE_BUILD_TYPE=Release \
  ${EXTRA_CMAKE_ARGS}

echo ""
echo "Build igraph"
cmake --build .

echo ""
echo "Install igraph to ${ROOT_DIR}/build-deps/install/"
cmake --build . --target install
