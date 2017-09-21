"""
Value-Distance 2

Separate facet value types (numeric (>95%), alpha (>95%) or mixed)
Do analysis depending on the type. Either bag of words or chi2 etc.
This script should aim to produce as much data as nessesary. It is
not designed to be optimised to run on all samples.

"""


# Imports
import requests, json, csv, re, numpy, sys, ast, jellyfish, math
import pandas as pd
import scipy.stats as stats
from dateutil.parser import parse
from itertools import combinations, product
from matplotlib import pyplot as plt
import jellyfish._jellyfish as py_jellyfish


# takes the values input file and convers it to dict of dict format
# also strips the _facet bit


def dict_convert(input_file):

	"""
	Converts the raw json value data to a dict of dicts
	"""

	with open(input_file, 'r') as f:
		data = ast.literal_eval(f.read())

		main_dict = {}
		for attribute in data:
			key = next(iter(attribute))
			# key_strip = lambda i: i.rstrip('_facet') if '_facet' in i else i
			# # print(key_strip)
			# key_stripped = key_strip(key)
			if '_facet' in key:
				key_stripped = key.replace('_facet', '')
			else:
				key_stripped = ''

			value_list = attribute.get(key)
			value_dict = {}

			count = 0
			for x in value_list:
				if count % 2 == 0:
					temp_key = x
					count = count + 1
				else:
					value_dict[temp_key] = x
					count = count + 1
			main_dict[key_stripped] = value_dict

		return main_dict

def type_hasher(values_list1, values_list2):

	"""
	Uses try to define a facets value type as a pair
	it calculates proportion of data types for each facet

	returns type buckets for humans to have a quick look.

	returns type_hash as:

	'numeric match' if 90% of both facet values are numbers (int, float or exponentials)
	'strings match' if 90% of both facet  values are strings (so excludes numbers)
	'date match' if 90% of both facet values are date type (I pull in a tool for this check and it checks many types)
	'mixed match string', 'mixed match numeric', 'mixed match date' and combinations
	thereof are returned if those relative ratios are within 10% and the ratio is greater than 0.25
	this prevents 0.00 and 0.00 matching etc

	"""
	if len(values_list1) > 0 and len(values_list2) > 0:

		# test facet 1

		type_int_f1 = 0
		type_str_f1 = 0
		type_date_f1 = 0
		values_list1_num = []
		for value in values_list1:
			try:	
				values_list1_num.append(float(value))
				type_int_f1 = type_int_f1 + 1
			except (ValueError, AttributeError):
				try:
					value = value.replace(',', '.')
					values_list1_num.append(float(value))
					type_int_f1 = type_int_f1 + 1
				except (ValueError, AttributeError):
				# attempts to create a date from value
					try:
						parse(value)
						type_date_f1 = type_date_f1 + 1
					except (ValueError, AttributeError):
						# add in regex for starts with no? to pick up measurements with units?
						type_str_f1 = type_str_f1 + 1
						pass

		int_ratio1 = type_int_f1/(type_int_f1 + type_str_f1 + type_date_f1)
		str_ratio1 = type_str_f1/(type_int_f1 + type_str_f1 + type_date_f1)
		date_ratio1 = type_date_f1/(type_int_f1 + type_str_f1 + type_date_f1)


		# print('int_ratio1: ',int_ratio1)
		# print('str_ratio1: ',str_ratio1)

		type_int1 = int_ratio1 > 0.9
		type_str1 = str_ratio1 > 0.9
		type_date1 = date_ratio1 > 0.9



		# test facet 2

		type_int_f2 = 0
		type_str_f2 = 0
		type_date_f2 = 0
		values_list2_num = []
		for value in values_list2:
			try:	
				values_list2_num.append(float(value))
				type_int_f2 = type_int_f2 + 1
			except (ValueError, AttributeError):
				try:
					value = value.replace(',', '.')
					values_list2_num.append(float(value))
					type_int_f2 = type_int_f2 + 1
				except:
					try:
						parse(value)
						type_date_f2 = type_date_f2 + 1
					except (ValueError, AttributeError):
						type_str_f2 = type_str_f2 + 1
						pass

		int_ratio2 = type_int_f2/(type_int_f2 + type_str_f2 + type_date_f2)
		str_ratio2 = type_str_f2/(type_int_f2 + type_str_f2 + type_date_f2)
		date_ratio2 = type_date_f2/(type_int_f2 + type_str_f2 + type_date_f2)



		# are they the same? arbitary limits:

		# both over 90% similar?
		type_int2 = int_ratio2 > 0.9
		type_str2 = str_ratio2 > 0.9
		type_date2 = date_ratio2 > 0.9

		# ratios same within 10% error?
		str_ratio1_lo = str_ratio1 * 0.95
		str_ratio1_hi = str_ratio1 * 1.05

		int_ratio1_lo = int_ratio1 * 0.95
		int_ratio1_hi = int_ratio1 * 1.05

		date_ratio1_lo = date_ratio1 * 0.95
		date_ratio1_hi = date_ratio1 * 1.05

		type_hash_mixed = []
		if str_ratio1 > 0.25 and str_ratio2 > 0.25 and str_ratio1_lo < str_ratio2 < str_ratio1_hi:
			type_hash_mixed.append('mixed match string')
		if int_ratio1 > 0.25 and int_ratio2 > 0.25 and int_ratio1_lo < int_ratio2 < int_ratio1_hi: 
			type_hash_mixed.append('mixed match numeric')
		if date_ratio1 > 0.25 and date_ratio2 > 0.25 and date_ratio1_lo < date_ratio2 < date_ratio1_hi: 
			type_hash_mixed.append('mixed match date')


		if type_int1 and type_int2:
			type_hash = 'numeric match'
			return (type_hash, values_list1_num, values_list2_num)
		elif type_str1 and type_str2:
			# they are both str value types not many int
			type_hash = 'strings match'
		elif type_date1 and type_date2:
			type_hash = 'date match'
		elif type_hash_mixed:

			if 'mixed match string' and 'mixed match numeric' and 'mixed match date' in type_hash_mixed:
				type_hash = 'mixed string, numeric and date match'

			elif 'mixed match string' and 'mixed match numeric' in type_hash_mixed:
				type_hash = 'mixed string and numeric match'
			elif 'mixed match string' and 'mixed match date' in type_hash_mixed:
				type_hash = 'mixed string and date match'
			elif 'mixed match numeric' and 'mixed match date' in type_hash_mixed:
				type_hash = 'mixed numeric and date match'

			elif 'mixed match string' in type_hash_mixed:
				type_hash = 'mixed match string'
			elif 'mixed match numeric' in type_hash_mixed:
				type_hash = 'mixed match numeric'
			elif 'mixed match date' in type_hash_mixed:
				type_hash = 'mixed match date'

		else:
			type_hash = 'no match'

		return (type_hash)

	else:
		type_hash = 'no match'
		return (type_hash)




	# values_list1.isdigit()

