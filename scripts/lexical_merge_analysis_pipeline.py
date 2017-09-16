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

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import csv

# Class to check if attribute type is number or set of sequence chars, AGCT
import validator

import nltk
from nltk import wordpunct_tokenize
from nltk import WordNetLemmatizer
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.corpus import wordnet


# Methods
def get_timestamp():
    """ 
    Get timestamp of current date and time. 
    """
    timestamp = '{:%Y-%m-%d_%H-%M-%S}'.format(datetime.datetime.now())
    return timestamp


def timing(f):
    """
    Create wrapper to report time of functions.
    """
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print('Function: %r took: %2.2f sec, %2.2f min' % (f.__name__, te-ts, (te-ts)/60))
        return result
    return wrap


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
        
        # Split on facet and usage
        attr_type, value = item.split(',')
        # Reformat attr_type, remove '_facet' suffix
        split_attr_type, junk = attr_type.split('_')
        
        # split on uppercase letter to generate tokens from facets
        formatted_attr_type_list = re.findall('[0-9a-zA-Z][^A-Z]*', split_attr_type)
        formatted_attr_type = ' '.join(formatted_attr_type_list)
        # print("FAT: ", formatted_attr_type)

        inner_dict['usage_count'] = value.strip()
        inner_dict['tokens'] = formatted_attr_type_list
        inner_dict['with_spaces'] = formatted_attr_type
        
        attribute_type_dict[attr_type] = inner_dict
    
    # for k,v in iteritems(attribute_type_dict):
    #     print(k, v['tokens'])
    
    print("Total number of Attribute Types: ", len(attribute_type_dict.keys()))
    return attribute_type_dict


def read_no_typos_attr_type():
    """
    Read file of known list of attribute types with typos.
    """
    with open(args.no_typo_attr_type_file_path, 'r') as f:
        content = f.readlines()
        print(content)
    return content


# NOT CURRENTLY USED
def check_for_matches(attr_dict):
    """
    Check for overall matches between attribute type due to case and space differences
    """
    TIMESTAMP = get_timestamp()
    filename = "overall_matches_"+TIMESTAMP+".csv"
    save_directory_path = "/Users/twhetzel/git/biosamples-data-mining/data_results"
    data_directory = "NoTypoAttrType"
    completeName = os.path.join(save_directory_path, data_directory, filename)

    outfile = open(completeName, "w")
    csvout = csv.writer(outfile)
    csvout.writerow(["Attr1", "Attr1_Usage", "Attr2", "Attr2_Usage"])
    
    original_attr_type_list = attr_dict.keys()
    copy_original_attr_type_list = original_attr_type_list[:]
    # print(original_attr_type_list)
    counter = 0

    formatted_attr_type_list = []
    matches_list = []

    for attr_type in original_attr_type_list:
        # remove spaces and lowercase
        formatted_attr_type = attr_type.lower()
        formatted_attr_type = formatted_attr_type.replace(" ", "")
        # print(formatted_attr_type)
        formatted_attr_type_list.append(formatted_attr_type)


    for attr1 in original_attr_type_list:
        # print("** Attr1:", attr1, attr1.lower().replace(" ",""))
        # original_attr_type_list.remove(attr1)
        for attr2 in copy_original_attr_type_list:
            # find matches where lowercase match, but original casing does not match
            if attr1.lower() == attr2.lower() and attr1 != attr2:
                counter += 1
                original_attr_type_list.remove(attr2)
                print(counter, "MATCHES: ", attr1, attr_dict[attr1], attr2, attr_dict[attr2])
                csvout.writerow([attr1, attr_dict[attr1], attr2, attr_dict[attr2]])
    outfile.close()


