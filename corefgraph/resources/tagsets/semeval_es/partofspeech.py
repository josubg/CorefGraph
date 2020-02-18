# coding=utf-8
""" Ancora POS tag checkers.

Each elements in this module is a function that check if a POS tag.

Elements starting with _ is only for internal use.
"""
from corefgraph.resources.lambdas import list_checker, equality_checker, matcher, fail

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

_pronouns = matcher(r"^P")
_possessive_determinant = matcher("^DP")
_possessive_pronouns = matcher(r"^PX")
_personal_pronouns = matcher(r"^PP")
_elliptic_pronoun = matcher(r"^PL")

# Features questions
female = matcher(r"^[ADP]..F|^N.F|^V.....F")
male = matcher(r"^[ADPS]..M|^N.M|^V.....M")
neutral = matcher(r"^[ADP]..N")

singular = matcher(r"^[ADPS]...S|^N..S|^V....S")
plural = matcher(r"^[ADPS]...P|^N..P|^V....P")

animate = fail()
inanimate = fail()

# Adjectives
adjective = matcher(r"^A")


# Pronouns
pronoun = lambda x: _pronouns(x) or _possessive_determinant(x)
relative_pronoun = matcher(r"^PR")
mention_pronoun = lambda x: _personal_pronouns(x) or _possessive_pronouns(x) or _possessive_determinant(x) \
    or relative_pronoun(x) or _elliptic_pronoun(x)

# Nouns
singular_common_noun = lambda x: common_nouns(x) and singular(x)
plural_common_noun = lambda x: common_nouns(x) and plural(x)
common_nouns = matcher(r"^NC")
proper_nouns = matcher(r"^NP")
noun = matcher(r"^N")

# Verbs
verb = matcher(r"^V")
modal = fail()

mod_forms = lambda x: noun(x) or adjective(x) or verb(x) or cardinal(x)
indefinites = matcher(r"^.I")

# Enumerations
enumerable_mention_words = lambda x: noun(x)
#subordinating_conjunction = fail()

conjunction = matcher(r"^CC")
interjection = matcher("^I")
cardinal = matcher("^Z")

# TODO change to Semeval tagset
head_rules = matcher("^N")
# Language specifics
# Determinant
determinant = matcher("^D")
interrogative_pronoun = matcher(r"^PT")