def exact_value_scoring(values_list1, values_list2):

	"""
	pass this two lists of values froma pair of facets and it will
	give a score for exact value matches
	"""
	if len(values_list1) > 0 and len(values_list2) > 0:
		total_attributes = len(values_list1) + len(values_list2)
		matching_attributes = len(set(values_list1) & set(values_list2))

		match_freq = 0

		# print(values_list1)
		# print(values_list2)
		for k in values_list1:
			if k in values_list2:
				freq = values1.get(k) + values2.get(k)
				match_freq = match_freq + freq

		total_freq = sum(values1.values()) + sum(values2.values())

		score = ((matching_attributes * 2) / (total_attributes)) * (match_freq / total_freq)
		return score
	else:
		score = 0
		return score

def fuzzy_value_scoring(values_list1, values_list2):

	"""
	string pairwise matcher
	NB only best matches are taken this is not all by all
	gets fuzzy pair match based on jarowinkler
	returns dict with mean, stc and 0.9 qualtile
	for jarowinkler, damerau levenshtein and hamming distances
	"""
	if len(values_list1) > 0 and len(values_list2) > 0:


		if len(values_list1) > len(values_list2):
			short_list = values_list2
			long_list = values_list1
		else:
			short_list = values_list1
			long_list = values_list2		

		# calculate the best fuzzy matches
		best_match_list = []
		for value1 in short_list:
			jaro_distance_list = []
			for value2 in long_list:

				try:
					damerau_levenshtein_distance = jellyfish.damerau_levenshtein_distance(value1, value2)
				except ValueError:
					damerau_levenshtein_distance = py_jellyfish.damerau_levenshtein_distance(value1, value2)

				jaro_winkler = jellyfish.jaro_winkler(value1, value2)
				hamming_distance = jellyfish.hamming_distance(value1, value2)

				jaro_tuple = (value1, value2, jaro_winkler, damerau_levenshtein_distance, hamming_distance)
				jaro_distance_list.append(jaro_tuple)		
			best_match = max(jaro_distance_list,key=lambda x:x[2])
			best_match_list.append(best_match)
		df = pd.DataFrame(best_match_list, columns = ['facet1', 'facet2', 'jaro_distance', 'damerau_levenshtein_distance', 'hamming_distance'])
		
		jaro_distance_quant = df['jaro_distance'].quantile(0.9)
		jaro_distance_mean = df['jaro_distance'].mean()
		jaro_distance_std = df['jaro_distance'].std()
		damerau_levenshtein_distance_quant = df['damerau_levenshtein_distance'].quantile(0.9)
		damerau_levenshtein_distance_mean = df['damerau_levenshtein_distance'].mean()
		damerau_levenshtein_distance_std = df['damerau_levenshtein_distance'].std()
		hamming_distance_quant = df['hamming_distance'].quantile(0.9)
		hamming_distance_mean = df['hamming_distance'].mean()
		hamming_distance_std = df['hamming_distance'].std()

		results = {'jaro_distance_quant':jaro_distance_quant, \
		'jaro_distance_mean':jaro_distance_mean, \
		'jaro_distance_std':jaro_distance_std, \
		'damerau_levenshtein_distance_quant':damerau_levenshtein_distance_quant, \
		'damerau_levenshtein_distance_mean':damerau_levenshtein_distance_mean, \
		'damerau_levenshtein_distance_std':damerau_levenshtein_distance_std, \
		'hamming_distance_quant':hamming_distance_quant, \
		'hamming_distance_mean':hamming_distance_mean, \
		'hamming_distance_std':hamming_distance_std}
		# so a good match will be a high mean, low std. The quantile is prob better than mean.
		
		return results
	else:

		# 'N.A.' returned if one or both of the facets dont have any values.


		results = {'jaro_distance_quant':'N.A.', \
		'jaro_distance_mean':'N.A.', \
		'jaro_distance_std':'N.A.', \
		'damerau_levenshtein_distance_quant':'N.A.', \
		'damerau_levenshtein_distance_mean':'N.A.', \
		'damerau_levenshtein_distance_std':'N.A.', \
		'hamming_distance_quant':'N.A.', \
		'hamming_distance_mean':'N.A.', \
		'hamming_distance_std':'N.A.'}

		return results