@timing
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
    # d = enchant.Dict("en_US") #default dictionary
    mywords = enchant.DictWithPWL("en_US","../master-data/biosamples-lexical-dictionary/mywords.txt")

    for attr_type, attr_type_data in iteritems(at_token_dict):
        counter += 1
        # print("Tokens: ",attr_type_data['tokens'])
        attr_type_validator = validator.AttrTypeValidator(attr_type_data['with_spaces'])

        # Check for known categories of attribute types that 
        #will not pass a dictionary test, e.g. string of sequences, contains numbers, etc.
        if attr_type_validator.check_for_sequence_strings():
            attr_type_as_sequences.append(attr_type)

        if attr_type_validator.check_for_numbers():
            #Note: Some attr_types can contain numbers and still be "mergable" attribute types, e.g. CD4
            attr_type_with_numbers.append(attr_type)

        # Check for attr_type for typos
        total_correctly_spelled_tokens = 0
        #NEW: add not in attr_type_with_numbers
        if attr_type not in attr_type_as_sequences and attr_type not in attr_type_with_numbers \
            and counter < int(args.num_attr_review):
            
            token_list = attr_type_data['tokens']
            # print("\n**TokenList: ", token_list)
            for token in token_list:
                # check token for typos
                is_correct_mywords = mywords.check(token)

                if is_correct_mywords:
                    total_correctly_spelled_tokens += 1
                else:
                    pass

            if len(token_list) != total_correctly_spelled_tokens:
                attr_types_with_typos.append(attr_type)
            else:
                attr_types_with_no_typos.append(attr_type)


    return attr_types_with_no_typos, attr_types_with_typos


@timing
def check_for_fuzzy_matches(attribute_types):
    """
    For attr_type with one or more tokens that do not pass 
    the dictionary test, check if this attr_type closely matches 
    other attr_types. RE-DO DESC
    """
    print("Checking for fuzzy matches...")

    # TIMESTAMP = get_timestamp()
    # filename = "attr_type_with_NO_typos_to_merge_"+TIMESTAMP+".csv"
    # save_directory_path = "/Users/twhetzel/git/biosamples-data-mining/data_results"
    # data_directory = "NoTypoAttrType"
    # completeName = os.path.join(save_directory_path, data_directory, filename)

    # outfile = open(completeName, "w")
    # csvout = csv.writer(outfile)
    # csvout.writerow(["Attr1", "Attr2", "FM_Score", "Attr1_Usage", "Attr2_Usage"])

    # all_attribute_types = attribute_type_dict.keys()
    all_matches = []
    match_pair_score = ()
    copy_attribute_types = attribute_types[:]

    # all_list_pairs = list(itertools.product(attribute_types[:500], attribute_types[:500]))
    # print(all_list_pairs)
    # print("Len-AllPairs: ", len(all_list_pairs))

    counter = 0
    print("NumRev: ", args.num_attr_review)
    for attr1 in attribute_types:
        for attr2 in copy_attribute_types:
            fuzzy_match_score = fuzz.ratio(attribute_type_dict[attr1]["with_spaces"], \
                attribute_type_dict[attr2]["with_spaces"])
            
            if fuzzy_match_score > 90 and attr1 != attr2:  #fuzzy_match_score != 100:
                counter += 1

                match_pair_score = (attr1, attr2, fuzzy_match_score)
                all_matches.append(match_pair_score)

                # copy_attribute_types.remove(attr2)
                # print("\n",match_pair_score)
                # print("Remove this attr_type:", attr2)
                if attr2 in attribute_types:
                    attribute_types.remove(attr2)


                # csvout.writerow([attr1, attr2, fuzzy_match_score, attribute_type_dict[attr1], attribute_type_dict[attr2]])
                # print("("+str(counter)+")", attribute_type_dict[attr1]["with_spaces"], "--", \
                #     attribute_type_dict[attr2]["with_spaces"], fuzzy_match_score)

    # print("All Matches: ", all_matches)
    # print("Count All Matches: ", len(all_matches))
    # outfile.close()
    return all_matches


