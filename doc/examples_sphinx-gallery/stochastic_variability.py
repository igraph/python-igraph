"""
.. _tutorials-stochastic-variability:

=========================================================
Stochastic Variability in Community Detection Algorithms
=========================================================

This example demonstrates the variability of stochastic community detection methods by analyzing the consistency of multiple partitions using similarity measures normalized mutual information (NMI), variation of information (VI), rand index (RI) on both random and structured graphs.

"""
# %%
# Import libraries
import igraph as ig
import matplotlib.pyplot as plt
import itertools

# %%
# First, we generate a graph.
# Load the karate club network
karate = ig.Graph.Famous("Zachary")
  
# %%
#For the random graph, we use an Erdős-Rényi :math:`G(n, m)` model, where 'n' is the number of nodes 
#and 'm' is the number of edges. We set 'm' to match the edge count of the empirical (Karate Club) 
#network to ensure structural similarity in terms of connectivity, making comparisons meaningful.
n_nodes = karate.vcount()
n_edges = karate.ecount()
#Generate an Erdős-Rényi graph with the same number of nodes and edges
random_graph = ig.Graph.Erdos_Renyi(n=n_nodes, m=n_edges)

# %%
# Now, lets plot the graph to visually understand them.

# Create subplots
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# Karate Club Graph
layout_karate = karate.layout("fr")
ig.plot(
    karate, layout=layout_karate, target=axes[0], vertex_size=30, vertex_color="lightblue", edge_width=1,
    vertex_label=[str(v.index) for v in karate.vs], vertex_label_size=10
)
axes[0].set_title("Karate Club Network")

# Erdős-Rényi Graph
layout_random = random_graph.layout("fr")
ig.plot(
    random_graph, layout=layout_random, target=axes[1], vertex_size=30, vertex_color="lightcoral", edge_width=1,
    vertex_label=[str(v.index) for v in random_graph.vs], vertex_label_size=10
)
axes[1].set_title("Erdős-Rényi Random Graph")
# %%
# Function to compute similarity between partitions
def compute_pairwise_similarity(partitions, method):
    similarities = []
    
    for p1, p2 in itertools.combinations(partitions, 2):
        similarity = ig.compare_communities(p1, p2, method=method)
        similarities.append(similarity)
    
    return similarities

# %%
# We have used, stochastic community detection using the Louvain method, iteratively generating partitions and computing similarity metrics to assess stability.
# The Louvain method is a modularity maximization approach for community detection. 
# Since exact modularity maximization is NP-hard, the algorithm employs a greedy heuristic that processes vertices in a random order. 
# This randomness leads to variations in the detected communities across different runs, which is why results may differ each time the method is applied.
def run_experiment(graph, iterations=50):
    partitions = [graph.community_multilevel().membership for _ in range(iterations)]
    nmi_scores = compute_pairwise_similarity(partitions, method="nmi")
    vi_scores = compute_pairwise_similarity(partitions, method="vi")
    ri_scores = compute_pairwise_similarity(partitions, method="rand")
    return nmi_scores, vi_scores, ri_scores

# %%
# Run experiments
nmi_karate, vi_karate, ri_karate = run_experiment(karate)
nmi_random, vi_random, ri_random = run_experiment(random_graph)

# %%
# Lastly, lets plot probability density histograms to understand the result.
fig, axes = plt.subplots(3, 2, figsize=(12, 10))
measures = [
    (nmi_karate, nmi_random, "NMI", 0, 1),  # Normalized Mutual Information (0-1, higher = more similar)
    (vi_karate, vi_random, "VI", 0, None),  # Variation of Information (0+, lower = more similar)
    (ri_karate, ri_random, "RI", 0, 1),  # Rand Index (0-1, higher = more similar)
]
colors = ["red", "blue", "green"]

for i, (karate_scores, random_scores, measure, lower, upper) in enumerate(measures):
    # Karate Club histogram
    axes[i][0].hist(
        karate_scores, bins=20, alpha=0.7, color=colors[i], edgecolor="black",
        density=True  # Probability density
    )
    axes[i][0].set_title(f"Probability Density of {measure} - Karate Club Network")
    axes[i][0].set_xlabel(f"{measure} Score")
    axes[i][0].set_ylabel("Density")
    axes[i][0].set_xlim(lower, upper)  # Set axis limits explicitly

    # Erdős-Rényi Graph histogram
    axes[i][1].hist(
        random_scores, bins=20, alpha=0.7, color=colors[i], edgecolor="black",
        density=True
    )
    axes[i][1].set_title(f"Probability Density of {measure} - Erdős-Rényi Graph")
    axes[i][1].set_xlabel(f"{measure} Score")
    axes[i][1].set_xlim(lower, upper)  # Set axis limits explicitly

plt.tight_layout()
plt.show()

# %%
# We have compared the probability density of NMI, VI, and RI for the Karate Club network (structured) and an Erdős-Rényi random graph.
#
# **NMI (Normalized Mutual Information):**
# 
# - Karate Club Network: The distribution is concentrated near 1, indicating high similarity across multiple runs, suggesting stable community detection.
# - Erdős-Rényi Graph: The values are more spread out, with lower NMI scores, showing inconsistent partitions due to the lack of clear community structures.
#
# **VI (Variation of Information):**
#
# - Karate Club Network: The values are low and clustered, indicating stable partitioning with minor variations across runs.
# - Erdős-Rényi Graph: The distribution is broader and shifted toward higher VI values, meaning higher partition variability and less consistency.
#
# **RI (Rand Index):**
#
# - Karate Club Network: The RI values are high and concentrated near 1, suggesting consistent clustering results across multiple iterations.
# - Erdős-Rényi Graph: The distribution is more spread out, but with lower RI values, confirming unstable community detection.
#
# **Conclusion**
# 
# The Karate Club Network exhibits strong, well-defined community structures, leading to consistent results across runs.  
# The Erdős-Rényi Graph, being random, lacks clear communities, causing high variability in detected partitions.