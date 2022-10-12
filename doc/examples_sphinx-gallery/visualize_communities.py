"""
.. _tutorials-visualize-communities:

=====================
Communities
=====================

This example shows how to visualize communities or clusters of a graph. First, make the graph: we just use a famous graph here for simplicity.
"""
import igraph as ig
import matplotlib.pyplot as plt

g = ig.Graph.Famous("Zachary")

# Use edge betweenness to detect communities
# and covert into a VertexClustering
communities = g.community_edge_betweenness()
communities = communities.as_clustering()

# Color each vertex and edge based on its community membership
num_communities = len(communities)
palette = ig.RainbowPalette(n=num_communities)
for i, community in enumerate(communities):
    g.vs[community]["color"] = i
    community_edges = g.es.select(_within=community)
    community_edges["color"] = i


# Plot with only vertex and edge coloring
fig, ax = plt.subplots()
ig.plot(
    communities,
    palette=palette,
    edge_width=1,
    target=ax,
    vertex_size=0.3,
)

# Create a custom color legend
legend_handles = []
for i in range(num_communities):
    handle = ax.scatter(
        [], [],
        s=100,
        facecolor=palette.get(i),
        edgecolor="k",
        label=i,
    )
    legend_handles.append(handle)
ax.legend(
    handles=legend_handles,
    title='Community:',
    bbox_to_anchor=(0, 1.0),
    bbox_transform=ax.transAxes,
)

plt.show()
