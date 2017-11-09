import re

import nltk
from nltk import wordpunct_tokenize
from nltk import WordNetLemmatizer
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.corpus import wordnet


class AttrTypeValidator:
    """
    Check if attribute type is number or a set of DNA sequence characters.
    """
    def __init__(self, attr_type):
        self.data = attr_type
        

    def check_for_numbers(self):
        RE_D = re.compile('\d')
        if RE_D.search(self.data):
            return True
        else:
            return False


    def check_for_sequence_strings(self):
        formatted_attr_type = self.data.lower().strip()
        token_list = formatted_attr_type.split()

        sequence_string_characters = set('agct')

        if len(token_list) == 1 and len(token_list[0]) > 3 \
        and set(formatted_attr_type) <= sequence_string_characters:
            return True
        else:
            return False


class MergeValidator:
    """
    Secondary check to confirm merge using NLTK methods.
    """
    def __init__(self, attribute1, attribute2):
        self.attr1 = attribute1
        self.attr2 = attribute2
