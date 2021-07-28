import matplotlib.pyplot as plt
from igraph import Graph, plot


g = Graph([
    (0, 1), (0, 2), (2, 3), (3, 4), (4, 2), (2, 5), (5, 0), (6, 3), (5, 6),
    ])
g.vs["name"] = [
        "Alice", "Bob", "Claire", "Dennis", "Esther", "Frank", "George",
        ]
g.vs["age"] = [25, 31, 18, 47, 22, 23, 50]
g.vs["gender"] = ["f", "m", "f", "m", "f", "m", "m"]
g.es["is_formal"] = [False, False, True, True, True, False, True, False, False]

# Compute layout
layout = g.layout("kk")

# Simple plot
fig, ax = plt.subplots()
plot(g, layout=layout, target=ax)


# Add labels and colors
g.vs["label"] = g.vs["name"]
color_dict = {"m": "blue", "f": "pink"}
g.vs["color"] = [color_dict[gender] for gender in g.vs["gender"]]

fig, ax = plt.subplots()
plot(g, layout=layout, target=ax)
