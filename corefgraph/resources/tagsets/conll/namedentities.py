# coding=utf-8


from corefgraph.resources.lambdas import list_checker, fail


__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

_no_ner = "O"

all = lambda x: x != _no_ner and x is not None and x != ""

# Classic 3 types useful in some cases
person = list_checker(("PERSON", "PER"))
organization = list_checker(("ORG", "ORGANIZATION"))
location = list_checker(("LOCATION", "LOC"))
other = list_checker(("MISC", "OTHER"))


singular = lambda x: all(x) and not organization(x)
plural = fail()

animate = list_checker(("PERSON", "PER"))
inanimate = list_checker(("FACILITY", "FAC", "NORP", "LOCATION", "LOC",
                          "PRODUCT", "EVENT", "ORGANIZATION", "ORG",
                          "WORK OF ART", "LAW", "LANGUAGE", "DATE", "TIME",
                          "PERCENT", "MONEY", "NUMBER", "QUANTITY",
                          "ORDINAL", "CARDINAL", "MISC", "GPE", "WEA", "NML"))

# NE types that denotes mention
mention_ner = lambda x: (x is not None) and (
    x not in ("O", "QUANTITY", "CARDINAL", "PERCENT", "DATE", "DURATION", "TIME", "SET"))
# NE types that must be filtered from mention candidates
# TODO NORP,"MONEY" in no NER improves results


