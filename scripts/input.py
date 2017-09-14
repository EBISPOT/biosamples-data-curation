#!/usr/bin/python
# checks for an creates input files if they are missing

# currently creates facets and freq of facets from solr
# more inputs need to be added.

# Imports
import requests, json, csv, re
import pandas as pd



# this module gets facets from solr and returns a dict,df and csv file
def get_solr_facets():
	# print("facets_name,facets_count")
	results = []
	#the inital search for facets
	q = "*:*"
	facet = "crt_type_ft"
	query_params = {
	    "q" : q,
	    "wt" : "json",
	    "rows": 0,
	    "facet": "true",
	    "facet.field": facet,
	    "facet.limit": -1,
	    "facet.sort": "count",
	    "facet.mincount": "1"
	}
	response = requests.get('http://cocoa.ebi.ac.uk:8989/solr/merged/select', params=query_params)
	facets = response.json()['facet_counts']['facet_fields'][facet]

	 # selects data to build dict and strips '_facet' no fancy regex because solr strips other underscores
	facets_name_raw = facets[::2]
	facets_name = [s.replace('_facet', '') for s in facets_name_raw ]
	facets_count = facets[1::2]

	facets_dict = {}
	for i in range(len(facets_name)):
		facets_dict[facets_name[i]] = facets_count[i]

	facets_df = pd.DataFrame.from_dict(facets_dict, orient = 'index')
	facets_df.reset_index(inplace=True)
	facets_df.columns = ['facet','frequency']

	facets_list = facets_dict.keys()
	return [facets_dict, facets_df, facets_list]

if __name__ == "__main__":

	# if 'facets.csv' exists solr is not asked to get them again.
	# Del this file if you want it to fetch them again.
	try:
		facets_df = pd.read_csv('facets.csv')
		facets_df.columns = ['index','facet','frequency']
		facets_list = facets_df['facet'].tolist()
		# facets_df = facets_df['facet'].astype(str)
	except FileNotFoundError:
		[facets_dict, facets_df, facets_list] = get_solr_facets()
		facets_df.to_csv('facets.csv', encoding='utf-8')






