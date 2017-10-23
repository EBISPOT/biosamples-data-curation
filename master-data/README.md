# Master Data

This directory contains the main input files for analysis by the lexical, statistical, semantic, and datatype modules.

## Files
* facet_values.zip
    * Contains 26,602 files, one file for each unique facet. Each file contains all unique values for the facet and their frequency. The data files are formatted as: 
    `{"1DayTreatment_facet": ["antibody", 12, "doxycycline", 23, "vehicle", 36]}`
    The data was generated on Oct.3, 2017 using the script `facet_values.py`.
* cocoa_facets.csv
    * Contains a CSV list of facets and their frequency.
* total_cooccurrence_matrix.json
