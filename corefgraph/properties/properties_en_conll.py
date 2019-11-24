# coding=utf-8

""" General properties
language is the name of the package stored in resources/languages that contains language resources and is expected to be
 named after language code. Example:

    # Spanish
    lang = "es"

this module contains all modules and text files needed for each language.



Tag_set values are the names of the packages for each annotation language used in the corpus. Currently, the system uses
POS, Syntactic Constituents ,NER types  and dependency tag sets. The packages are stored in in resources/tagsets are
named after their annotation and can contains one or more levels of annotation. Each module in the  package is a level
of annotation and is named: constituent, namedentities, partofspeech or dependency. Example:

    pos_tag_set = "penntreebank"
    constituent_tag_set = "penntreebank"
    ner_tag_set = "conll"
    dep_tag_set = "standford"

"""

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


lang = "en"

pos_tag_set = "penntreebank"
constituent_tag_set = "penntreebank"
ner_tag_set = "conll"
dep_tag_set = "standford"
