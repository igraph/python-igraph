import igraph as ig
import matplotlib.pyplot as plt
import random

# Create a random graph
random.seed(0)
g1 = ig.Graph.Erdos_Renyi(n=10, p=0.5)

# Generate complement
g2 = g1.complementer(loops=False)

# Plot graph
fig, axs = plt.subplots(1, 2)
ig.plot(
    g1,
    target=axs[0],
    layout="circle",
    vertex_color="lightblue",
)
ig.plot(
    g2,
    target=axs[1],
    layout="circle",
    vertex_color="lightblue",
)
plt.show()

