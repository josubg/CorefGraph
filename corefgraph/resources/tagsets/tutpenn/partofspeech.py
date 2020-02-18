# coding=utf-8
from corefgraph.resources.lambdas import equality_checker, fail, matcher

__author__ = 'Valeria Quochi <valeria.quochi@ilc.cnr.it>'
__date__ = '5/16/2013'

# features questions
female = fail()
male = fail()
neutral = fail()
singular = equality_checker("^NOU_CS")
plural = equality_checker("^NOU_CP")
animate = fail()
inanimate = fail()


# Adjectives
adjective = matcher("^ADJ.*")


# pronouns
personal_pronoun = matcher("^PRO~PE")
relative_pronoun = matcher("^PRO~RE")
pronoun = matcher("^PRO")
mention_pronoun = lambda x: relative_pronoun(x) or personal_pronoun(x)

singular_common_noun = equality_checker("^NOU_CS")
plural_common_noun = equality_checker("^NOU_CP")
proper_nouns = matcher("^NOU~PR")
noun = matcher("^NOU.*")

verbs = matcher("^V.*")
modals = equality_checker("^VMO.*")
mod_forms = lambda x: singular_common_noun(x) or plural_common_noun(x) or adjective(x) or verbs(x) or cardinal(x)


# enumerations
enumerable_mention_words = matcher("^NOU.C*")

conjunction = equality_checker("CONJ")
interjections = equality_checker("INTERJ")
cardinal = equality_checker("CD")
wh_words = lambda x: not verbs(x) and matcher("DE$")


determinant = lambda x: not verbs(x) and matcher("DE$")
indefinite = lambda x: not verbs(x) and matcher("IN$")

head_rules = matcher("#^NOU.*")
