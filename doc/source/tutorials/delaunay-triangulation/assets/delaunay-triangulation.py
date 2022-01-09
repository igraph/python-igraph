import numpy as np
from scipy.spatial import Delaunay
import igraph as ig
import matplotlib.pyplot as plt


# Generate a random graph in the 2D unit cube
np.random.seed(0) # To ensure reproducibility
x, y = np.random.rand(2, 30)
g = ig.Graph(30)
g.vs['x'] = x
g.vs['y'] = y

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
