from igraph._igraph import (
    IN,
    OUT,
    arpack_options as default_arpack_options,
)
from igraph.statistics import Histogram


def _indegree(self, *args, **kwds):
    """Returns the in-degrees in a list.

    See L{degree} for possible arguments.
    """
    kwds["mode"] = IN
    return self.degree(*args, **kwds)


def _outdegree(self, *args, **kwds):
    """Returns the out-degrees in a list.

    See L{degree} for possible arguments.
    """
    kwds["mode"] = OUT
    return self.degree(*args, **kwds)


def _degree_distribution(self, bin_width=1, *args, **kwds):
    """Calculates the degree distribution of the graph.

    Unknown keyword arguments are directly passed to L{degree()}.

    @param bin_width: the bin width of the histogram
    @return: a histogram representing the degree distribution of the
      graph.
    """
    result = Histogram(bin_width, self.degree(*args, **kwds))
    return result


def _pagerank(
    self,
    vertices=None,
    directed=True,
    damping=0.85,
    weights=None,
    arpack_options=None,
    implementation="prpack",
    niter=1000,
    eps=0.001,
):
    """Calculates the PageRank values of a graph.

    @param vertices: the indices of the vertices being queried.
      C{None} means all of the vertices.
    @param directed: whether to consider directed paths.
    @param damping: the damping factor. M{1-damping} is the PageRank value
      for nodes with no incoming links. It is also the probability of
      resetting the random walk to a uniform distribution in each step.
    @param weights: edge weights to be used. Can be a sequence or iterable
      or even an edge attribute name.
    @param arpack_options: an L{ARPACKOptions} object used to fine-tune
      the ARPACK eigenvector calculation. If omitted, the module-level
      variable called C{arpack_options} is used. This argument is
      ignored if not the ARPACK implementation is used, see the
      I{implementation} argument.
    @param implementation: which implementation to use to solve the
      PageRank eigenproblem. Possible values are:
        - C{"prpack"}: use the PRPACK library. This is a new
          implementation in igraph 0.7
        - C{"arpack"}: use the ARPACK library. This implementation
          was used from version 0.5, until version 0.7.
        - C{"power"}: use a simple power method. This is the
          implementation that was used before igraph version 0.5.
    @param niter: The number of iterations to use in the power method
      implementation. It is ignored in the other implementations
    @param eps: The power method implementation will consider the
      calculation as complete if the difference of PageRank values between
      iterations change less than this value for every node. It is
      ignored by the other implementations.
    @return: a list with the Google PageRank values of the specified
      vertices."""
    if arpack_options is None:
        arpack_options = default_arpack_options
    return self.personalized_pagerank(
        vertices,
        directed,
        damping,
        None,
        None,
        weights,
        arpack_options,
        implementation,
        niter,
        eps,
    )
