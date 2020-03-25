# coding=utf-8
from corefgraph.resources.lambdas import equality_checker, list_checker, matcher, fail


__author__ = 'Valeria Quochi <valeria.quochi@ilc.cnr.it>'


# Is a root constituent
root = list_checker(("root", "top", "ROOT", "TOP"))


# Is a clause
clause = list_checker(("S", "SBAR",))

# Is a simple or subordinated clause
simple_or_sub_phrase = clause

# Is a Noun phrase
noun_phrase = equality_checker("NP")

# Is a Verb phrase
verb_phrase = equality_checker("VP")

# Is a Adverbial phrase
adverbial_phrase = fail()

# Is a complement direct
complement_direct = list_checker(("CD",))

# Is a particle constituent
particle_constituent = fail()

# Is a past_participle verb constituent
past_participle_verb = equality_checker("VBN")

# Is an interjection constituent
interjection = fail()

# Is a NER annotated into semantic tree
ner_constituent = fail()

preposition = fail()

enumerable = noun_phrase

head_rules = noun_phrase

# The mention is a plausible constituent
mention_constituents = matcher("NP.*")

