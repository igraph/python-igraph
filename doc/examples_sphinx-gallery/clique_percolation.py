"""
.. _tutorials-clique-percolation:

==========================
Clique Percolation Method
==========================

This example shows how to detect **overlapping communities** using the
Clique Percolation Method (CPM). Unlike partitioning algorithms, CPM allows
a node to belong to more than one community simultaneously.
"""

import itertools
from collections import Counter

import igraph as ig
import matplotlib.pyplot as plt

# %%
# We construct a graph with three dense cliques that share individual nodes,
# creating natural *overlapping* community boundaries:
g = ig.Graph(9)
g.add_edges(list(itertools.combinations([0, 1, 2, 3], 2)))  # clique A
g.add_edges(list(itertools.combinations([3, 4, 5, 6], 2)))  # clique B, shares node 3 with A
g.add_edges(list(itertools.combinations([6, 7, 8], 2)))     # clique C, shares node 6 with B

# %%
# The CPM algorithm works in three steps:
#
# 1. Find all k-cliques (complete subgraphs of exactly k nodes).
# 2. Build a clique graph : two k-cliques are adjacent when they share k-1 nodes.
# 3. Each connected component of the clique graph is a community — the union
#    of all its k-cliques. A node shared between cliques in *different*
#    components belongs to multiple communities simultaneously.
k = 3
cliques = [set(c) for c in g.cliques(k, k)]

clique_graph = ig.Graph(len(cliques))
clique_graph.add_edges([
    (i, j)
    for i, j in itertools.combinations(range(len(cliques)), 2)
    if len(cliques[i] & cliques[j]) >= k - 1
])

communities = []
for component in clique_graph.connected_components():
    members = set()
    for idx in component:
        members |= cliques[idx]
    communities.append(sorted(members))

# %%
# Nodes that appear in more than one community are *overlapping nodes*:
overlap = [
    v for v, count in Counter(v for comm in communities for v in comm).items()
    if count > 1
]
print(f"Communities (k={k}): {communities}")
print(f"Overlapping nodes:   {overlap}")

# %%
# We visualize the result using :class:`igraph.VertexCover`, which draws a
# shaded hull around each community and handles overlapping nodes naturally:
cover = ig.VertexCover(g, communities)
palette = ig.RainbowPalette(n=len(communities))

fig, ax = plt.subplots(figsize=(6, 5))
ig.plot(
    cover,
    mark_groups=True,
    palette=palette,
    vertex_size=25,
    vertex_label=list(range(g.vcount())),
    vertex_label_size=10,
    edge_width=1.5,
    target=ax,
)
ax.set_title(
    f"Clique Percolation Method (k={k})\n"
    f"{len(communities)} communities  —  overlapping nodes: {overlap}"
)
plt.show()

# %%
# Advanced: effect of k
# ----------------------
# Raising k to 4 requires larger cliques. The 3-clique {6, 7, 8} no longer
# qualifies, so community C disappears and node 6 is no longer in any community:
k = 4
cliques_4 = [set(c) for c in g.cliques(k, k)]

clique_graph_4 = ig.Graph(len(cliques_4))
clique_graph_4.add_edges([
    (i, j)
    for i, j in itertools.combinations(range(len(cliques_4)), 2)
    if len(cliques_4[i] & cliques_4[j]) >= k - 1
])

communities_4 = []
for component in clique_graph_4.connected_components():
    members = set()
    for idx in component:
        members |= cliques_4[idx]
    communities_4.append(sorted(members))

print(f"Communities (k=4): {communities_4}")

cover_4 = ig.VertexCover(g, communities_4)
palette_4 = ig.RainbowPalette(n=max(len(communities_4), 1))

fig, ax = plt.subplots(figsize=(6, 5))
ig.plot(
    cover_4,
    mark_groups=True,
    palette=palette_4,
    vertex_size=25,
    vertex_label=list(range(g.vcount())),
    vertex_label_size=10,
    edge_width=1.5,
    target=ax,
)
ax.set_title(
    f"Clique Percolation Method (k=4)\n"
    f"{len(communities_4)} communities  —  nodes 6, 7, 8 no longer qualify"
)
plt.show()
