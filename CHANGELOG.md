# igraph Python interface changelog

## [Unreleased]

### Changed

- UMAP layout now exposes the computation of the symmetrized edge weights via
  `umap_compute_weights()`. The layout function, `Graph.layout_umap()`, can
  now be called either on a directed graph with edge distances, or on an
  undirected graph with edge weights, typically computed via
  `umap_compute_weights()` or precomputed by the user. Moreover, the
  `sampling_prob` argument was faulty and has been removed. See PR
  [#613](https://github.com/igraph/python-igraph/pull/613) for details.

### Fixed

- `Graph.Data_Frame()` now handles the `Int64` data type from `pandas`, thanks
  to [@Adriankhl](https://github.com/Adriankhl). See PR
  [#609](https://github.com/igraph/python-igraph/pull/609) for details.

- `Graph.layout_lgl()` `root` argument is now optional (as it should have been).

- The `VertexClustering` class now handles partial dendrograms correctly.

## [0.10.2] - 2022-10-14

### Added

- `python-igraph` is now tested in Python 3.11.

- Added `Graph.modularity_matrix()` to calculate the modularity matrix of
  a graph.

- Added `Graph.get_k_shortest_paths()`, thanks to
  [@sombreslames](https://github.com/user/sombreslames). See PR
  [#577](https://github.com/igraph/python-igraph/pull/577) for details.

- The `setup.py` script now also accepts environment variables instead of
  command line arguments to configure several aspects of the build process
  (i.e. whether a fully static extension is being built, or whether it is
  allowed to use `pkg-config` to retrieve the compiler and linker flags for
  an external `igraph` library instead of the vendored one). The environment
  variables are named similarly to the command line arguments but in
  uppercase, dashes replaced with underscores, and they are prefixed with
  `IGRAPH_` (i.e. `--use-pkg-config` becomes `IGRAPH_USE_PKG_CONFIG`).

### Changed

- The C core of igraph was updated to version 0.10.2, fixing a range of bugs
  originating from the C core.

### Fixed

- Fixed a crash in `Graph.decompose()` that was accidentally introduced in
  0.10.0 during the transition to `igraph_graph_list_t` in the C core.

- `Clustering.sizes()` now works correctly even if the membership vector
  contains `None` items.

- `Graph.modularity()` and `Graph.community_multilevel()` now correctly expose
  the `resolution` parameter.

- Fixed a reference leak in `Graph.is_chordal()` that decreased the reference
  count of Python's built-in `True` and `False` constants unnecessarily.

- Unit tests updated to get rid of deprecation warnings in Python 3.11.

## [0.10.1] - 2022-09-12

### Added

- Added `Graph.minimum_cycle_basis()` and `Graph.fundamental_cycles()`

- `Graph.average_path_length()` now supports edge weights.

### Fixed

- Restored missing exports from `igraph.__all__` that used to be in the main
  `igraph` package before 0.10.0.

## [0.10.0] - 2022-09-05

### Added

- More robust support for Matplotlib and initial support for plotly as graph
  plotting backends, controlled by a configuration option. See PR
  [#425](https://github.com/igraph/python-igraph/pull/425) for more details.

- Added support for additional ways to construct a graph, such as from a 
  dictionary of dictionaries, and to export a graph object back to those
  data structures. See PR [#434](https://github.com/igraph/python-igraph/pull/434)
  for more details.

- `Graph.list_triangles()` lists all triangles in a graph.

- `Graph.reverse_edges()` reverses some or all edges of a graph.

- `Graph.Degree_Sequence()` now supports the `"no_multiple_uniform"` generation
  method, which generates simple graphs, sampled uniformly, using rejection
  sampling.

- `Graph.Lattice()` now supports per-dimension periodicity control.

- `Graph.get_adjacency()` now allows the user to specify whether loop edges
  should be counted once or twice, or not at all.

- `Graph.get_laplacian()` now supports left-, right- and symmetric normalization.

- `Graph.modularity()` now supports setting the resolution with the
  `resolution=...` parameter.

### Changed

- The C core of igraph was updated to version 0.10.0.

- We now publish `abi3` wheels on PyPI from CPython 3.9 onwards, making it
  possible to use an already-built Python wheel with newer minor Python
  releases (and also reducing the number of wheels we actually need to
  publish). Releases for CPython 3.7 and 3.8 still use version-specific wheels
  because the code of the C part of the extension contains conditional macros
  for CPython 3.7 and 3.8.

- Changed default value of the `use_vids=...` argument of `Graph.DataFrame()`
  to `True`, thanks to [@fwitter](https://github.com/user/fwitter).

- `Graph.Degree_Sequence()` now accepts all sorts of sequences as inputs, not
  only lists.

### Fixed

- The Matplotlib backend now allows `edge_color` and `edge_width` to be set
  on an edge-by-edge basis.

### Removed

- Dropped support for Python 3.6.

- Removed deprecated `UbiGraphDrawer`.

- Removed deprecated `show()` method of `Plot` instances as well as the feature
  that automatically shows the plot when `plot()` is called with no target.

- Removed the `eids` keyword argument of `get_adjacency()`.

### Deprecated

- `Graph.clusters()` is now deprecated; use `Graph.connected_components()` or
  its already existing shorter alias, `Graph.components()`.

- `Graph.shortest_paths()` is now deprecated; use `Graph.distances()` instead.

## [0.9.11]

### Added

- We now publish `musllinux` wheels on PyPI.

### Changed

- Vendored igraph was updated to version 0.9.9.

### Fixed

- Graph union and intersection (by name) operators now verify that there are no
  duplicate names within the individual graphs.

- Fixed a memory leak in `Graph.union()` when edge maps were used; see
  [#534](https://github.com/igraph/python-igraph/issues/534) for details.

- Fixed a bug in the Cairo and Matplotlib backends that prevented edges with
  labels from being drawn properly; see
  [#535](https://github.com/igraph/python-igraph/issues/535) for details.

## [0.9.10]

### Changed

- Vendored igraph was updated to version 0.9.8.

### Fixed

- Fixed plotting of curved edges in the Cairo plotting backend.

- `setup.py` now looks for `igraph.pc` recursively in `vendor/install`; this
  fixes building igraph from source in certain Linux distributions

- `Graph.shortest_paths()` does not crash with zero-length weight vectors any
  more

- Fix a memory leak in `Graph.delete_vertices()` and other functions that
  convert a list of vertex IDs internally to an `igraph_vs_t` object, see
  [#503](https://github.com/igraph/python-igraph/issues/503) for details.

- Fixed potential memory leaks in `Graph.maximum_cardinality_search()`,
  `Graph.get_all_simple_paths()`, `Graph.get_subisomorphisms_lad()`, 
  `Graph.community_edge_betweenness()`, as well as the `union` and `intersection`
  operators.

- Fix a crash that happened when subclassing `Graph` and overriding `__new__()`
  in the subclass; see [#496](https://github.com/igraph/python-igraph/issues/496)
  for more details.

- Documentation now mentions that we now support graphs of size 5 or 6 for
  isomorphism / motif calculations if the graph is undirected

## [0.9.9]

### Changed

- Vendored igraph was updated to version 0.9.6.

### Fixed

- Fixed a performance bottleneck in `VertexSeq.select()` and `EdgeSeq.select()`
  for the case when the `VertexSeq` or the `EdgeSeq` represents the whole
  graph. See [#494](https://github.com/igraph/python-igraph/issues/494) for
  more details.

- Edge labels now take the curvature of the edge into account, thanks to
  [@Sriram-Pattabiraman](https://github.com/Sriram-Pattabiraman).
  ([#457](https://github.com/igraph/python-igraph/pull/457))

## [0.9.8]

### Changed

- `python-igraph` is now simply `igraph` on PyPI. `python-igraph` will be
  updated until Sep 1, 2022 but it will only be a stub package that pulls in
  `igraph` as its only dependency, with a matching version number. Please
  update your projects to depend on `igraph` instead of `python-igraph` to
  keep on receiving updates after Sep 1, 2022.

### Fixed

- `setup.py` no longer uses `distutils`, thanks to
  [@limburgher](https://github.com/limburgher).
  ([#449](https://github.com/igraph/python-igraph/pull/449))

## [0.9.7]

### Added

- Added support for graph chordality which was already available in the C core:
  `Graph.is_chordal()`, `Graph.chordal_completion()`, and
  `Graph.maximal_cardinality_search()`. See PR
  [#437](https://github.com/igraph/python-igraph/pull/437) for more details.
  Thanks to [@cptwunderlich](https://github.com/cptwunderlich) for requesting
  this.

- `Graph.write()` and `Graph.Read()` now accept `Path` objects as well as
  strings. See PR [#441](https://github.com/igraph/python-igraph/pull/441) for
  more details. Thanks to [@jboynyc](https://github.com/jboynyc) for the
  implementation.

### Changed

- Improved performance of `Graph.DataFrame()`, thanks to
  [@fwitter](https://github.com/user/fwitter). See PR
  [#418](https://github.com/igraph/python-igraph/pull/418) for more details.

### Fixed

- Fixed the Apple Silicon wheels so they should now work out of the box on
  newer Macs with Apple M1 CPUs.

- Fixed a bug that resulted in an unexpected error when plotting a graph with
  `wrap_labels=True` if the size of one of the vertices was zero or negative,
  thanks to [@jboynyc](https://github.com/user/jboynyc). See PR
  [#439](https://github.com/igraph/python-igraph/pull/439) for more details.

- Fixed a bug that sometimes caused random crashes in
  `Graph.Realize_Degree_Sequence()` and at other times caused weird errors in
  `Graph.Read_Ncol()` when it received an invalid data type.

## [0.9.6]

### Fixed

- Version 0.9.5 accidentally broke the Matplotlib backend when it was invoked
  without the `mark_groups=...` keyword argument; this version fixes the issue.
  Thanks to @dschult for reporting it!

## [0.9.5]

### Fixed

- `plot(g, ..., mark_groups=True)` now works with the Matplotlib plotting backend.

- `set_random_number_generator(None)` now correctly switches back to igraph's
  own random number generator instead of the default one that hooks into
  the `random` module of Python.

- Improved performance in cases when igraph has to call back to Python's
  `random` module to generate random numbers. One example is
  `Graph.Degree_Sequence(method="vl")`, whose performance suffered a more than
  30x slowdown on 32-bit platforms before, compared to the native C
  implementation. Now the gap is smaller. Note that if you need performance and
  do not care about seeding the random number generator from Python, you can
  now use `set_random_number_generator(None)` to switch back to igraph's own
  RNG that does not need a roundtrip to Python.

## [0.9.4]

### Added

- Added `Graph.is_tree()` to test whether a graph is a tree.

- Added `Graph.Realize_Degree_Sequence()` to construct a graph that realizes a
  given degree sequence, using a deterministic (Havel-Hakimi-style) algorithm.

- Added `Graph.Tree_Game()` to generate random trees with uniform sampling.

- `Graph.to_directed()` now supports a `mode=...` keyword argument.

- Added a `create_using=...` keyword argument to `Graph.to_networkx()` to
  let the user specify which NetworkX class to use when converting the graph.

### Changed

- Updated igraph dependency to 0.9.4.

### Fixed

- Improved performance of `Graph.from_networkx()` and `Graph.from_graph_tool()`
  on large graphs, thanks to @szhorvat and @iosonofabio for fixing the issue.

- Fixed the `autocurve=...` keyword argument of `plot()` when using the
  Matplotlib backend.

### Deprecated

- Functions and methods that take string arguments that represent an underlying
  enum in the C core of igraph now print a deprecation warning when provided
  with a string that does not match one of the enum member names (as documented
  in the docstrings) exactly. Partial matches will be removed in the next
  minor or major version, whichever comes first.

- `Graph.to_directed(mutual=...)` is now deprecated, use `mode=...` instead.

- `igraph.graph.drawing.UbiGraphDrawer` is deprecated as the upstream project
  is not maintained since 2008.

## [0.9.1]

### Changed

- Calling `plot()` without a filename or a target surface is now deprecated.
  The original intention was to plot to a temporary file and then open it in
  the default image viewer of the platform of the user automatically, but this
  has never worked reliably. The feature will be removed in 0.10.0.

### Fixed

- Fixed plotting of `VertexClustering` objects on Matplotlib axes.

- The `IGRAPH_CMAKE_EXTRA_ARGS` environment variable is now applied _after_ the
  default CMake arguments when building the C core of igraph from source. This
  enables package maintainers to override any of the default arguments we pass
  to CMake.

- Fixed the documentation build by replacing Epydoc with PyDoctor.

### Miscellaneous

- Building `python-igraph` from source should not require `flex` and `bison`
  any more; sources of the parsers used by the C core are now included in the
  Python source tarball.

- Many old code constructs that were used to maintain compatibility with Python
  2.x are removed now that we have dropped support for Python 2.x.

- Reading GraphML files is now also supported on Windows if you use one of the
  official Python wheels.

## [0.9.0]

### Added

- `Graph.DataFrame` now has a `use_vids=...` keyword argument that decides whether
  the data frame contains vertex IDs (`True`) or vertex names (`False`). (PR #348)

- Added `MatplotlibGraphDrawer` to draw a graph on an existing Matplotlib
  figure. (PR #341)

- Added a code path to choose between preferred image viewers on FreeBSD. (PR #354)

- Added `Graph.harmonic_centrality()` that wraps `igraph_harmonic_centrality()`
  from the underlying C library.

### Changed

- `python-igraph` is now compatible with `igraph` 0.9.0.

- The setup script was adapted to the new CMake-based build system of `igraph`.

- Dropped support for older Python versions; the oldest Python version that
  `python-igraph` is tested on is now Python 3.6.

- The default splitting heuristic of the BLISS isomorphism algorithm was changed
  from `IGRAPH_BLISS_FM` (first maximally non-trivially connected non-singleton cell)
  to `IGRAPH_BLISS_FL` (first largest non-singleton cell) as this seems to provide
  better performance on a variety of graph classes. This change is a follow-up
  of the change in the recommended heuristic in the core igraph C library.

### Fixed

- Fixed crashes in the Python-C glue code related to the handling of empty
  vectors in certain attribute merging functions (see issue #358).

- Fixed a memory leak in `Graph.closeness_centrality()` when an invalid `cutoff`
  argument was provided to the function.

- Clarified that the `fixed=...` argument is ineffective for the DrL layout
  because the underlying C code does not handle it. The argument was _not_
  removed for sake of backwards compatibility.

- `VertexSeq.find(name=x)` now works correctly when `x` is an integer; fixes
  #367

### Miscellaneous

- The Python codebase was piped through `black` for consistent formatting.

- Wildcard imports were removed from the codebase.

- CI tests were moved to Github Actions from Travis.

- The core C library is now built with `-fPIC` on Linux to allow linking to the
  Python interface.

## [0.8.3]

This is the last released version of `python-igraph` without a changelog file.
Please refer to the commit logs at https://github.com/igraph/python-igraph for
a list of changes affecting versions up to 0.8.3. Notable changes after 0.8.3
are documented above.

[Unreleased]: https://github.com/igraph/python-igraph/compare/0.10.2...master
[0.10.2]: https://github.com/igraph/python-igraph/compare/0.10.1...0.10.2
[0.10.1]: https://github.com/igraph/python-igraph/compare/0.10.0...0.10.1
[0.10.0]: https://github.com/igraph/python-igraph/compare/0.9.11...0.10.0
[0.9.11]: https://github.com/igraph/python-igraph/compare/0.9.10...0.9.11
[0.9.10]: https://github.com/igraph/python-igraph/compare/0.9.9...0.9.10
[0.9.9]: https://github.com/igraph/python-igraph/compare/0.9.8...0.9.9
[0.9.8]: https://github.com/igraph/python-igraph/compare/0.9.7...0.9.8
[0.9.7]: https://github.com/igraph/python-igraph/compare/0.9.6...0.9.7
[0.9.6]: https://github.com/igraph/python-igraph/compare/0.9.5...0.9.6
[0.9.5]: https://github.com/igraph/python-igraph/compare/0.9.4...0.9.5
[0.9.4]: https://github.com/igraph/python-igraph/compare/0.9.1...0.9.4
[0.9.1]: https://github.com/igraph/python-igraph/compare/0.9.0...0.9.1
[0.9.0]: https://github.com/igraph/python-igraph/compare/0.8.5...0.9.0
[0.8.3]: https://github.com/igraph/python-igraph/releases/tag/0.8.3
