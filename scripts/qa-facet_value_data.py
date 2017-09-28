import argparse
import glob, os
import re, csv
from tqdm import tqdm


def get_attr_type_value_file_names():
    """
    Get list of all filenames to examine.
    """
    all_value_file_names = []
    modified_all_value_file_names = []
    cwd = os.getcwd()
    # Change to dir with result files to analyze
    os.chdir(args.attr_values_dir)
    
    for filename in glob.glob("*.json"):
        all_value_file_names.append(filename)

    # Modfiy file names to match attribute facet name format, e.g. barcode_facet
    for facet in all_value_file_names:
        facet, junk = facet.split("_results")
        # print "Modified: ", facet
        modified_all_value_file_names.append(facet)

    # Return to current working directory
    os.chdir(cwd)
    # return all_value_file_names
    return modified_all_value_file_names


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
        if attr_type not in file_list:
            # Print missing to file
            csvout = csv.writer(outfile)
            csvout.writerow([attr_type, 0])

    outfile.close        


if __name__ == '__main__':
    print "Starting QA..."

    # Commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--attr_type_file_path', default="/vagrant/biosamples-data-curation/master-data/cocoa_facets.csv")
    parser.add_argument('--attr_values_dir', default="/vagrant/biosamples-data-curation/master-data/facet_values")
    args = parser.parse_args()

    # Get list of files with attribute value results
    all_value_file_names = get_attr_type_value_file_names()

    # Read in file of attribute types
    attribute_type_dict = read_attr_type_file()

    # Confirm/find missing value files based on attr_type list
    find_missing_facet_value_results(all_value_file_names, attribute_type_dict)
    



