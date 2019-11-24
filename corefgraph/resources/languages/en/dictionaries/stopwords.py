# coding=utf-8
""" List of Stopwords  and other meaningless or confusing words of english
"""
from corefgraph.resources.lambdas import list_checker, equality_checker, matcher, fail

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


# List extracted from Stanford CoreNLP

stop_words = list_checker((
    "a", "an", "the", "of", "at", "on", "upon", "in", "to", "from", "out", "as", "so",
    "such", "or", "and", "those", "this", "these", "that", "for", ",", "is", "was",
    "am", "are", "'s", "been", "were"))

extended_stop_words = list_checker((
    "the", "this", "mr.", "miss", "mrs.", "dr.", "ms.", "inc.", "ltd.", "corp.", "'s", ",", "."))
    # , "..", "..", "-", "''", '"', "-"))

# all pronouns are added to stop_word

common_NE_subfixes = list_checker(("corp", "co", "inc", "ltd"))

non_words = list_checker(("mm", "hmm", "ahem", "um"))


_invalid = list_checker(("u.s.", "u.k", "u.s.s.r.", "there", "ltd."))
_invalid_start_word_a = matcher("'s.*")
_invalid_start_word_b = matcher("etc.*")
_invalid_end_a = matcher(".*etc.")
invalid_words = lambda x: _invalid(x) or _invalid_end_a(x) or _invalid_start_word_a(x) or _invalid_start_word_b(x) \
                          or non_words(x)

location_modifiers = list_checker(("east", "west", "north", "south", "eastern", "western", "northern", "southern",
                                   "upper", "lower"))

unreliable = list_checker(("this",))

speaking_begin = list_checker(("``",))
speaking_end = list_checker(("''",))
speaking_ambiguous = list_checker(('"',))
