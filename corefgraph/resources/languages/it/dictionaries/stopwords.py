# coding=utf-8
""" List of Stopwords 
"""
from corefgraph.resources.lambdas import list_checker, fail

__author__ = 'Valeria Quochi <valeria.quochi@ilc.cnr.it>'

# very basic Stopword list.

stop_words = list_checker(("﻿a", "ad", "ai", "al", "alla", "allo", "con", "cosi'", "così", "da", "del", "della", "dello", "dentro", "di", "e", "ecco", "ed", "fra", "fuori", "ha", "hai", "hanno", "ho", "il", "in", "nei", "nella", "o", "per", "qua'", "quello", "questo", "qui", "quindi", "quà", "sopra", "sotto", "su", "sul", "sulla", "tra", "un", "una", "uno"))

extended_stop_words = list_checker(("ad", "ad"))

non_words = list_checker(("mm", "hmm", "ahm", "uhm", "ehm", "ah", "eh", "oh", "uh", "ih"))


unreliable = fail()
invalid_stop_words = list_checker(("c'è", "c'e'", "spa", "s.p.a.", "s.r.l.", "ecc", "etc"))  # TODO. Re-Check. not sure of what should go here
invalid_start_words = list_checker(("'s",  "etc", ))
invalid_end_words = list_checker(("etc",))

location_modifiers = list_checker(("est", "ovest", "nord", "sud", "est", "ovest", "nord", "sud", "superiore", "inferiore"))

common_NE_subfixes = fail() # TODO
speaking_begin = list_checker(("``",))
speaking_end = list_checker(("''",))
speaking_ambiguous = list_checker(('"', '-'))