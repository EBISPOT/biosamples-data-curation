from functools import wraps
from time import time
import argparse
import requests, json
import datetime
import csv
import urllib
import os



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
    save_directory_path = "/Users/twhetzel/git/biosamples-data-curation/"
    data_directory = "master-data"
    completeName = os.path.join(save_directory_path, data_directory, filename)

    outfile = open(completeName, "w")

    all_attribute_types = attribute_type_dict.keys()
    attr_type_count = 0

    all_facet_results = []
    for attr_type in all_attribute_types:
        attr_type_count += 1

        if attr_type_count <= int(args.num_attr_review):
            print "\n** Attribute Type("+ str(attr_type_count) +"): ", attr_type, attribute_type_dict[attr_type]

            values = _get_attr_values(attr_type)
            # print values
            all_facet_results.append(values)

    
    # write ols search results for attr_trype to file
    json.dump(all_facet_results, outfile)
    outfile.close()


def _get_attr_values(facet):
    """
    Use Solr web service calls to get all values and usage count.
    """
    facet = urllib.quote(facet)
    SOLR_COCOA_URL = "http://cocoa.ebi.ac.uk:8989/solr/samples/select?" \
                "q=*%3A*&rows=0&wt=json&indent=true&facet=true&" \
                "facet.field={facet:s}".format(facet=facet)
    headers = {
        'User-Agent': 'biosamples-curation',
        'From': 'twhetzel@ebi.ac.uk'
    }

    print "Sending request...", SOLR_COCOA_URL

    facet_results = {}
    try:
        response = requests.get(SOLR_COCOA_URL, headers=headers)
        if response.status_code == 200:
            results = json.loads(response.content)
            # print results
            if results:
                values = results["facet_counts"]["facet_fields"][facet]
                # print values
                facet_results[facet] = values
                return facet_results
        else:
            print response.status_code

    except requests.exceptions.RequestException as e:
        print e





if __name__ == '__main__':
    print "Getting facet values from Solr..."

    # Commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--attr_type_file_path', default="/Users/twhetzel/git/biosamples-data-curation/master-data/cocoa_facets.csv")
    parser.add_argument('--num_attr_review', default=26610, help="Number of Attributes to search OLS.")
    args = parser.parse_args()

    # Read in file of attribute types
    attribute_type_dict = read_attr_type_file()

    # Get values 
    get_facet_values(attribute_type_dict)


