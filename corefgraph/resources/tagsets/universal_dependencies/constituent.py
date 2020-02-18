# coding=utf-8
from corefgraph.resources.lambdas import equality_checker, list_checker, matcher, fail


__author__ = 'Valeria Quochi <valeria.quochi@ilc.cnr.it>'
__date__ = '5/16/2013'

# Is a root constituent
root = list_checker(("root", "top", "ROOT", "TOP"))

"""Clause introduced by a (possibly empty) subordinating conjunction."""


# Is a clause
clause = list_checker(("S", "SBAR",))

# Is a Noun phrase
noun_phrase = equality_checker("NP")

# Is a Verb phrase
verb_phrase = equality_checker("VP")

particle_constituents = fail()
past_participle_verb = equality_checker("VBN")

interjections = fail()
simple_or_sub_phrase = list_checker(("S", "SBAR"))
ner_constituent = fail()
mention_constituents = matcher("NP.*")
head_rules = list_checker(("SN", "SUJ", "GRUP.NOM"))
