# coding=utf-8
""" List of Stopwords 
"""
from corefgraph.resources.lambdas import list_checker, equality_checker, matcher, fail

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


# List extracted from Stanford CoreNLP

stop_words = list_checker(('unes', 'una', 'uns', 'un', 'del', 'al', 'el', 'la', 'les', 'lo', 'de', 'en',
                           'sobre', 'per', 'dins', 'fins', 'desde', 'fora', 'com', 'així', 'tal', 'o', 'i', 'a',
                           'aquest', 'aquesta', 'aquelles', 'aquells', ',', 'es',
                           'era', 'sóc', 'eres', 'sido', 'eras'))

extended_stop_words = list_checker(("el", "la",  "sr", "sra", "srta", "dr", "ms.", "s.", "s.l.",
                                    "s.a", ",", "."))  # , "..", "..", "-", "''", '"', "-"))
# all pronouns are added to stop_word

common_NE_subfixes = list_checker(("s.a.", "s.l.", "s.a.l.", "s.l.l.", "s.c.", "s.com", "s.coop"))

non_words = list_checker(('ejem', 'ajá', 'hm', 'jo'))


invalid_words = list_checker(("sa", "sl", "etc", "dólars", "pesetes", "euros"))

location_modifiers = list_checker(("nord", "sud", "est", "oest", "adalt", "abaix"))

unreliable = list_checker(("_", "que", "su", "sus"))

speaking_begin = list_checker(("``",))
speaking_end = list_checker(("''",))
speaking_ambiguous = list_checker(('"', '-'))
