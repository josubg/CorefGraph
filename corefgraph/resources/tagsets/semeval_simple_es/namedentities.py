# coding=utf-8

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


from corefgraph.resources.lambdas import list_checker, equality_checker, matcher, fail

_no_ner = "O"

no_ner = lambda x: x == _no_ner or x is None or x == ""
all = lambda x: x != _no_ner and x is not None and x != ""

# Classic 3 types useful in some cases
person = list_checker(("person", "per"))
organization = list_checker(("org", "organization"))
location = list_checker(("location", "loc"))
other = list_checker(("misc", "other"))

singular = fail()# lambda x: all(x) and not organization(x)
plural = fail()# organization

animate = fail()#list_checker(("PERSON", "PER"))
inanimate = fail()#list_checker(("FACILITY", "FAC", "NORP", "LOCATION", "LOC", "PRODUCT", "EVENT", "ORGANIZATION", "ORG",
                  #        "WORK OF ART", "LAW", "LANGUAGE", "DATE", "TIME", "PERCENT", "MONEY", "NUMBER", "QUANTITY",
                  #        "ORDINAL", "CARDINAL", "MISC", "GPE", "WEA", "NML"))

# NE types that denotes mention
mention_ner = lambda x: x != _no_ner and x is not None and x != ""
mention_ner = list_checker(("person", "norp", "facility", "organization", "gpe", "nml", "location", "product", "event", "work of art",
                            "law", "language", "date", "time"))

# NE types that must be filtered from mention candidates
no_mention_ner = list_checker(("date",))


