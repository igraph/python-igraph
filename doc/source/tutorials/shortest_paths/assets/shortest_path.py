import igraph as ig
import matplotlib.pyplot as plt

# Find the shortest path on an unweighted graph
g = ig.Graph(
    6,
    [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5)]
)

# g.get_shortest_paths() returns a list of vertex ID paths
results = g.get_shortest_paths(1, to=4, output="vpath") # results = [[1, 0, 2, 4]]

if len(results[0]) > 0:
    # The distance is the number of vertices in the shortest path minus one.
    print("Shortest distance is: ", len(results[0])-1)
else:
    print("End node could not be reached!")

# Find the shortest path on a weighted graph
g.es["weight"] = [2, 1, 5, 4, 7, 3, 2]

# g.get_shortest_paths() returns a list of edge ID paths
results = g.get_shortest_paths(0, to=5, weights=g.es["weight"], output="epath") # results = [[1, 3, 5]]

if len(results[0]) > 0:
    # Add up the weights across all edges on the shortest path
    distance = sum(g.es[e]["weight"] for e in results[0])
    print("Shortest weighted distance is: ", distance)
else:
    print("End node could not be reached!")

# Output:
# Shortest distance is:  3
# Shortest weighted distance is:  8   
