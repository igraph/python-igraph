import igraph as ig
import matplotlib.pyplot as plt
import random

# Set a random seed for reproducibility
random.seed(0)

# Generate two Erdos Renyi graphs based on probability
g1 = ig.Graph.Erdos_Renyi(n=15, p=0.2, directed=False, loops=False)
g2 = ig.Graph.Erdos_Renyi(n=15, p=0.2, directed=False, loops=False)

# Generate two Erdos Renyi graphs based on number of edges
g3 = ig.Graph.Erdos_Renyi(n=20, m=35, directed=False, loops=False)
g4 = ig.Graph.Erdos_Renyi(n=20, m=35, directed=False, loops=False)

# Print out summaries of each graph
ig.summary(g1)
ig.summary(g2)
ig.summary(g3)
ig.summary(g4)

fig, axs = plt.subplots(1, 2, figsize=(10, 5))
ig.plot(
    g1,
    target=axs[0],
    layout="circle",
    vertex_color="lightblue"
)
ig.plot(
    g2,
    target=axs[1],
    layout="circle",
    vertex_color="lightblue"
)
plt.show()

fig, axs = plt.subplots(1, 2, figsize=(10, 5))
ig.plot(
    g3,
    target=axs[0],
    layout="circle",
    vertex_color="lightblue",
    vertex_size=0.15
)
ig.plot(
    g4,
    target=axs[1],
    layout="circle",
    vertex_color="lightblue",
    vertex_size=0.15
)
plt.show()

# IGRAPH U--- 15 18 -- 
# IGRAPH U--- 15 21 -- 
# IGRAPH U--- 20 35 -- 
# IGRAPH U--- 20 35 -- 
