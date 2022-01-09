import igraph as ig
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize
import random

def plot_betweenness(g, ax):
    
    # Calculate vertex betweenness and scale it to be between 0.0 and 1.0
    vertex_betweenness = g.betweenness()
    edge_betweenness = g.edge_betweenness()
    scaled_vertex_betweenness = ig.rescale(vertex_betweenness, clamp=True)
    scaled_edge_betweenness = ig.rescale(edge_betweenness, clamp=True)
    print(f"vertices: {min(vertex_betweenness)} - {max(vertex_betweenness)}")
    print(f"edges: {min(edge_betweenness)} - {max(edge_betweenness)}")

    # Define color bars
    cmap1 = LinearSegmentedColormap.from_list("vertex_cmap", ["pink", "indigo"])
    cmap2 = LinearSegmentedColormap.from_list("edge_cmap", ["lightblue", "midnightblue"])

    norm1 = Normalize()
    norm1.autoscale(vertex_betweenness)
    norm2 = Normalize()
    norm2.autoscale(edge_betweenness)

    plt.colorbar(ScalarMappable(norm=norm1, cmap=cmap1), ax=ax)
    plt.colorbar(ScalarMappable(norm=norm2, cmap=cmap2), ax=ax)

    # Plot graph
    g.vs["color"] = [cmap1(betweenness) for betweenness in scaled_vertex_betweenness]
    g.vs["size"]  = ig.rescale(vertex_betweenness, (0.1, 0.5))
    g.es["color"] = [cmap2(betweenness) for betweenness in scaled_edge_betweenness]
    g.es["width"] = ig.rescale(edge_betweenness, (0.5, 1.0))

    ig.plot(
        g, 
        target=ax, 
        layout="fruchterman_reingold",
        vertex_frame_width=0.2,
    )

# Generate Krackhardt Kite Graphs and Watts Strogatz graphs
random.seed(0)
g1 = ig.Graph.Famous("Krackhardt_Kite")
g2 = ig.Graph.Watts_Strogatz(dim=1, size=150, nei=2, p=0.1)

# Plot the graph
fig, axs = plt.subplots(1, 2, figsize=(10, 5))
plot_betweenness(g1, axs[0])
plot_betweenness(g2, axs[1])

# Add "a" and "b" labels for panels
fig.text(0.05, 0.9, 'a', va='top')
fig.text(0.55, 0.9, 'b', va='top')

plt.show()
