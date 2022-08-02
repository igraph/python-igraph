_format_mapping = {
    "ncol": ("Read_Ncol", "write_ncol"),
    "lgl": ("Read_Lgl", "write_lgl"),
    "graphdb": ("Read_GraphDB", None),
    "graphmlz": ("Read_GraphMLz", "write_graphmlz"),
    "graphml": ("Read_GraphML", "write_graphml"),
    "gml": ("Read_GML", "write_gml"),
    "dot": (None, "write_dot"),
    "graphviz": (None, "write_dot"),
    "net": ("Read_Pajek", "write_pajek"),
    "pajek": ("Read_Pajek", "write_pajek"),
    "dimacs": ("Read_DIMACS", "write_dimacs"),
    "adjacency": ("Read_Adjacency", "write_adjacency"),
    "adj": ("Read_Adjacency", "write_adjacency"),
    "edgelist": ("Read_Edgelist", "write_edgelist"),
    "edge": ("Read_Edgelist", "write_edgelist"),
    "edges": ("Read_Edgelist", "write_edgelist"),
    "pickle": ("Read_Pickle", "write_pickle"),
    "picklez": ("Read_Picklez", "write_picklez"),
    "svg": (None, "write_svg"),
    "gw": (None, "write_leda"),
    "leda": (None, "write_leda"),
    "lgr": (None, "write_leda"),
    "dl": ("Read_DL", None),
}