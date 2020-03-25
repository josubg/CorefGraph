# coding=utf-8
from corefgraph.resources.lambdas import equality_checker, list_checker, matcher, fail


__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


# Is a root constituent
root = list_checker(("root", "top", "ROOT", "TOP"))


# Is a clause
clause = list_checker(("S", "SENTENCE"))

# Is a simple or subordinated clause
simple_or_sub_phrase = clause

# Is a Noun phrase
noun_phrase = list_checker(("SN","SUJ", "GRUP.NOM"))

# Is a Verb phrase
verb_phrase = equality_checker("GRUP.VERB")

# Is a Adverbial phrase
adverbial_phrase = equality_checker("SADV")

# Is a complement direct
complement_direct = equality_checker("CD")

# Is a particle constituent
particle_constituent = fail()

# Is a past_participle verb constituent
past_participle_verb = fail()

# Is an interjection constituent
interjection = equality_checker("INTERJECCIÓ")

# Is a NER annotated into semantic tree
ner_constituent = fail()

preposition = equality_checker("PREP")

enumerable = noun_phrase

head_rules = noun_phrase

# The mention is a plausible constituent
mention_constituents = lambda x: noun_phrase(x) or complement_direct(x)

