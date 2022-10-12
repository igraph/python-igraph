"""
.. _tutorials-topological-sort:

===================
Topological sorting
===================

This example demonstrates how to get a topological sorting on a directed acyclic graph (DAG). A topological sorting of a directed graph is a linear ordering based on the precedence implied by the directed edges. It exists iff the graph doesn't have any cycle. In ``igraph``, we can use :meth:`igraph.GraphBase.topological_sorting` to get a topological ordering of the vertices.

"""
import igraph as ig
import matplotlib.pyplot as plt


# generate a directed acyclic graph (DAG)
g = ig.Graph(
    edges=[(0, 1), (0, 2), (1, 3), (2, 4), (4, 3), (3, 5), (4, 5)], 
    directed=True,
)
assert g.is_dag
    
# g.topological_sorting() returns a list of node IDs.
# If the given graph is not DAG, the error will occur.
results = g.topological_sorting(mode='out')
print('Topological sort of g (out):', *results)

results = g.topological_sorting(mode='in')
print('Topological sort of g (in):', *results)

# g.vs[i].indegree() returns the indegree of the node.
for i in range(g.vcount()):
    print('degree of {}: {}'.format(i, g.vs[i].indegree()))

# visualization
with plt.xkcd():
    fig, ax = plt.subplots(figsize=(5, 5))
    ig.plot(
            g,
            target=ax,
            layout='kk',
            vertex_size=0.3,
            edge_width=4,
            vertex_label=range(g.vcount()),
            vertex_color="white",
        )
