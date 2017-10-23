# Lexical Analysis Pipeline

## Description
Analyzes facets from EBI Biosamples to identify pairs of facets to merge. Facets are first split into 
groups of facets that contain typos and those that do not. The group of facets with no typos are examined
for merge pairs using fuzzy matching followed by use of lemmatization of tokens using the WordNetLemmatizer
and morphy from NLTK. This group is then compared to the typo group to find additional merger pairs.

## Prerequisites
See `requirements.txt` for full list of modules. See http://www.nltk.org/data.html for details on installing data for NLTK.

## Usage 
`python lexical_merge_analysis_pipeline.py`
See commandline args for additional parameters.

## Output
Two CSV files that contain a list of facet pairs to merge. The file "merge_confirmed.csv" contains high confidence merge pairs, while "merge_after_manual_review.csv" contains lower confidence merge pairs that require fuurther review.


