# coding=utf-8

from corefgraph.properties import lang, default_lang
from logging import getLogger
from importlib import import_module

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

logger = getLogger(__name__)

try:
    rules = import_module("corefgraph.resources.languages.{0}.rules".format(lang), __name__)
except IOError as ex:
    logger.exception("Resource fail (rules) loading default")
    rules = import_module("corefgraph.resources.languages.{0}.rules".format(default_lang), __name__)
except ImportError as ex:
    logger.exception("Resource fail (rules) loading default")
    rules = import_module("corefgraph.resources.languages.{0}.rules".format(default_lang), __name__)
