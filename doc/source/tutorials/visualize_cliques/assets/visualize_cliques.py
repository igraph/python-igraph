import igraph as ig
import matplotlib.pyplot as plt

g = ig.Graph.Famous('Zachary')

# Compute cliques
cliques = g.cliques(4, 4)

# Plot each clique highlighted in a separate axes
fig, axs = plt.subplots(3, 4)
axs = axs.ravel()
for clique, ax in zip(cliques, axs):
    ig.plot(
        ig.VertexCover(g, [clique]),
        mark_groups=True, palette=ig.RainbowPalette(),
        edge_width=0.5,
        target=ax,
    )

plt.axis('off')
plt.show()
