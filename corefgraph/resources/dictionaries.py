# coding=utf-8

from corefgraph.properties import lang, default_lang
from logging import getLogger
from importlib import import_module
from os import walk

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

logger = getLogger(__name__)


_m = import_module("corefgraph.resources.languages.{0}.dictionaries".format(lang), __name__)


for (dirpath, dirnames, filenames) in walk(_m.__path__[0]):
    for file in filenames:
        if file[0] == "_" or file[-3:] != ".py":
            continue
        name = file[:-3]
        globals()[name] = import_module("corefgraph.resources.languages.{0}.dictionaries.{1}".format(lang, name), __name__)
    break
