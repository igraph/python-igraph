from igraph import Graph
import warnings

warnings.simplefilter('error', 'Cannot shuffle graph')
degseq = [1,2,2,3]
try:
    testgraph = Graph.Degree_Sequence(degseq,method = "vl")
except RuntimeWarning:
    print(degseq)
else:
    print("go on")
