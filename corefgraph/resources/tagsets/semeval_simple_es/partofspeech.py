# coding=utf-8
""" Ancora POS tag checkers.

Each elements in this module is a function that check if a POS tag.

Elements starting with _ is only for internal use.
"""

from corefgraph.resources.lambdas import fail, matcher

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


_pronouns = matcher(r"pos=p")
_possessive = matcher(r".*postype=possessive")
_relative = matcher(r".*postype=relative")
_personal = matcher(r".*postype=personal")
_personal_pronouns = lambda x: _pronouns(x) and _personal(x)

# features questions
male = matcher(r".*gen=m")
female = matcher(r".*gen=f")
neutral = matcher(r".*gen=n")

singular = matcher(r".*num=s")
plural = matcher(r".*num=p")

animate = fail()
inanimate = fail()
# Adecjtives
adjectives = matcher(r"pos=a")

# Determinant
_possessive_determinant = matcher(".*postype=possessive")

#pronouns
#TODO Assure broad usage of these tags

pronouns = lambda x: _pronouns(x) or _possessive_determinant(x)
possessive_pronouns = lambda x: _pronouns(x) and _possessive(x)

relative_pronoun = lambda x: _pronouns(x) and _relative(x)
mention_pronouns = lambda x: _personal_pronouns(x) or possessive_pronouns(x) or _possessive_determinant(x) \
    or relative_pronoun(x)

#Nouns
_noun = matcher(r"pos=n")
_common = matcher(r".*postype=common")
_proper = matcher(r".*postype=proper")
noun = _noun
common_nouns = lambda x: _noun(x) and _common(x)
proper_nouns = lambda x: _noun(x) and _proper(x)
singular_common_noun = lambda x: common_nouns(x) and singular(x)
plural_common_noun = lambda x: common_nouns(x) and plural(x)

#Verbs
_aux = matcher(r".*postype=aux")
verbs = matcher(r"pos=v")
modals = lambda x:verbs(x) and _aux(x)

#TODO No hay cardinales
mod_forms = lambda x: noun(x) or adjectives(x) or verbs(x) or cardinal(x)
indefinites = matcher(r".*postype=indefinite")

# Enumerations
enumerable_mention_words = lambda x: proper_nouns(x)
wh_words = fail()
subordinating_conjunction = fail()
conjunctions = matcher(r".*postype=coordinating")

valid_inner_np = lambda x: conjunctions(x)

interjection = matcher(".*pos=interjecio")


cardinal = fail()

#TODO change to Semeval tagset
head_rules = matcher("^N")