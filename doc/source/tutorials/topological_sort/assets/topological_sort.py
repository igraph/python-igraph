import igraph as ig

# generate directed acyclic graph
g = ig.Graph(edges=[(0, 1), (0, 2), (1, 3), (2, 4), (4, 3), (3, 5), (4, 5)], 
            directed=True)
assert g.is_dag
    
# topological sorting
results = g.topological_sorting(mode='out')
print('Topological sorting result (out):', *results)

results = g.topological_sorting(mode='in')
print('Topological sorting result (in):', *results)

# print indegree of each node
for i in range(g.vcount()):
    print('degree of {}: {}'.format(i, g.vs[i].indegree()))