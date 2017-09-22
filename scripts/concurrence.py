"""
calculates varuous ditances between two attributes in a graph
of note Attribute Similarities & Jaccard Coefficient which give
unweighted and weighted connection estimations

further work:
try to implement M.E.J. Newman method
thinking about how I might implement wider changes
"""

import numpy as np
import networkx as nx
from matplotlib import pylab
import matplotlib.pyplot as plt
import pandas as pd


def load_graph(graph):
	print('loading graph....')
	G = nx.read_gexf(graph)
	return G

def edge_connections(facet1, facet2):
	# break_no is min no. nodes removed to break all paths source to target
	# maybe this / average or total freq would be interesting
	print('calculating break number....')
	break_no = nx.node_connectivity(G, facet1, facet2)

	print('calculating degrees...')
	degree1 = nx.degree(G, facet1)
	degree2 = nx.degree(G, facet2)
	edge_total = degree1 + degree2
	# what fraction of their partner attributes do they share?
	# similar to Jaccard without weighting
	attribute_sim = (break_no*2)/edge_total

	return (break_no, degree1, degree2, edge_total, attribute_sim)

def weighted_connections(facet1, facet2):

	print('getting edge weight....')
	try:
		edge = G.get_edge_data(facet1,facet2)
		edge_weight = edge.get('Fold_Difference')
	except AttributeError:
		edge_weight = 0

	print('calculating Jaccard coefficient....')
	jc = nx.jaccard_coefficient(G, [(facet1, facet2)])
	jc2 = next(jc)
	jaccard_coefficient = jc2[2]

	return (edge_weight, jaccard_coefficient)


if __name__ == '__main__':


	# test facet pairs:

	facet1 = 'frozenDessertFrequency'
	facet2 = 'frozenDesertFrequency'

	# facet1 = 'latitude'
	# facet2 = 'longitude'

	# facet1 = 'serovar'
	# facet2 = 'sex'

	G = load_graph('fold_diff_weighted_network.gexf')
	# unweighted_edge_calcs = edge_connections(facet1, facet2)
	# weighted_edge_calcs = weighted_connections(facet1, facet2)
	





	# # Temporary Output

	# print('Break No.:', unweighted_edge_calcs[0])
	# print('Degree Total:', unweighted_edge_calcs[3])
	# print(facet1,':', unweighted_edge_calcs[1])
	# print(facet2,':', unweighted_edge_calcs[2])
	# print('Attribute Similarities:', unweighted_edge_calcs[4])
	# print('Jaccard Coefficient:', weighted_edge_calcs[1])
	# print('Edge Weight:', weighted_edge_calcs[0])



	# # Unused

	# print(nx.average_clustering(G)) # on whole graph takes forever
	# see https://networkx.github.io/documentation/networkx-1.10/reference/algorithms.link_prediction.html

	# see popular frequencies in a histogram on whole graph
	# graphs = nx.degree_histogram(G)
	# print(graphs)


















