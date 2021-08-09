# igraph Python interface changelog

## [Unreleased]

### Changed

- Improved performance of `Graph.DataFrame()`, thanks to
  [@fwitter](https://github.com/user/fwitter). See PR
  [#418](https://github.com/igraph/python-igraph/pull/418) for more details.

### Removed

- Removed deprecated `UbiGraphDrawer`.

- Removed deprecated `show()` method of `Plot` instances as well as the feature
  that automatically shows the plot when `plot()` is called with no target.

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

[unreleased]: https://github.com/igraph/python-igraph/compare/0.9.6..HEAD
[0.9.6]: https://github.com/igraph/python-igraph/compare/0.9.5...0.9.6
[0.9.5]: https://github.com/igraph/python-igraph/compare/0.9.4...0.9.5
[0.9.4]: https://github.com/igraph/python-igraph/compare/0.9.1...0.9.4
[0.9.1]: https://github.com/igraph/python-igraph/compare/0.9.0...0.9.1
[0.9.0]: https://github.com/igraph/python-igraph/compare/0.8.5...0.9.0
[0.8.3]: https://github.com/igraph/python-igraph/releases/tag/0.8.3
