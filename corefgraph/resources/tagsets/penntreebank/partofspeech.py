# coding=utf-8
""" Penn treebank POS tag checkers.

Each elements in this module is a function that check if a POS tag.

Elements starting with _ is only for internal use.
"""
from corefgraph.resources.lambdas import list_checker, equality_checker, matcher, fail

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

# Inner usage only
_personal_pronoun = "PRP"
_possessive_pronoun = "PRP$"
_wh_pronoun = "WP"
_wh_possessive_pronoun = "WP$"
_wh_determiner = "WDT"
_wh_adverb = "WRB"
_wh_words = list_checker((_wh_pronoun, _wh_possessive_pronoun, _wh_determiner, _wh_adverb))
_verbs_list = ("VB", "VBD", "VBG", "VBN", "VBP ", "VBZ")
_modal = "MD"
_noun = "NN"
_noun_plural = "NNS"
_interjection = "UH"
_proper_noun = "NNP"
_proper_noun_plural = "NNPS"

_adjective = "JJ"
_adjective_comparative = "JJR"
_adjective_superlative = "JJS"

_conjunction = ("CC",)

# comma = equality_checker(",")

# Features questions
female = fail()
male = fail()
neutral = fail()

singular = matcher("^NNP?$")
plural = matcher("^NNP?S$")

animate = fail()
inanimate = fail()

# Adjectives
adjective = list_checker((_adjective,))

# Pronouns
pronoun = list_checker((_personal_pronoun, _possessive_pronoun, _wh_pronoun, _wh_possessive_pronoun))
relative_pronoun = list_checker((_wh_pronoun, _wh_possessive_pronoun))
mention_pronoun = matcher("^PRP")

# Nouns
singular_common_noun = equality_checker(_noun)
plural_common_noun = equality_checker(_noun_plural)
proper_nouns = list_checker((_proper_noun, _proper_noun_plural))
noun = lambda x: x is not None and (singular_common_noun(x) or plural_common_noun(x) or proper_nouns(x))

# Verbs
verb = list_checker(_verbs_list)
modal = equality_checker(_modal)

mod_forms = lambda x: x is not None and (x.startswith("N") or x.startswith("JJ") or x.startswith("V") or x == "CD")
indefinite = fail

# Enumerations
enumerable_mention_words = matcher("^NNP")

conjunction = list_checker(_conjunction)

interjection = equality_checker(_interjection)

cardinal = matcher("^CD")

head_rules = matcher("^N")

#subordinating_conjunction = equality_checker("IN")

verbs_past_particicle = matcher("VBN")

# Train
adjectives = list_checker((_adjective, _adjective_comparative, _adjective_superlative))
