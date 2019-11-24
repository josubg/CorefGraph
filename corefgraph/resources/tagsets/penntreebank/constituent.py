# coding=utf-8

from corefgraph.resources.lambdas import list_checker, equality_checker, matcher, fail

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

# Is a root constituent
root = list_checker(("root", "top", "ROOT", "TOP"))

# Is a clause
clause = matcher("^S")

# Is a Noun phrase
noun_phrase = equality_checker("NP")

# Is a Noun phrase
#prepositional_phrase = equality_checker("SP")

# Is a Verb phrase
verb_phrase = equality_checker("VP")

# Is a particle constituent
particle_constituent = equality_checker("PRT")

# Is an interjection constituent
past_participle_verb = equality_checker("VBN")

# Is an interjection constituent
interjection = equality_checker("INTJ")


# Is a simple or subordinated clause
simple_or_sub_phrase = list_checker(("S", "SBAR"))

adjectival_phrase = list_checker(("ADJP",))

adverbial_phrase = list_checker(("ADVP",))

#TODO Remove this check
mention_constituents = matcher("^NP")

enumerable = list_checker(("^NP", "^NML"))

#head_rules = matcher("NP")