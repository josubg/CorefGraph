# coding=utf-8
from corefgraph.resources.lambdas import equality_checker, fail, matcher

__author__ = 'Valeria Quochi <valeria.quochi@ilc.cnr.it>'
__date__ = '5/16/2013'

# features questions
female = matcher(".*FEM.*")
male = matcher(".*MASC.*")
neutral = fail()
singular = equality_checker(".*SING.*")
plural = equality_checker(".*PLUR.*")
animate = fail()
inanimate = fail()


# Adjectives
adjective = matcher("^ADJ.*")


# pronouns
personal_pronoun = matcher("^PRON.*PRS")
relative_pronoun = matcher("^PRON.*REL")
pronoun = matcher("^PRON.*")
mention_pronoun = lambda x: relative_pronoun(x) or personal_pronoun(x)

singular_common_noun = equality_checker("^NOUN.*SING.*")
plural_common_noun = equality_checker("^NOUN.*PLUR.*")
proper_nouns = matcher("^PROPN")
noun = lambda x: proper_nouns(x) or matcher("^NOUN")

verbs = matcher("^VERB")
modals = equality_checker("^AUX")
mod_forms = lambda x: singular_common_noun(x) or plural_common_noun(x) or adjective(x) or verbs(x) or cardinal(x)


# enumerations
enumerable_mention_words = noun

conjunction = equality_checker("CONJ")
interjections = equality_checker("INTERJ")
cardinal = equality_checker("CD")
# wh_words = lambda x: not verbs(x) and matcher("DE$")


determinant = lambda x: not verbs(x) and matcher("DET.*")
indefinite = lambda x: not verbs(x) and matcher(".*IND.*")

head_rules = matcher("#^NOU.*")
