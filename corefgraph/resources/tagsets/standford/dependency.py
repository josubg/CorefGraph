# coding=utf-8

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


from corefgraph.resources.lambdas import list_checker, equality_checker, matcher, fail

object = list_checker(("iobj", "pobj", "dobj"))
subject = list_checker(("nsubj", "csubj"))
