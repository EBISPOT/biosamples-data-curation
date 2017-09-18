"""
using and testing out jellyfish algos

"""


# Imports
import requests, json, csv, re, itertools, numpy, sys
import pandas as pd
import jellyfish





if __name__ == "__main__":

	# semi smart _facet stripping

	for chunk in pd.read_csv('pairs_copy.csv', names=['facet1', 'facet2'],  iterator=True, chunksize=1000):
		chunk['facet1'] = chunk['facet1'].map(lambda x: x.rstrip('_facet') if '_facet' in str(x) else str(x))		
		chunk['facet2'] = chunk['facet2'].map(lambda x: x.rstrip('_facet') if '_facet' in str(x) else str(x))		
		
		# lambda implementation of the jellyrish algo's

		chunk['jaro_distance'] = chunk.apply(lambda row: jellyfish.jaro_distance(str(row['facet1']), str(row['facet2'])), axis = 1)  
		chunk['levenshtein_distance'] = chunk.apply(lambda row: jellyfish.levenshtein_distance(str(row['facet1']), str(row['facet2'])), axis = 1)  
		chunk['jaro_winkler'] = chunk.apply(lambda row: jellyfish.jaro_winkler(str(row['facet1']), str(row['facet2'])), axis = 1)  
		chunk['damerau_levenshtein_distance'] = chunk.apply(lambda row: jellyfish.damerau_levenshtein_distance(str(row['facet1']), str(row['facet2'])), axis = 1)  
		chunk['match_rating_comparison'] = chunk.apply(lambda row: jellyfish.match_rating_comparison(str(row['facet1']), str(row['facet2'])), axis = 1)  
		chunk['hamming_distance'] = chunk.apply(lambda row: jellyfish.hamming_distance(str(row['facet1']), str(row['facet2'])), axis = 1)  


		'''
		for testing stuff
		'''

		# jaro_distance = jellyfish.jaro_distance('environmental', 'environment')
		# levenshtein_distance = jellyfish.levenshtein_distance('environmental', 'environment')
		# jaro_winkler = jellyfish.jaro_winkler('environmental', 'environment')
		# damerau_levenshtein_distance = jellyfish.damerau_levenshtein_distance('environmental', 'environment')
		# match_rating_comparison = jellyfish.match_rating_comparison('environmental', 'environment')
		# hamming_distance = jellyfish.hamming_distance('environmental', 'environment')

		# print('jaro_distance:', jaro_distance)
		# print('levenshtein_distance:', levenshtein_distance)
		# print('jaro_winkler:', jaro_winkler)
		# print('damerau_levenshtein_distance:', damerau_levenshtein_distance)
		# print('match_rating_comparison:', match_rating_comparison)
		# print('hamming_distance:', hamming_distance)


		print(chunk)
		sys.exit()














