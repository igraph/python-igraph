import igraph as ig
import matplotlib.pyplot as plt
import random
from scipy.spatial import Delaunay

# Generate a random geometric graph
random.seed(0)
g = ig.Graph.GRG(30, 0)

# Calculate the delaunay triangulation, and add the edges into the original graph
coords = g.layout_auto().coords
delaunay = Delaunay(coords)
for tri in delaunay.simplices:
    g.add_edges([
        (tri[0], tri[1]), 
        (tri[1], tri[2]), 
        (tri[0], tri[2]),
    ])
g.simplify()

# Plot the graph
fig, ax = plt.subplots()
ig.plot(
    g,
    target=ax,
    vertex_size=0.04,
    vertex_color="lightblue",
    edge_width=0.8
)
plt.show()
