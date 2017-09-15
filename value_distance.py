"""
read csv
get pairs
get pair values from trish's dict
do stats

"""


# Imports
import requests, json, csv, re, itertools, numpy, sys, ast
import pandas as pd

# takes the values input file and convers it to dict of dict format
# also strips the _facet bit

def dict_convert():

	with open('demo-facet_value_results_2017-09-14_11-15-52.csv', 'r') as f:
		data = ast.literal_eval(f.read())

		main_dict = {}

		for attribute in data:
			key = next(iter(attribute))
			key_strip = lambda i: i.rstrip('_facet') if '_facet' in i else i
			key_stripped = key_strip(key)
			value_list = attribute.get(key)
			value_dict = {}

			count = 0
			for x in value_list:
				if count % 2 == 0:
					temp_key = x
					count = count +1
				else:
					value_dict[temp_key] = x
					count = count +1
			main_dict[key_stripped] = value_dict
		return main_dict

def get_some_keys():

	# not used becasue of size issues NB pairs_copy is huge
	# this can pull in chunks of a csv and make smaller dataframes
	# these can be used to iterate through large pairs at a later stage
	# this also strips the _facet bit

	for chunk in pd.read_csv('pairs_copy.csv', names=['facet1', 'facet2'],  iterator=True, chunksize=1000):
		chunk['facet1'] = chunk['facet1'].map(lambda x: x.rstrip('_facet') if '_facet' in str(x) else str(x))		
		chunk['facet2'] = chunk['facet2'].map(lambda x: x.rstrip('_facet') if '_facet' in str(x) else str(x))
	return chunk

def value_scoring(facet1, facet2):

	value_info = dict_convert()

	values1 = value_info.get(facet1)
	values2 = value_info.get(facet2)

	values_list1 = values1.keys()
	values_list2 = values2.keys()

	total_attributes = len(values_list1) + len(values_list2)
	matching_attributes = len(set(values_list1) & set(values_list2))

	match_freq = 0
	for k in values_list1:
		if k in values_list2:
			freq = values1.get(k) + values2.get(k)
			match_freq = match_freq + freq

	total_freq = sum(values1.values()) + sum(values2.values())

	score = ((matching_attributes * 2) / (total_attributes)) * (match_freq / total_freq)
	return score

if __name__ == "__main__":

	# skipping the get_some_keys type input I'll just focus on a couple for testing
	facet1 = 'environementalHistory'
	facet2 = 'environmentBiom'

	x = value_scoring(facet1, facet2)

	# print(value_info.keys())
	print(x)
	sys.exit()














