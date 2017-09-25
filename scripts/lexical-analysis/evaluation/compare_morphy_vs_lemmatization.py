from __future__ import print_function
import future        # pip install future
import builtins      # pip install future
import past          # pip install future
import six           # pip install six
from future.utils import iteritems

import re
from functools import wraps
from time import time
import itertools

import argparse
import os, sys
import csv, unicodecsv
import datetime
import re

import enchant
from enchant import DictWithPWL
from enchant.checker import SpellChecker

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Class to check if attribute type is number or set of sequence chars, AGCT
import sys
sys.path.insert(0, '/Users/twhetzel/git/biosamples-data-curation/scripts')
import validator

import nltk
from nltk import wordpunct_tokenize
from nltk import WordNetLemmatizer
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import PorterStemmer
from nltk.stem.snowball import SnowballStemmer

import progressbar
from time import sleep
from tqdm import *

import operator
from multiprocessing import Process, Pool, Value, Array




def read_attr_type_file():
    """ 
    Read file of unique attribute types. 
    """
    counter = 0
    with open(args.attr_type_file_path, 'r') as f:
        content = f.readlines()

    # Strip lines of newline/return characters in csv file
    content = [x.strip(' \t\n\r') for x in content]

    # Generate dictionary of types, their count and reformatted attr_type
    attribute_type_dict = {}

    for item in content:
        counter += 1
        inner_dict = {}
        
        # Split on facet name and frequency
        attr_type, value = item.split(',')
        # Reformat attr_type, remove '_facet' suffix
        split_attr_type, junk = attr_type.split('_')
        
        # Split on uppercase letter to generate tokens from facets
        formatted_attr_type_list = re.findall('[0-9a-zA-Z][^A-Z]*', split_attr_type)
        formatted_attr_type = ' '.join(formatted_attr_type_list)

        # Create inner dictionary keys and values
        inner_dict['usage_count'] = value.strip()
        inner_dict['tokens'] = formatted_attr_type_list
        inner_dict['with_spaces'] = formatted_attr_type
    
        # Build dictionary with number of attribute types to analyze    
        if counter <= args.num_attr_review:
            attribute_type_dict[split_attr_type] = inner_dict

    
    print("Total number of Attribute Types: ", len(attribute_type_dict.keys()))
    return attribute_type_dict


def check_for_typos(at_token_dict):
    """
    Check each token for typos.
    """
    counter = 0
    attr_type_with_numbers = []
    attr_type_as_sequences = [] # e.g. ATGC

    attr_types_with_no_typos = []
    attr_types_with_typos = []

    # Intitialize dictionaries
    mywords = enchant.DictWithPWL("en_US","../../../master-data/biosamples-lexical-dictionary/lowercase_mywords.txt")

    for attr_type, attr_type_data in iteritems(at_token_dict):
        counter += 1
        attr_type_validator = validator.AttrTypeValidator(attr_type_data['with_spaces'])

        # Check for known categories of attribute types that 
        # will not pass a dictionary test, e.g. string of sequences, contains numbers, etc.
        if attr_type_validator.check_for_sequence_strings():
            attr_type_as_sequences.append(attr_type)

        if attr_type_validator.check_for_numbers():
            # Note: Some attr_types can contain numbers and still be "mergable" attribute types, e.g. CD4
            attr_type_with_numbers.append(attr_type)

        # Check for attr_type for typos
        total_correctly_spelled_tokens = 0
        #NEW: add not in attr_type_with_numbers. Consider leaving Attr w/numbers and compare lowercase versions
        if attr_type not in attr_type_as_sequences and attr_type not in attr_type_with_numbers \
            and counter < int(args.num_attr_review):

            token_list = attr_type_data['tokens']
            for token in token_list:
                # Check token for typos using custom dictionary
                is_correct_mywords = mywords.check(token.lower())

                if is_correct_mywords:
                    total_correctly_spelled_tokens += 1
                else:
                    pass

            if len(token_list) != total_correctly_spelled_tokens:
                attr_types_with_typos.append(attr_type)
            else:
                attr_types_with_no_typos.append(attr_type)

    return attr_types_with_no_typos, attr_types_with_typos


def compare_methods(data):
    """
    Compare use of morhpy and lemmatization to see 
    which method better "lemmatizes" tokens in AttrTypes.
    """

    # Customize stopword list
    stopWords = set(stopwords.words('english'))
    #TODO: Consider also removing y, can't include 'yes' because "yes_facet"
    words_to_remove = ['m', 's', 't', 'd', 'before', 'after', 'at', 'during', 'no', 'he']
    for word in words_to_remove:
        stopWords.remove(word)


    # Print file headers
    with open("lex_comparison.csv", "w") as outfile:
        csvout = csv.writer(outfile)
        csvout.writerow(["attr_type", "morphed_token", "lemma", "better_method", "","","",\
            "porter", "snowball", "stemming_is_different"])
    
        # Compare Morphy to Lemmatization
        for attr_type in tqdm(data, desc="Comparing methods", ncols=100):
            attr_tokens = attribute_type_dict[attr_type]["tokens"]

            # Remove stopwords
            attr_tokens_filtered = [w.lower() for w in attr_tokens if not w.lower() in stopWords]

            wnl = WordNetLemmatizer()
            porter_stemmer = PorterStemmer()
            snowball_stemmer = SnowballStemmer("english")

            
            for token in attr_tokens_filtered:
                # Use Morphy
                morphed_token = wordnet.morphy(token)
                if morphed_token == None:
                    morphed_token = token

                # Use lemmatization
                lemma = wnl.lemmatize(token)

                # Use Porter stemming
                porter_stemmed = porter_stemmer.stem(token)

                # Use Snowball stemming
                snowball_stemmed = snowball_stemmer.stem(token) 

                # Check which is better or changes token
                better_method = ""
                if len(morphed_token) < len(token) and len(lemma) < len(token):
                    better_method = "both_methods"
                elif len(morphed_token) == len(token) and len(lemma) == len(token):
                    better_method = "neither_method"
                elif len(morphed_token) < len(token):
                    better_method = "morphy_method"
                else:
                    better_method = "lemma_method"

                # Check if stemming generates a different form than token
                is_different = ""
                if porter_stemmed != token and snowball_stemmed != token:
                    is_different = "both"
                elif porter_stemmed != token and snowball_stemmed == token:
                    is_different = "porter"
                elif porter_stemmed == token and snowball_stemmed != token:
                    is_different = "snowball"
                else:
                    is_different = "neither"
                    
                csvout.writerow([attr_type, morphed_token, lemma, better_method, \
                    len(token), len(morphed_token), len(lemma), \
                    porter_stemmed, snowball_stemmed, is_different])

                # print(attr_type, morphed_token, lemma, better_method, \
                #     len(token), len(morphed_token), len(lemma), \
                #     porter_stemmed, snowball_stemmed, is_different)



if __name__ == '__main__':
    """
    Compare lexical methods to lemmatize and stem tokens.
    """
    print("Start analysis...")

    # Commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--attr_type_file_path', default="../../../master-data/cocoa_facets.csv")
    parser.add_argument('--num_attr_review', default=26610, help="Number of Attributes to analyze their values")
    args = parser.parse_args()


    # Get attr_type file with count of attr per type
    attribute_type_dict = read_attr_type_file()

    # Check for typos
    no_typos, at_typos = check_for_typos(attribute_type_dict)

    # Compare methods
    compare_methods(no_typos)

    # compare_methods(at_typos)