@timing
def secondary_fuzzy_match_check(matches):
    """
    Apply fuzzy match checking on each token. 
    Account for difference in numbers of tokens in matches and stop words.
    """
    total_confirmed_match_pairs = 0
    confirmed_matches = []
    unconfirmed_matches = []

    for match_pair in matches:
        mp1_tokens = attribute_type_dict[match_pair[0]]["tokens"]
        mp2_tokens = attribute_type_dict[match_pair[1]]["tokens"]

        # Remove stopwords
        mp1_tokens_filtered = [w for w in mp1_tokens if not w in stopwords.words('english')]
        mp2_tokens_filtered = [w for w in mp2_tokens if not w in stopwords.words('english')]
        # print(mp1_tokens_filtered, mp2_tokens_filtered)

        # Check Fuzzy match score on individual tokens with stopwords/tokens removed
        fm_score_100_count = 0
        non_matching_fuzz_scores = []
        if len(mp1_tokens_filtered) != len(mp2_tokens_filtered):
            # print("Can't check these...", mp1_tokens_filtered, mp2_tokens_filtered)
            unconfirmed_matches.extend([match_pair])
        else:
            for mp1_token, mp2_token in zip(mp1_tokens_filtered, mp2_tokens_filtered):
                morphed_mp1_token = wordnet.morphy(mp1_token)
                morphed_mp2_token = wordnet.morphy(mp2_token)

                if morphed_mp1_token == None:
                    morphed_mp1_token = mp1_token
                if morphed_mp2_token == None:
                    morphed_mp2_token = mp2_token
                fuzz_score = fuzz.ratio(morphed_mp1_token, morphed_mp2_token)
                
                if fuzz_score == 100:
                    fm_score_100_count += 1
                else:
                    non_matching_fuzz_scores.append(fuzz_score)

            if fm_score_100_count == len(mp1_tokens_filtered):
                total_confirmed_match_pairs += 1
                confirmed_matches.extend([match_pair])
                # print("** These attr_types match!", "'"+attribute_type_dict[match_pair[0]]["with_spaces"]+"'", \
                #     "'"+attribute_type_dict[match_pair[1]]["with_spaces"]+"'\n")
            else:
                unconfirmed_matches.extend([match_pair])
                # print("** Need to manually check these (FuzzScore: "+str(non_matching_fuzz_scores)+"): ", "'"+attribute_type_dict[match_pair[0]]["with_spaces"]+"'", \
                #     "'"+attribute_type_dict[match_pair[1]]["with_spaces"]+"'\n")

    # print("** Total confirmed match pairs: ", total_confirmed_match_pairs)
    return confirmed_matches, unconfirmed_matches


@timing
def check_for_fuzzy_matches_between_confirmed_and_typo_group(*args):
    """
    Compare attribute_types with typos to those wthout typos
    and have other confirmed merge pairing.
    """
    # known_good_pairs[0] formatted as: ('patients_facet', 'patient_facet', 93)
    # typos[0] formatted as: bacteroidales_facet
    known_good_pairs = args[0]
    typos = args[1]
    # print("** LEN-KGP: ", len(known_good_pairs))
    # print("** TYPOS: ", len(typos))
    
    # Get list of known merges to compare to
    possible_new_merges = []
    new_merge = ()
    counter = 0

    for typo_attr_type in typos:
        typo_attr_type, junk = typo_attr_type.split('_')
        # print("\nTAT: ", typo_attr_type)
        for good_pair in known_good_pairs:
            good_pair1, junk = good_pair[0].split('_')
            good_pair2, junk = good_pair[1].split('_')
            # print("Good Pair: ", good_pair1, good_pair2)

            fuzz_score_gp1 = fuzz.ratio(typo_attr_type, good_pair1)
            fuzz_score_gp2 = fuzz.ratio(typo_attr_type, good_pair2)
            # print("** Fuzz Scores: ", fuzz_score_gp1, fuzz_score_gp2)

            if fuzz_score_gp1 > 90 and fuzz_score_gp2 > 90:
                counter += 1
                # print("("+str(counter)+")", "Possible matches between: ", typo_attr_type, \
                #     " and ", good_pair1, good_pair2)
                new_merge = (good_pair1, good_pair2, typo_attr_type, fuzz_score_gp1, fuzz_score_gp2)
                possible_new_merges.append(new_merge)

    # print("Possible New Merges: ", len(possible_new_merges))
    return possible_new_merges


