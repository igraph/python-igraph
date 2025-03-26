"""
.. _tutorials-stochastic-variability:

=========================================================
Stochastic Variability in Community Detection Algorithms
=========================================================

This example demonstrates the variability of stochastic community detection methods by analyzing the consistency of multiple partitions using similarity measures (NMI, VI, RI) on both random and structured graphs.

"""
# %%
# Import Libraries
import igraph as ig
import numpy as np
import matplotlib.pyplot as plt
import itertools

# %%
# First, we generate a graph.
# Generates a random Erdos-Renyi graph (no clear community structure)
def generate_random_graph(n, p):
    return ig.Graph.Erdos_Renyi(n=n, p=p)
  
# %%
# Generates a clustered graph with clear communities using the Stochastic Block Model (SBM)
def generate_clustered_graph(n, clusters, intra_p, inter_p):
    block_sizes = [n // clusters] * clusters
    prob_matrix = [[intra_p if i == j else inter_p for j in range(clusters)] for i in range(clusters)]
    return ig.Graph.SBM(sum(block_sizes), prob_matrix, block_sizes)

# %%
# Computes pairwise similarity (NMI, VI, RI) between partitions
def compute_pairwise_similarity(partitions, method):
    """Computes pairwise similarity measure between partitions."""
    scores = []
    for p1, p2 in itertools.combinations(partitions, 2):
        scores.append(ig.compare_communities(p1, p2, method=method))
    return scores

# %%
# Stochastic Community Detection
# Runs Louvain's method iteratively to generate partitions
# Computes similarity metrics: 
def run_experiment(graph, iterations=50):
    """Runs the stochastic method multiple times and collects community partitions."""
    partitions = [graph.community_multilevel().membership for _ in range(iterations)]
    nmi_scores = compute_pairwise_similarity(partitions, method="nmi")
    vi_scores = compute_pairwise_similarity(partitions, method="vi")
    ri_scores = compute_pairwise_similarity(partitions, method="rand")
    return nmi_scores, vi_scores, ri_scores

# %%
# Parameters
n_nodes = 100
p_random = 0.05
clusters = 4
p_intra = 0.3  # High intra-cluster connection probability
p_inter = 0.01  # Low inter-cluster connection probability

# %%
# Generate graphs
random_graph = generate_random_graph(n_nodes, p_random)
clustered_graph = generate_clustered_graph(n_nodes, clusters, p_intra, p_inter)

# %%
# Run experiments
nmi_random, vi_random, ri_random = run_experiment(random_graph)
nmi_clustered, vi_clustered, ri_clustered = run_experiment(clustered_graph)

# %% 
# Lets, plot the histograms
fig, axes = plt.subplots(3, 2, figsize=(12, 10))
measures = [(nmi_random, nmi_clustered, "NMI"), (vi_random, vi_clustered, "VI"), (ri_random, ri_clustered, "RI")]
colors = ["red", "blue", "green"]

for i, (random_scores, clustered_scores, measure) in enumerate(measures):
    axes[i][0].hist(random_scores, bins=20, alpha=0.7, color=colors[i], edgecolor="black")
    axes[i][0].set_title(f"Histogram of {measure} - Random Graph")
    axes[i][0].set_xlabel(f"{measure} Score")
    axes[i][0].set_ylabel("Frequency")
    
    axes[i][1].hist(clustered_scores, bins=20, alpha=0.7, color=colors[i], edgecolor="black")
    axes[i][1].set_title(f"Histogram of {measure} - Clustered Graph")
    axes[i][1].set_xlabel(f"{measure} Score")

plt.tight_layout()
plt.show()

# %%
# The results are plotted as histograms for random vs. clustered graphs, highlighting differences in detected community structures.
#The key reason for the inconsistency in random graphs and higher consistency in structured graphs is due to community structure strength:
#Random Graphs: Lack clear communities, leading to unstable partitions. Stochastic algorithms detect different structures across runs, resulting in low NMI, high VI, and inconsistent RI.
#Structured Graphs: Have well-defined communities, so detected partitions are more stable across multiple runs, leading to high NMI, low VI, and stable RI.


# %%
