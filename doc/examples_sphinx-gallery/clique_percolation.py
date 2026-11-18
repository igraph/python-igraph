"""
==================
Clique percolation
==================

Find overlapping communities by joining triangles that share an edge.
"""

from itertools import combinations

import igraph as ig
import matplotlib.pyplot as plt

# %%
# Each pair of adjacent triangles shares an edge. The left and right pairs
# share only vertex C, which can belong to both communities.
g = ig.Graph.TupleList([
    ("A", "B"), ("A", "C"), ("B", "C"), ("B", "D"), ("C", "D"),
    ("C", "E"), ("C", "F"), ("E", "F"), ("E", "G"), ("F", "G"),
])

# %%
# Make a graph with one vertex per triangle and an edge between triangles
# that share two vertices. Each connected component gives one community.
triangles = [set(clique) for clique in g.cliques(min=3, max=3)]
adjacent = [
    (i, j)
    for i, j in combinations(range(len(triangles)), 2)
    if len(triangles[i] & triangles[j]) == 2
]
triangle_graph = ig.Graph(n=len(triangles), edges=adjacent)
communities = [
    sorted(set().union(*(triangles[i] for i in component)))
    for component in triangle_graph.connected_components()
]

# %%
# Plot the communities on the original graph using a vertex cover, which
# allows C to appear in both highlighted groups.
layout = [(-2, 0), (-1, 1), (0, 0), (-1, -1), (1, 1), (1, -1), (2, 0)]
fig, ax = plt.subplots(figsize=(6, 3))
ig.plot(
    ig.VertexCover(g, communities),
    target=ax,
    layout=layout,
    mark_groups=True,
    palette=ig.PrecalculatedPalette(["#5794c6", "#dd9748"]),
    vertex_color="white",
    vertex_frame_color="#344054",
    vertex_size=30,
    vertex_label=g.vs["name"],
)
ax.set_axis_off()
plt.show()
