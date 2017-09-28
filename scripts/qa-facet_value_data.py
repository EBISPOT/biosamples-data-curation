import argparse
import glob, os
import re, csv
from tqdm import tqdm


def get_attr_type_value_file_names():
    """
    Get list of all filenames to examine.
    """
    all_value_file_names = []
    cwd = os.getcwd()
    # Change to dir with result files to analyze
    os.chdir(args.attr_values_dir)
    
    for filename in glob.glob("*.json"):
        all_value_file_names.append(filename)
    # Return to current working directory
    os.chdir(cwd)
    return all_value_file_names


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
    
    # print(len(attribute_type_dict.keys()))
    return attribute_type_dict


def find_missing_facet_value_results(file_list, attr_type_data):
    """
    For each attribute type, confirm there is a values file.
    """
    attribute_types = attr_type_data.keys()
    
    missing = []
    found = []
    filename = "missing_attribute_type_values.csv"
    save_directory_path = "../master-data/"
    completeName = os.path.join(save_directory_path, filename)
    outfile = open(completeName, "w")
    
    for attr_type in tqdm(attribute_types, ncols=120):
        attr_type = attr_type+"_results.json"
        if attr_type not in file_list:
            attr_type, junk = attr_type.split('_results.json')
            # Print missing to file
            csvout = csv.writer(outfile)
            csvout.writerow([attr_type, 0])

    outfile.close        


if __name__ == '__main__':
    print "Starting QA..."

    # Commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--attr_type_file_path', default="/Users/twhetzel/git/biosamples-data-curation/master-data/cocoa_facets.csv")
    parser.add_argument('--attr_values_dir', default="/Users/twhetzel/git/biosamples-data-curation/master-data/facet_values")
    # parser.add_argument('--attr_type_file_path', default="/Users/twhetzel/git/biosamples-data-mining/data_results/unique_attr_types_2017-06-20_14-31-00.csv")
    # parser.add_argument('--search_content', default="attr_type", help="Indicates what content to search. \
    #                                         Possible values are attr_type, values, both.")
    # parser.add_argument('--num_attr_review', default=16000, help="Number of Attributes to search OLS.")
    # parser.add_argument('--restart_attr_count', default=0, help="Count of which attribute to re-start OLS search \
                                            # when values are used for search.")
    args = parser.parse_args()

    # Get list of files with attribute value results
    all_value_file_names = get_attr_type_value_file_names()

    # Read in file of attribute types
    attribute_type_dict = read_attr_type_file()

    # Confirm/find missing value files based on attr_type list
    find_missing_facet_value_results(all_value_file_names, attribute_type_dict)
    



