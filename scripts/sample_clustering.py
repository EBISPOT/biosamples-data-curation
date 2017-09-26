'''
Sample Clustering

build_matrix:
Takes csv a each line of format SampleID, facets1, facet2, facet3...
Converts thins into a dictionary with the SampleID as the key
Defines a dataframe SampleID vs all attributes
Fills the dataframe with binary info based on presence of attribute in sample

affinity_cluster:
Performs affinity propagation clustering

affinity_histo:
plots affinity propagation clusters as sorted histogram

'''

import numpy as np
import pandas as pd
import sys, csv, sklearn
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist
from sklearn.cluster import AffinityPropagation
from scipy.cluster.hierarchy import dendrogram, linkage, cophenet

def build_matrix(facets):

	samples_dict = {}
	unique_facets = []
	unique_samples = []

	print('Generating dictionary for:', facets)
	with open("all.csv",'r') as f_in:


		for line in f_in:
			data_list = line.rstrip().split(',')
			if facets in data_list:
				sample_id = data_list[0]
				data_list.remove(sample_id)			
				#if I need a dict:
				samples_dict[sample_id] = data_list
				for attribute in data_list:
					if attribute not in unique_facets:
						unique_facets.append(attribute)
				if sample_id not in unique_samples:
					unique_samples.append(sample_id)
	print('Found', len(unique_samples), 'unique samples sharing', len(unique_facets), 'attributes.')
	print('Generating', len(unique_samples), 'x', len(unique_facets), 'DataFrame...')
	df = pd.DataFrame(index=unique_samples, columns=unique_facets)

	printcounter = 0
	for s in unique_samples:
		attributes_ = samples_dict.get(s)
		printcounter += 1
		if (printcounter % 500 == 0):
			print('Made it to dataframe row', printcounter,'...')
		for a in unique_facets:
			if a in attributes_:
				df.loc[s,a] = 1
			else:
				df.loc[s,a] = 0

	print('DataFrame generated')
	print('Generating matrix...')
	X = df.as_matrix()
	print('Matrix generated')
	return (df, X)

def affinity_cluster(X):
	# NB X is a np matrix built in 'build_matrix'

	print('Doing Affinity Propagation...')
	af = AffinityPropagation().fit(X)
	# af = AffinityPropagation(preference=0.000000001).fit(X)
	cluster_centers_indices = af.cluster_centers_indices_
	labels = af.labels_
	n_clusters_ = len(cluster_centers_indices)
	print('Affinity Propagation done')
	print('Estimated number of clusters: %d' % n_clusters_)


	return (labels, n_clusters_)

def affinity_histo(df, affinity_clus_result):

	labels = affinity_clus_result[0]
	

	# reorder histogram ascending to decending

	df['labels_'] = labels
	df2 = df.sort_index(by=['labels_'], ascending=[False])
	df2['freq'] = df.groupby('labels_', as_index=False)['labels_'].transform(lambda s: s.count())
	df3 = df2.sort_values(by=['freq', 'labels_'], ascending=[False, False])
	c1 = df3.labels_ != df3.labels_.shift()
	df3['cluster_'] = c1.cumsum()

	# plot

	binsize = affinity_clus_result[1] -1
	title_ = 'Clusters from samples containing attribute ' + facets
	df3['cluster_'].plot(x='Clusters', y='Samples per cluster', kind='hist', bins=binsize, title=title_, colormap = 'jet')
	plt.xlabel('Clusters')
	plt.ylabel('Samples per cluster')
	plt.show()

def hierarchical_cluster(X):
	print('Doing Hierarchical Clustering...')

	best_params = best_linkage(X)
	best_method = best_params[0]
	best_metric = best_params[1]
	coph = best_params[2]

	Z = linkage(X, best_method, best_metric)
	print('NB: best cophenetic correlation distance is', coph)



def best_linkage(X):

	# Tests multiple options for linkage for the 

	method_options = ['single', 'complete', 'average', 'weighted', 'centroid', 'median', 'ward']
	metric_options = ['euclidean', 'cityblock', 'hamming', 'cosine']
	
	best_method_score = 0
	best_method = ''
	for u in method_options:
		Z = linkage(X, u)
		coph, coph_dists = cophenet(Z, pdist(X))
		# print('Method:', u, 'gave cophenetic correlation distance', coph)
		if coph > best_method_score:
			best_method_score = coph
			best_method = u
	# print('Best method is', best_method)

	best_metric_score = 0
	best_metric = ''
	if best_method is not 'ward':
		for q in metric_options:
			Z = linkage(X, best_method, q)
			coph, coph_dists = cophenet(Z, pdist(X))
			# print('Within', best_method, ',', q, 'gave score', coph)
			if coph > best_metric_score:
				best_metric_score = coph
				best_metric = q

	print('Best linkage method is', best_method, 'using metric', best_metric)
	print('Score:', best_metric_score)

	return (best_method, best_metric, best_metric_score)


if __name__ == '__main__':

	facets = 'frozenDesertFrequency'
	matrixA = build_matrix(facets)
	X = matrixA[1]
	df = matrixA[0]

	# # Affinity Propagation Clustering

	# affinity_clus_result = affinity_cluster(X)
	# affinity_histo(df, affinity_clus_result)


	# Hierarchical Clustering
	hierarchical_cluster(X)
	# This is a test 1





