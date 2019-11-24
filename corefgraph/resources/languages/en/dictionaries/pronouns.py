#coding=utf-8
""" This module contains all the list of pronouns form used in the system.

These lists(in fact tuples or sets) are used to detect pronouns and extract function and features of them. Each element
 of these list are a lowercase form of the pronoun .

Language: English
Language-code: EN

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

Additional or language specific elements:

(Put here any additional list added)

Notes:
 + Mark internal use elements with a initial "_".
 + Use tuples or sets
"""
from corefgraph.resources.lambdas import list_checker, equality_checker, matcher, fail

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '14/3/13'  # DD/MM/YY


plural = list_checker(("we", "us", "ourself", "ourselves", "ours", "our",  "yourselves", "they", "them",
          "themselves", "theirs", "their"))
singular = list_checker(("i", "me", "myself", "mine", "my", "yourself", "he", "him", "himself", "his", "she",
            "herself", "hers", "her", "it", "itself", "its", "one", "oneself", "one's"))

female = list_checker(("her", "hers", "herself", "she"))
male = list_checker(("he", "him", "himself", "his"))
neutral = list_checker(("it", "its", "itself", "where", "here", "there", "which"))


animate = list_checker(("i", "me", "myself", "mine", "my",
           "we", "us", "yourself", "ourselves", "ours", "our",
           "you", "yourself", "yours", "your", "yourselves",
           "he", "him", "himself", "his", "she", "her", "herself", "hers", "her", "one", "oneself", "one's",
           "they", "them", "themselves", "themselves", "theirs", "their", "they", "them", "'em", "themselves",
           "who", "whom", "whose"))
inanimate = list_checker(("it", "itself", "its", "where", "when", "which", "here", "there"))


indefinite = list_checker(("another", "anybody", "anyone", "anything", "each", "either", "enough", "everybody",
                           "everyone", "everything", "less", "little", "much", "neither", "no one", "nobody",
                           "nothing", "one", "other", "plenty", "somebody", "someone", "something", "both", "few",
                           "fewer", "many", "others", "several", "all", "any", "more", "most", "none", "some", "such"))

relative = list_checker(("that", "who", "which", "whom", "where", "whose"))
reflexive = list_checker(("myself", "yourself", "yourselves", "himself", "herself", "itself", "ourselves", "themselves", "oneself"))

no_organization = list_checker(("i", "me", "myself", "mine", "my", "yourself", "he", "him", "himself", "his", "she", "her",
                   "herself", "hers", "here"))

first_person = list_checker(("i", "me", "myself", "mine", "my", "we", "us", "ourself", "ourselves", "ours", "our"))
second_person = list_checker( ("you", "yourself", "yours", "your", "yourselves"))
third_person = list_checker(("he", "him", "himself", "his", "she", "her", "herself", "hers", "her", "it", "itself", "its", "one",
                "oneself", "one's", "they", "them", "themself", "themselves", "theirs", "their", "they", "them", "'em",
                "themselves"))
_others = list_checker(("who", "whom", "whose", "where", "when", "which"))

all_pronouns = lambda x: first_person(x) or second_person(x) or third_person(x) or _others(x)

pleonastic = equality_checker("it")
