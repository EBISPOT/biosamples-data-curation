from functools import wraps
from time import time
import argparse
import requests, json
import datetime
import csv
import urllib
import os
import time as t
import glob, os
from collections import Counter
import string, random


def timing(f):
    """
    Create wrapper to report time of functions.
    """
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print 'Function: %r took: %2.2f sec, %2.2f min' % \
          (f.__name__, te-ts, (te-ts)/60)
        return result
    return wrap


def read_attr_type_file():
    """ 
    Read file of common attributes. 
    """
    with open(args.attr_type_file_path, 'r') as f:
        content = f.readlines()

    # Strip lines of newline/return characters in csv file
    content = [x.strip(' \t\n\r') for x in content]

    # Generate dictionary of types and their count
    attribute_type_dict = {}
    for item in content:
        attr_type, value = item.split(',')
        if attr_type != '':
            attribute_type_dict[attr_type.strip()] = value.strip()
    
    print "- Number of Facets: ", len(attribute_type_dict.keys())
    return attribute_type_dict


@timing
def get_facet_values(attr_type):
    """
    Get all facet/attribute type values and their usage count from Solr.
    """

    all_attribute_types = attr_type.keys()
    attr_type_count = -1
    save_directory_path = "../master-data/facet_values/"

    for attr_type in all_attribute_types:
        attr_type_count += 1
        start = attr_type_count

        num_attr_review = int(args.num_attr_review) + int(args.restart_attr_count)
        if attr_type_count >= int(args.restart_attr_count) and attr_type_count <= num_attr_review:
            # print "\n** Attribute Type("+ str(attr_type_count) +"): ", attr_type, attribute_type_dict[attr_type]
            
            search_facets = []

            if start % 5 == 0:
                end = start + 5
                print "\n** Facet slice: ", all_attribute_types[start:end], start, end
                # Slice list to search Solr with 5 attribute types
                search_facets = all_attribute_types[start:end]

                result_values = _get_attr_values(search_facets)
                
                # Print facet search results to files
                for key, values in result_values.iteritems():
                    individual_facet_results = {}

                    # Do not print out file for "test1234_facet"
                    if key == "test1234_facet":
                        pass
                    else:
                        # Create unique tag since some facet names are repeated and 
                        # some file systems can only have unique case insensitive filenames
                        UNIQUE_TAG = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(8))

                        filename = key+"_results-"+UNIQUE_TAG+".json"
                        
                        completeName = os.path.join(save_directory_path, filename)
                        outfile = open(completeName, "w")

                        individual_facet_results[key] = values
                        json.dump(individual_facet_results, outfile)


def _get_attr_values(facets):
    """
    Use Solr web service calls to get all values and usage count.
    """
    # TODO: Better handle when "facets" has less than 5 search terms
    # Temporary solution is set to default value

    # Create "facets" list that contains 5 elements
    for i in range(5):
        if i < len(facets):
            facets[i] = urllib.quote(facets[i])
        else:
            facets.append("test1234_facet")
    

    # Format search values for use in URL
    if facets[0]:
        facet0 = urllib.quote(facets[0])
    if facets[1]:
        facet1 = urllib.quote(facets[1])
    if facets[2]:
        facet2 = urllib.quote(facets[2])
    if facets[3]:
        facet3 = urllib.quote(facets[3])
    if facets[4]:
        facet4 = urllib.quote(facets[4])

    
    headers = {
        'User-Agent': 'biosamples-curation',
        'From': 'twhetzel@ebi.ac.uk'
    }

    # NEW SOLR URL FORMAT
    NEW_SOLR_URL = "http://beans.ebi.ac.uk:8989/solr/merged/select?" \
                "q=*%3A*&rows=0&wt=json&indent=true&facet=true&" \
                "facet.field={facet0}&facet.field={facet1}&" \
                "facet.field={facet2}&facet.field={facet3}&" \
                "facet.field={facet4}&facet.mincount=0&" \
                "facet.limit=-1".format(facet0=facet0, facet1=facet1, \
                    facet2=facet2, facet3=facet3, facet4=facet4)


    facet_results = {}
    dummy_results = {}
    try:
        response = requests.get(NEW_SOLR_URL, headers=headers)
        if response.status_code == 200:
            results = json.loads(response.content)
            if results:
                values = results["facet_counts"]["facet_fields"]
                return values
        else:
            print "** Failed with error: ", response.status_code
            
            dummy_results[facet0] = [response.status_code, 0]
            dummy_results[facet1] = [response.status_code, 0]
            dummy_results[facet2] = [response.status_code, 0]
            dummy_results[facet3] = [response.status_code, 0]
            dummy_results[facet4] = [response.status_code, 0]
            
            return dummy_results

    except requests.exceptions.RequestException as e:
        print e


if __name__ == '__main__':
    print "Getting facet values from Solr..."

    # Commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--attr_type_file_path', default="../master-data/cocoa_facets.csv")
    parser.add_argument('--attr_values_dir', default="../master-data/facet_values")
    parser.add_argument('--num_attr_review', default=26610, help="Number of Attributes to search Biosample Solr.")
    parser.add_argument('--restart_attr_count', default=0, help="Count of attribute types to restart Solr queries.")
    args = parser.parse_args()


    # Read in file of attribute types
    attribute_type_dict = read_attr_type_file()

    # Get values 
    get_facet_values(attribute_type_dict)


