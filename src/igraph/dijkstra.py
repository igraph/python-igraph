import sys


def closest_neighbor(graph, weights, from_vertex):
	min_dist = sys.maxint
	for v in range(len(graph.vs[from_vertex])):
		dist = weights[from_vertex][graph.vs[from_vertex][v]]
		if (dist < min_dist):
			min_dist = dist
	
	return min_dist


def igraph_shortest_path_dijkstra(graph, from_vertex, weights):
	no_of_nodes = graph.vcount()
	no_of_edges = graph.ecount()
	
	if (len(weights) != no_of_edges):
		raise ValueError("Weight vector length does not match")
	
	if (no_of_edges > 0):
		min_weight = weights.min()
		if (min_weight < 0):
			raise ValueError("Weight vector must be non-negative")
		elif (min_weight == None):
			raise ValueError("Weight vector must not contain NaN values")
	
	dist = [sys.maxint] * no_of_nodes
	dist[from_vertex] = 0
	short_path_included = [0] * no_of_nodes
	
	for v in range(no_of_nodes):
		neighbor = closest_neighbor(graph, weights, from_vertex)
		
		short_path_included[neighbor] = True
		
		for vertex in range(no_of_nodes):
			if weights[neighbor][vertex] > 0 and not short_path_included[vertex]:
				if dist[vertex] > dist[neighbor] + weights[neighbor][vertex]:
					dist[vertex] = dist[neighbor] + weights[neighbor][vertex]
				
	return dist
	