def magnitude_diff(type_hash):

	if type_hash[0] == 'numeric match':
		values_list1_num = type_hash[1]
		values_list2_num = type_hash[2]
		# values_list1_stat = stats.normaltest(values_list1_num)
		# values_list2_stat = stats.normaltest(values_list2_num)
		mean1 = sum(values_list1_num)/len(values_list1_num)
		mean2 = sum(values_list2_num)/len(values_list2_num)
		mag1 = int(math.floor(math.log10(mean1)))
		mag2 = int(math.floor(math.log10(mean2)))
	if mag1 == mag2:
		magnitude_difference = 'Roughly Equivalent'
	else:
		magnitude_difference = abs(mag1-mag2)
	return magnitude_difference

if __name__ == "__main__":

	# skipping the get_some_keys type input I'll just focus on a couple for testing
	facet1 = 'dateOfSort'
	facet2 = 'experimentStartDate'

	# get value data globally
	input_file = 'demo-facet_value_results_2017-09-14_11-15-52.csv'
	value_info = dict_convert(input_file) 
	values1 = value_info.get(facet1)
	values2 = value_info.get(facet2)

	# print(value_info)


	try:
		values_list1 = values1.keys()
	except AttributeError:
		values_list1 = []
	try:
		values_list2 = values2.keys()
	except AttributeError:
		values_list2 = []

	exact_score = exact_value_scoring(values_list1, values_list2)
	type_hash = type_hasher(values_list1, values_list2)
	if type(type_hash) is str:
		type_match = type_hash
	elif type(type_hash) is list or tuple:
		type_match = type_hash[0]
	else:
		print('something going wrong with type_hash')
		print(type(type_hash))
		sys.exit()

	if type_match == 'numeric match':
		magnitude_difference = magnitude_diff(type_hash)
		fuzzy_scores = 'N.A.'
	elif type_match == 'date match':
		magnitude_difference = 'N.A.'
		fuzzy_scores = 'N.A.'
	else:
		magnitude_difference = 'N.A.'
		fuzzy_scores = fuzzy_value_scoring(values_list1, values_list2)
		# print(values_list2)

	try:
		fuzzy_scores.get('jaro_distance_quant')
		jaro_score = fuzzy_scores.get('jaro_distance_quant')
	except AttributeError:
		jaro_score = 'N.A.'


	
	print('Exact Score:', exact_score)
	print('Type Match:', type_match)
	print('Magnitude Difference:', magnitude_difference)
	# lots more info is calculated for the fuzzy score if needed!
	print('Jaro Score:', jaro_score)

	
	
	sys.exit()
