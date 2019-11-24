# coding=utf-8

import re

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

matcher = lambda r: lambda value:  value is not None and re.compile(r).match(value)
list_checker = lambda l: lambda value: value in l
equality_checker = lambda x: lambda value: value is not None and x == value
fail = lambda: lambda value: False
