import igraph as ig 
import os


nodes = [
    "Pennsylvania State", "Northwestern", "Ohio State", "Minnesota",
    "Michigan", "Iowa", "Wisconsin", "Illinois", "Michigan State",
    "Purdue", "Indiana"
]

edges = [
    ("Pennsylvania State", "Northwestern"), 
    ("Pennsylvania State", "Minnesota"), 
    ("Pennsylvania State", "Illinois"), 
    ("Pennsylvania State", "Purdue"), 
    ("Pennsylvania State", "Michigan State"), 
    ("Pennsylvania State", "Wisconsin"), 
    ("Pennsylvania State", "Ohio State"), 
    
    ("Northwestern", "Illinois"),
    ("Northwestern", "Purdue"),
    ("Northwestern", "Iowa"),
    ("Northwestern", "Michigan State"),
    ("Northwestern", "Wisconsin"),
    
    ("Minnesota", "Purdue"),
    ("Minnesota", "Indiana"),
    ("Minnesota", "Michigan"),
    ("Minnesota", "Michigan State"),

    ("Iowa", "Minnesota"), 
    ("Iowa", "Illinois"), 
    ("Iowa", "Purdue"),
    ("Iowa", "Indiana"),
    ("Iowa", "Wisconsin"),

    ("Ohio State", "Iowa"),
    ("Ohio State", "Illinois"),
    ("Ohio State", "Michigan"),
    ("Ohio State", "Michigan State"),
    ("Ohio State", "Indiana"),
    ("Ohio State", "Northwestern"),
    ("Ohio State", "Minnesota"),

    ("Michigan", "Iowa"),
    ("Michigan", "Michigan State"),
    ("Michigan", "Indiana"),
    ("Michigan", "Pennsylvania State"),
    ("Michigan", "Northwestern"),

    ("Wisconsin", "Indiana"),
    ("Wisconsin", "Illinois"),
    ("Wisconsin", "Purdue"),
    ("Wisconsin", "Michigan"),
    ("Wisconsin", "Minnesota"),
    
    ("Purdue", "Illinois"),
    ("Purdue", "Indiana"),
    ("Purdue", "Michigan State"),

    ("Michigan State", "Indiana"),
    ("Michigan State", "Illinois"),

    ("Indiana", "Illinois")
]

g = ig.Graph.TupleList(edges, directed=True)

# Assign node names and community attributes
g.vs["name"] = nodes


local_path = "football/football.gml"
script_dir = os.path.dirname(os.path.abspath(__file__))
full_local_path = os.path.join(script_dir, local_path)
g.write_gml(full_local_path)