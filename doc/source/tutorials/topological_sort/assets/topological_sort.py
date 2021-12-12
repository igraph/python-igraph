import igraph as ig

# generate a directed acyclic graph (DAG)
g = ig.Graph(edges=[(0, 1), (0, 2), (1, 3), (2, 4), (4, 3), (3, 5), (4, 5)], 
            directed=True)
assert g.is_dag
    
# g.topological_sorting() returns a list of node IDs.
# If the given graph is not DAG, the error will occur.
results = g.topological_sorting(mode='out')
print('Topological sort of graph g (out):', *results)

results = g.topological_sorting(mode='in')
print('Topological sort of graph g (in):', *results)

# g.vs[i].indegree() returns the indegree of the node (which is g.vs[i]).
for i in range(g.vcount()):
    print('degree of {}: {}'.format(i, g.vs[i].indegree()))