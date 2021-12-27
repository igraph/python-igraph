import igraph as ig
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# User data (usually would come with time stamp)
action_dataframe = pd.DataFrame([
    ['dsj3239asadsa3', 'createPage', 'greatProject'],
    ['2r09ej221sk2k5', 'editPage', 'greatProject'],
    ['dsj3239asadsa3', 'editPage', 'greatProject'],
    ['789dsadafj32jj', 'editPage', 'greatProject'],
    ['oi32ncwosap399', 'editPage', 'greatProject'],
    ['4r4320dkqpdokk', 'createPage', 'miniProject'],
    ['320eljl3lk3239', 'editPage', 'miniProject'],
    ['dsj3239asadsa3', 'editPage', 'miniProject'],
    ['3203ejew332323', 'createPage', 'private'],
    ['3203ejew332323', 'editPage', 'private'],
    ['40m11919332msa', 'createPage', 'private2'],
    ['40m11919332msa', 'editPage', 'private2'],
    ['dsj3239asadsa3', 'createPage', 'anotherGreatProject'],
    ['2r09ej221sk2k5', 'editPage', 'anotherGreatProject'],
    ],
    columns=['userid', 'action', 'project'],
)

# Make a graph with vertices as users, and edges connecting two users who
# worked on the same project
users = action_dataframe['userid'].unique()
adjacency_matrix = pd.DataFrame(
    np.zeros((len(users), len(users)), np.int32),
    index=users,
    columns=users,
)
for project, project_data in action_dataframe.groupby('project'):
    project_users = project_data['userid'].values
    for i1, user1 in enumerate(project_users):
        for user2 in project_users[:i1]:
            adjacency_matrix.at[user1, user2] += 1

g = ig.Graph.Weighted_Adjacency(adjacency_matrix, mode='plus')

# Plot the graph
# Make a layout first
layout = g.layout('circle')

# Make vertex size based on their closeness to other vertices
vertex_size = g.closeness()
vertex_size = [0.5 * v**2 if not np.isnan(v) else 0.05 for v in vertex_size]

# Make mpl axes
fig, ax = plt.subplots()

# Plot graph in that axes
ig.plot(
    g,
    target=ax,
    layout=layout,
    vertex_label=g.vs['name'],
    vertex_color="lightblue",
    vertex_size=vertex_size,
    edge_width=g.es["weight"],
)
plt.show()
