import numpy as np
from scipy.spatial import Delaunay
import igraph as ig
import matplotlib.pyplot as plt


# Generate a random graph in the 2D unit cube
np.random.seed(0)  # To ensure reproducibility
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

# Plot the triangles
fig, ax = plt.subplots()

palette = ig.GradientPalette("midnightblue", "lightblue", 100)
for tri in delaunay.simplices:
    # get the points of the triangle
    tri_points = [delaunay.points[tri[i]] for i in range(3)]

    # calculate the vertical center of the triangle
    center = (tri_points[0][1] + tri_points[1][1] + tri_points[2][1]) / 3

    # draw triangle onto axes
    poly = plt.Polygon(tri_points, color=palette.get(int(center * 100)))
    ax.add_patch(poly)

# Plot the graph on top
ig.plot(
    g,
    target=ax,
    vertex_size=0.0,
    edge_width=0.2,
    edge_color="white",
)
plt.show()
