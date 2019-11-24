# coding=utf-8
"""

"""

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '3/13' # DD/MM/YY

from corefgraph.resources.lambdas import list_checker, equality_checker, matcher, fail

# Extracted from CoreNLP

indefinite_articles = list_checker(("a", "an"))

quantifiers = list_checker(("not", "every", "any", "none", "everything", "anything", "nothing", "all", "enough"))

partitives = list_checker((
    "half", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "hundred", "thousand", "million", "billion", "tens", "dozens", "hundreds", "thousands", "millions", "billions",
    "group", "groups", "bunch", "number", "numbers", "pinch", "amount", "amount", "total", "all", "mile",
    "miles", "pounds"))

partitive_particle = equality_checker("of")