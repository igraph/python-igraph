"""
.. _tutorials-stochastic-variability:

=========================================================
Stochastic Variability in Community Detection Algorithms
=========================================================

This example demonstrates the use of stochastic community detection methods to check whether a network possesses a strong community structure, and whether the partitionings we obtain are meaningul. Many community detection algorithms are randomized, and return somewhat different results after each run, depending on the random seed that was set. When there is a robust community structure, we expect these results to be similar to each other. When the community structure is weak or non-existent, the results may be noisy and highly variable. We will employ several partion similarity measures to analyse the consistency of the results, including the normalized mutual information (NMI), the variation of information (VI), and the Rand index (RI).

"""

# %%
import igraph as ig
import matplotlib.pyplot as plt
import itertools
import random

# %%
# .. note::
#   We set a random seed to ensure that the results look exactly the same in
#   the gallery. You don't need to do this when exploring randomness.
random.seed(42)

# %%
# We will use Zachary's karate club dataset [1]_, a classic example of a network
# with a strong community structure:
karate = ig.Graph.Famous("Zachary")

# %%
# We will compare it to an an Erdős-Rényi :math:`G(n, m)` random network having
# the same number of vertices and edges. The parameters 'n' and 'm' refer to the
# vertex and edge count, respectively. Since this is a random network, it should
# have no community structure.
random_graph = ig.Graph.Erdos_Renyi(n=karate.vcount(), m=karate.ecount())

# %%
# First, let us plot the two networks for a visual comparison:

# Create subplots
fig, axes = plt.subplots(1, 2, figsize=(12, 6), subplot_kw={"aspect": "equal"})

# Karate club network
ig.plot(
    karate,
    target=axes[0],
    vertex_color="lightblue",
    vertex_size=30,
    vertex_label=range(karate.vcount()),
    vertex_label_size=10,
    edge_width=1,
)
axes[0].set_title("Karate club network")

# Random network
ig.plot(
    random_graph,
    target=axes[1],
    vertex_color="lightcoral",
    vertex_size=30,
    vertex_label=range(random_graph.vcount()),
    vertex_label_size=10,
    edge_width=1,
)
axes[1].set_title("Erdős-Rényi random network")

plt.show()


# %%
# Function to compute similarity between partitions using various methods:
def compute_pairwise_similarity(partitions, method):
    similarities = []

    for p1, p2 in itertools.combinations(partitions, 2):
        similarity = ig.compare_communities(p1, p2, method=method)
        similarities.append(similarity)

    return similarities


# %%
# The Leiden method, accessible through :meth:`igraph.Graph.community_leiden()`,
# is a modularity maximization approach for community detection.  Since exact
# modularity maximization is NP-hard, the algorithm employs a greedy heuristic
# that processes vertices in a random order.  This randomness leads to
# variation in the detected communities across different runs, which is why
# results may differ each time the method is applied. The following function
# runs the Leiden algorithm multiple times:
def run_experiment(graph, iterations=100):
    partitions = [
        graph.community_leiden(objective_function="modularity").membership
        for _ in range(iterations)
    ]
    nmi_scores = compute_pairwise_similarity(partitions, method="nmi")
    vi_scores = compute_pairwise_similarity(partitions, method="vi")
    ri_scores = compute_pairwise_similarity(partitions, method="rand")
    return nmi_scores, vi_scores, ri_scores


# %%
# Run the experiment on both networks:
nmi_karate, vi_karate, ri_karate = run_experiment(karate)
nmi_random, vi_random, ri_random = run_experiment(random_graph)

# %%
# Finally, let us plot histograms of the pairwise similarities of the obtained
# partitionings to understand the result:
fig, axes = plt.subplots(2, 3, figsize=(12, 6))
measures = [
    # Normalized Mutual Information (0-1, higher = more similar)
    (nmi_karate, nmi_random, "NMI", 0, 1),
    # Variation of Information (0+, lower = more similar)
    (vi_karate, vi_random, "VI", 0, max(vi_karate + vi_random)),
    # Rand Index (0-1, higher = more similar)
    (ri_karate, ri_random, "RI", 0, 1),
]
colors = ["red", "blue", "green"]

for i, (karate_scores, random_scores, measure, lower, upper) in enumerate(measures):
    # Karate club histogram
    axes[0][i].hist(
        karate_scores,
        bins=20,
        range=(lower, upper),
        density=True,  # Probability density
        alpha=0.7,
        color=colors[i],
        edgecolor="black",
    )
    axes[0][i].set_title(f"{measure} - Karate club network")
    axes[0][i].set_xlabel(f"{measure} score")
    axes[0][i].set_ylabel("PDF")

    # Random network histogram
    axes[1][i].hist(
        random_scores,
        bins=20,
        range=(lower, upper),
        density=True,
        alpha=0.7,
        color=colors[i],
        edgecolor="black",
    )
    axes[1][i].set_title(f"{measure} - Random network")
    axes[1][i].set_xlabel(f"{measure} score")
    axes[0][i].set_ylabel("PDF")

plt.tight_layout()
plt.show()

# %%
# We have compared the pairwise similarities using the NMI, VI, and RI measures
# between partitonings obtained for the karate club network (strong community
# structure) and a comparable random graph (which lacks communities).
#
# The Normalized Mutual Information (NMI) and Rand Index (RI) both quantify
# similarity, and take values from :math:`[0,1]`. Higher values indicate more
# similar partitionings, with a value of 1 attained when the partitionings are
# identical.
#
# The Variation of Information (VI) is a distance measure. It takes values from
# :math:`[0,\infty]`, with lower values indicating higher similarities. Identical
# partitionings have a distance of zero.
#
# For the karate club network, NMI and RI value are concentrated near 1, while
# VI is concentrated near 0, suggesting a robust community structure. In contrast
# the values obtained for the random network are much more spread out, showing
# inconsistent partitionings due to the lack of a clear community structure.

# %%
# .. [1] W. Zachary: "An Information Flow Model for Conflict and Fission in Small Groups". Journal of Anthropological Research 33, no. 4 (1977): 452–73. https://www.jstor.org/stable/3629752
