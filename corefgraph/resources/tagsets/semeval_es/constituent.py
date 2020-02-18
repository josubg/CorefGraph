# coding=utf-8
from corefgraph.resources.lambdas import equality_checker, list_checker, matcher, fail


__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


# Is a root constituent
root = list_checker(("root", "top", "ROOT", "TOP"))

# Is a clause
clause = list_checker(("S", "SENTENCE"))

# Is a Noun phrase
noun_phrase = list_checker(("SN","SUJ", "GRUP.NOM"))

# Is a Verb phrase
verb_phrase = list_checker(("GRUP.VERB",))

# Is a complement direct
complement_direct = list_checker(("CD",))

# Is a particle constituent
particle_constituent = fail()

# Is a past_participle verb constituent
past_participle_verb = fail()

# Is an interjection constituent
interjection = equality_checker("INTERJECCIÓ")

# Is a NER annotated into semantic tree
ner_constituent = fail()

# Is a simple or subordinated clause
simple_or_sub_phrase = clause

preposition = list_checker(("PREP",))

adverbial_phrase = list_checker(("SADV",))

#TODO Remove this check

mention_constituents = lambda x: noun_phrase(x) or complement_direct(x)
enumerable = list_checker(("^SN",))

head_rules = list_checker(("SN","SUJ", "GRUP.NOM"))