@timing
def check_for_fuzzy_matches_between_unconfirmed_and_typo_group(*args):
    """
    Compare attribute types from no typos from unconfirmed merge with typos group.
    """
    unconfirmed_merge_no_typos = args[0]
    typos = args[1]

    unconfirmed_list_no_typos = []
    match_pair = ()
    unconfirmed_merge_typo_list = []
    confirmed_merge_typo_list = []

    # Loop through sets of unconfirmed merge pairs to get a single list
    for merge_pair in unconfirmed_merge_pairs:
        # print(merge_pair)
        unconfirmed_list_no_typos.append(merge_pair[0])
        unconfirmed_list_no_typos.append(merge_pair[1])

    # Loop through both lists
    for x, y in [(x,y) for x in unconfirmed_list_no_typos for y in typos]:
        # print("** Pairs to check for fuzzy match: ", x, y)
        x_formatted, junk = x.split('_')
        y_formatted, junk = y.split('_')
        
        fuzz_score = fuzz.ratio(x_formatted.lower(), y_formatted.lower())
        if fuzz_score > 90:
            # print("** Possible match betw unconfirmed+typo: ", x_formatted, y_formatted, fuzz_score)
            match_pair = (x_formatted, y_formatted, fuzz_score)
            unconfirmed_merge_typo_list.append(match_pair)
        if fuzz_score == 100:
            match_pair = (x_formatted, y_formatted, fuzz_score)
            confirmed_merge_typo_list.append(match_pair)

    # print("UCL: ", unconfirmed_merge_typo_list)
    # print("CL: ", confirmed_merge_typo_list)
    return unconfirmed_merge_typo_list, confirmed_merge_typo_list


if __name__ == '__main__':
    """ 
    Typo analysis pipeline.... and find possible lexical attr_type merges.
    """
    print("Analyzing attribute types...")


    # Commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--attr_type_file_path', default="../master-data/cocoa_facets.csv")
    # parser.add_argument('--no_typo_attr_type_file_path', default="../master-data/data-to-review/SomeFileName")
    parser.add_argument('--num_attr_review', default=26610, help="Number of Attributes to analyze their values")
    args = parser.parse_args()

    # Get attr_type file with count of attr per type
    attribute_type_dict = read_attr_type_file()

    # Check for typos
    no_typos, at_typos = check_for_typos(attribute_type_dict)
    print("** No typos:", len(no_typos), "Typos:", len(at_typos))

    # Check for fuzzy matches amongst attr_types with no typos
    no_typos_all_matches = check_for_fuzzy_matches(no_typos)

    confirmed_merge_pairs, unconfirmed_merge_pairs = secondary_fuzzy_match_check(no_typos_all_matches)
    print("** Confirmed merge pairs in no typos: ", len(confirmed_merge_pairs))
    # print("Confirmed: ", confirmed_merge_pairs)
    print("** Unconfirmed merge pairs in no typos: ", len(unconfirmed_merge_pairs))

    # Check for matches between confirmed merge attribute types
    # and attribute types with typos
    more_merges_to_confirmed = check_for_fuzzy_matches_between_confirmed_and_typo_group(confirmed_merge_pairs, at_typos)
    print("** More possible merges between no typos(confirmed merge group) and typos group: ", len(more_merges_to_confirmed), "\n")

    # Check for matches between attribute types in unconfirmed_merge_pairs set 
    # and those in the set with typos
    more_unconf_merges_between_unconfirmednotypos_and_typos, more_conf_merges_between_unconfirmed_and_typos = check_for_fuzzy_matches_between_unconfirmed_and_typo_group(unconfirmed_merge_pairs, at_typos)
    print("** More possible merges between no typo(unconfirmed) and typos group: ", len(more_unconf_merges_between_unconfirmednotypos_and_typos))
    print("** More _confirmed_ merges with no typo merge set: ", len(more_conf_merges_between_unconfirmed_and_typos), "\n")


    # Check for fuzzy matches amongst typos list
    typos_all_matches = check_for_fuzzy_matches(at_typos)
    typos_confirmed_merge_pairs, typos_unconfirmed_merge_pairs = secondary_fuzzy_match_check(typos_all_matches)
    print("** Confirmed Typo merge pairs: ", len(typos_confirmed_merge_pairs))
    print("** Unconfirmed Typo merge pairs: ", len(typos_unconfirmed_merge_pairs))


    # Output data to files
    TIMESTAMP = get_timestamp()
    with open("no_typos_confirmed_merges_"+TIMESTAMP+".csv", "w") as confirmed_merge_no_typos_out:
        csvout = csv.writer(confirmed_merge_no_typos_out)
        for merge_pair in confirmed_merge_pairs:
            csvout.writerow([merge_pair[0], merge_pair[1], "no_typos"])
        
        for mmtc in more_merges_to_confirmed:
            csvout.writerow([mmtc[0], mmtc[1], "pair_with_typo"])
   



