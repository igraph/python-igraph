# igraph Python interface changelog

## [Unreleased]

### Added

* `Graph.DataFrame` now has a `use_vids=...` keyword argument that decides whether
  the data frame contains vertex IDs (`True`) or vertex names (`False`). (PR #348)

* Added `MatplotlibGraphDrawer` to draw a graph on an existing Matplotlib
  figure. (PR #341)

* Added a code path to choose between preferred image viewers on FreeBSD. (PR #354)

* Added `Graph.harmonic_centrality()` that wraps `igraph_harmonic_centrality()`
  from the underlying C library.

### Changed

* `python-igraph` is now compatible with `igraph` 0.9.0.

* The setup script was adapted to the new CMake-based build system of `igraph`.

* Dropped support for older Python versions; the oldest Python version that
  `python-igraph` is tested on is now Python 3.6.

* The default splitting heuristic of the BLISS isomorphism algorithm was changed
  from `IGRAPH_BLISS_FM` (first maximally non-trivially connected non-singleton cell)
  to `IGRAPH_BLISS_FL` (first largest non-singleton cell) as this seems to provide
  better performance on a variety of graph classes. This change is a follow-up
  of the change in the recommended heuristic in the core igraph C library.

### Fixed

* Fixed crashes in the Python-C glue code related to the handling of empty
  vectors in certain attribute merging functions (see issue #358).

* Fixed a memory leak in `Graph.closeness_centrality()` when an invalid `cutoff`
  argument was provided to the function.

* Clarified that the `fixed=...` argument is ineffective for the DrL layout
  because the underlying C code does not handle it. The argument was _not_
  removed for sake of backwards compatibility.

* `VertexSeq.find(name=x)` now works correctly when `x` is an integer; fixes
  #367

### Miscellaneous

* The Python codebase was piped through `black` for consistent formatting.

* Wildcard imports were removed from the codebase.

* CI tests were moved to Github Actions from Travis.

* The core C library is now built with `-fPIC` on Linux to allow linking to the
  Python interface.

## 0.8.3

This is the last released version of `python-igraph` without a changelog file.
Please refer to the commit logs at https://github.com/igraph/python-igraph for
a list of changes affecting versions up to 0.8.3. Notable changes after 0.8.3
are documented above.
