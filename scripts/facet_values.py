from functools import wraps
from time import time
import argparse
import requests, json
import datetime
import csv
import urllib
import os
import time as t



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
    
    print(len(attribute_type_dict.keys()))
    return attribute_type_dict


@timing
def get_facet_values(attr_type):
    """
    Get all facet/attribute type values and their usage count from Solr.
    """
    TIMESTAMP = get_timestamp()

    filename = "facet_value_results_"+TIMESTAMP+".csv"
    save_directory_path = "../master-data"
    completeName = os.path.join(save_directory_path, filename)

    outfile = open(completeName, "w")

    all_attribute_types = attribute_type_dict.keys()
    attr_type_count = 0
    start = -1

    all_facet_results = {}
    for attr_type in all_attribute_types:
        attr_type_count += 1
        start += 1

        if attr_type_count <= int(args.num_attr_review):
            # print "\n** Attribute Type("+ str(attr_type_count) +"): ", attr_type, attribute_type_dict[attr_type]
            
            search_facets = []
            if start % 5 == 0:
                end = start + 5
                print(all_attribute_types[start:end])
                # Search Solr with 5 attribute types
                search_facets = all_attribute_types[start:end]

                values = _get_attr_values(search_facets)
                # print type(values), values
                all_facet_results.update(values)
    
    # write ols search results for attr_trype to file
    print "** All Results: ", all_facet_results
    json.dump(all_facet_results, outfile)
    outfile.close()


def _get_attr_values(facets):
    """
    Use Solr web service calls to get all values and usage count.
    """
    print("** Facets: " ,facets)
    facet1 = urllib.quote(facets[0])
    facet2 = urllib.quote(facets[1])
    facet3 = urllib.quote(facets[2])
    facet4 = urllib.quote(facets[3])
    facet5 = urllib.quote(facets[4])


    # facet = urllib.quote(facet)

    # SOLR_COCOA_URL = "http://beans.ebi.ac.uk:8989/solr/samples/select?" \
    #             "q=*%3A*&rows=0&wt=json&indent=true&facet=true&" \
    #             "facet.field={facet:s}".format(facet=facet)
    
    headers = {
        'User-Agent': 'biosamples-curation',
        'From': 'twhetzel@ebi.ac.uk'
    }

    # NEW SOLR URL FORMAT
    NEW_SOLR_COCOA_URL = "http://cocoa.ebi.ac.uk:8989/solr/merged/select?" \
                "q=*%3A*&rows=0&wt=json&indent=true&facet=true&" \
                "facet.field={facet1}&facet.field={facet2}&" \
                "facet.field={facet3}&facet.field={facet4}&" \
                "facet.field={facet5}&facet.mincount=0&" \
                "facet.limit=-1".format(facet1=facet1, facet2=facet2, \
                    facet3=facet3, facet4=facet4, facet5=facet5)


    print "Sending request...", NEW_SOLR_COCOA_URL

    t.sleep(0.2)

    facet_results = {}
    try:
        response = requests.get(NEW_SOLR_COCOA_URL, headers=headers)
        if response.status_code == 200:
            results = json.loads(response.content)
            # print results
            if results:
                # values = results["facet_counts"]["facet_fields"][facet]
                values = results["facet_counts"]["facet_fields"]
                # print values
                # facet_results[facet] = values
                # return facet_results
                return values
        else:
            print response.status_code

    except requests.exceptions.RequestException as e:
        print e





if __name__ == '__main__':
    print "Getting facet values from Solr..."

    # Commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--attr_type_file_path', default="/Users/twhetzel/git/biosamples-data-curation/master-data/cocoa_facets.csv")
    parser.add_argument('--num_attr_review', default=26610, help="Number of Attributes to search Biosample Solr.")
    args = parser.parse_args()

    # Read in file of attribute types
    attribute_type_dict = read_attr_type_file()

    # Get values 
    get_facet_values(attribute_type_dict)


