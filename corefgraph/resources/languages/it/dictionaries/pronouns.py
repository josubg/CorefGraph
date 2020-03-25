# coding=utf-8
""" This module contains all the list of pronouns form used in the system.

__author__ = 'Valeria Quochi <valeria.quochi@ilc.cnr.it>'
__date__ = '5/13/13'

Language: Italian
Language-code: IT

Expected list form the system are:

 + all: A list that contains all pronouns of the language

 + Features lists:
     + plural: All undoubtedly
     + singular: All undoubtedly
     + male: All undoubtedly
     + female: All undoubtedly
     + neutral: All undoubtedly
     + animate: All undoubtedly
     + inanimate: All undoubtedly
     + first_person: All undoubtedly
     + second_person: All undoubtedly
     + third_person: All undoubtedly
     + indefinite:  All undoubtedly
 + function lists:
  + relative: All relative pronoun forms.
  + reflexive: All reflexive pronoun forms
 + others list
  + pleonastic: The pronouns that can be pleonastic (http://en.wikipedia.org/wiki/Dummy_pronoun).
  + no_organization: The pronouns that can't match with an organization NE.
"""
from corefgraph.resources.lambdas import list_checker

plural = list_checker(("noi", "voi", "loro", "essi", "esse", "ci", "ce", "vi", "ve", "li", "le", "nostro", "nostri","nostra","nostre", "vostro",  "vostri",  "vostra",  "vostre"))
singular = list_checker(("io", "tu", "ti", "egli", "esso", "lui", "suo", "sua", "sue", "suoi", "ella", "essa", "lei", "sé", "lo", "la", "gli"))

female = list_checker(("esse", "essa", "lei", "ella", "la", "le"))
male = list_checker(("egli", "esso", "lui", "lo", "gli"))
neutral = list_checker(("che", "cui", "quanto", "chi", "quando", "come", "quale", "quali"))


animate = list_checker(("io", "me", "mi", "mio", "noi", "voi", "loro", "ci", "vi", "nostro", "nostra", "nostri", "nostre", "vostro", "vostra", "vostri", "vostre", "egli", "lui", "ella", "lei", "chi"))
inanimate = list_checker(("esso", "essa", "quanto", "quando", "che", "come", "quale", "quali"))

first_person = list_checker(("ja",))
second_person = list_checker(("ja",))
third_person = list_checker(("ja",))
indefinite = list_checker(("altro", "altra", "altri", "altre", "nessuno", "nessuna", "ciascuno", "ciascuna", "qualcuno", "qualcuna", "ognuno", "tutto", "tutti", "tutte", "tutta" "uno", "una", "molti", "molte", "molta", "nulla", "alcuni", "alcuno", "alcune", "alcuna", "certo", "certi", "certa", "certe", "diverso", "diversa", "diversi", "diverse", "parecchio", "parecchi", "parecchia", "parecchie", "tale", "tali", "troppo", "troppa", "troppi", "troppe", "poco", "poca", "pochi", "poche", "qualcosa", "niente", "tanto", "tanti", "tanta", "tante", "vario", "vari", "varia", "varie", "meno", "altrettanti", "piu'", "più"))

others = list_checker(("who", "whom", "whose", "where", "when", "which"))

relative = list_checker(("che", "chi", "quale", "quali ", "dove", "cui", "quando"))
reflexive = list_checker(("ja",))

pleonastic = list_checker(("it",))
no_organization = list_checker(("ja",))

all = lambda x: first_person(x) or second_person(x) or third_person(x) or others(x) or plural(x) or singular(x) or male(x) or female(x) or neutral(x) or animate(x) or inanimate(x)