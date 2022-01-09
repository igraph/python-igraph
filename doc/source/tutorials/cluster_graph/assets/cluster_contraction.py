import igraph as ig
import matplotlib.pyplot as plt

# Load the graph
g = ig.load("./lesmis/lesmis.gml")

# Generate communities
communities = g.community_edge_betweenness()
communities = communities.as_clustering() # Convert into a VertexClustering for plotting

# Print them out
for i, community in enumerate(communities):
    print(f"Community {i}:")
    for v in community:
        print(f"\t{g.vs[v]['label']}")

# Set community colors
num_communities = len(communities)
palette1 = ig.RainbowPalette(n=num_communities)
for i, community in enumerate(communities):
    g.vs[community]["color"] = i
    community_edges = g.es.select(_within=community)
    community_edges["color"] = i

g.vs["label"] = ["\n\n" + label for label in g.vs["label"]] # Move the labels below the vertices

# Plot the communities
fig1, ax1 = plt.subplots()
ig.plot(
    communities, 
    target=ax1,
    mark_groups=True,
    palette=palette1,
    vertex_size=0.1,
    edge_width=0.5,
)
fig1.set_size_inches(20, 20)
fig1.savefig("../figures/communities.png", dpi=200)

# Assign x, y, and sizes for each node
layout = g.layout_kamada_kawai()
g.vs["x"], g.vs["y"] = list(zip(*layout))
g.vs["size"] = 1
g.es["size"] = 1

# Generate cluster graph
cluster_graph = communities.cluster_graph(
    combine_vertices={
        "x": "mean", 
        "y": "mean",
        "color": "first",
        "size": "sum",
    },
    combine_edges={
        "size": "sum",
    },
)

# Plot the cluster graph
palette2 = ig.GradientPalette("gainsboro", "black")
g.es["color"] = [palette2.get(int(i)) for i in ig.rescale(cluster_graph.es["size"], (0, 255), clamp=True)]

fig2, ax2 = plt.subplots()
ig.plot(
    cluster_graph, 
    target=ax2,
    palette=palette1,
    # set a minimum size on vertex_size, otherwise vertices are too small
    vertex_size=[max(0.2, size / 20) for size in cluster_graph.vs["size"]], 
    edge_color=g.es["color"],
    edge_width=0.8,
)

# Add a legend
legend_handles = []
for i in range(num_communities):
    handle = ax2.scatter(
        [], [],
        s=100,
        facecolor=palette1.get(i),
        edgecolor="k",
        label=i,
    )
    legend_handles.append(handle)

ax2.legend(
    handles=legend_handles,
    title='Community:',
    bbox_to_anchor=(0, 1.0),
    bbox_transform=ax2.transAxes,
)

fig2.set_size_inches(10, 10)
fig2.savefig("../figures/cluster_graph.png", dpi=150)
