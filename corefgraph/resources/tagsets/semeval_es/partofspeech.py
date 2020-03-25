# coding=utf-8
from corefgraph.resources.lambdas import equality_checker, matcher, fail

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


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
pronoun = matcher(r"^D?P")
personal_pronoun = matcher(r"^PP")
relative_pronoun = matcher(r"^PR")
interrogative_pronoun = matcher(r"^PT")
mention_pronoun = matcher(r"P[PXRL]|^DP") 

# Nouns
singular_common_noun = matcher(r"^NC.S")
plural_common_noun = matcher(r"^NC.P")
common_noun = matcher(r"^NC")
proper_noun = matcher(r"^NP")
noun = matcher(r"^N")

# Verbs
verb = matcher(r"^V")
modal = fail()
mod_forms = matcher(r"NVZA")
indefinites = matcher(r"^.I")

# Enumerations
enumerable_mention_words = noun

conjunction = matcher(r"^CC")
interjection = matcher("^I")
cardinal = matcher("^Z")


# Determinant
determinant = matcher("^D[^I]")
indefinite = matcher("^.I")

head_rules = matcher("^N")
