# coding=utf-8
from corefgraph.resources.lambdas import equality_checker, matcher, fail

__author__ = ''


# Features questions
female = matcher(".*FEM.*")
male = matcher(".*MASC*")
neutral = fail()

singular = matcher(".*SING.*")
plural = matcher(".*PLUR.*")

animate = fail()
inanimate = fail()

# Adjectives
adjective = matcher("^ADJ.*")


# Pronouns
pronoun = matcher("^PRON.*")
personal_pronoun = matcher("^PRON.*PRS.*")
relative_pronoun = matcher("^PRON.*REL.*")
interrogative_pronoun = matcher("^PRON.*INT.*")
mention_pronoun = lambda x: relative_pronoun(x) or personal_pronoun(x)

# Nouns
singular_common_noun = matcher("^NOUN.*SING.*")
plural_common_noun = matcher("^NOUN.*PLUR.*")
common_noun = matcher("^NOUN.*")
proper_noun = matcher("^PROPN.*")
noun = matcher("^PROPN|^NOUN")

# Verbs
verb = matcher("^VERB")
modal = equality_checker("^AUX")
mod_forms = lambda x: common_noun(x) or adjective(x) or verb(x) or cardinal(x)
indefinites = fail()

# Enumerations
enumerable_mention_words = noun

conjunction = equality_checker("CONJ")
interjection = equality_checker("INTERJ")
cardinal = equality_checker("CD")

# Determinant
determinant = lambda x: not verb(x) and matcher("DET")
indefinite = lambda x: not verb(x) and matcher("IND")

head_rules = noun