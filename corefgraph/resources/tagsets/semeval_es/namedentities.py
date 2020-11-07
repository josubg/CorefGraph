# coding=utf-8
""" Named entity labels used in Semeval 2010.

"""
from corefgraph.resources.lambdas import list_checker, fail

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

all = lambda x: not((x == "O") or (x is None) or (x == ""))

# Classic 3 types useful in some cases
person = list_checker(("PERSON", "PER", "person"))
organization = list_checker(("ORG", "ORGANIZATION", "org"))
location = list_checker(("LOCATION", "LOC", "loc"))
#other = list_checker(("MISC", "OTHER", "other"))

singular = lambda x: all(x) and not organization(x)
plural = fail()

animate = person
inanimate = location


# NE types that denotes mention
mention_ner = all

# NE types that must be filtered from mention candidates
no_mention_ner = lambda: False
