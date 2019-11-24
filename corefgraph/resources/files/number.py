# coding=utf-8
""" This modules load language specific gazetteers files into lists. As fallback create empty list for missing files or
in case of unexpected errors.
"""
import os
from logging import getLogger
import corefgraph.properties as properties
from corefgraph.resources.files import utils

__author__ = 'josubg'

logger = getLogger(__name__)

# Unigrams files

plural_words = ()
singular_words = ()

_name = os.path.join(
    properties.module_path, "resources/languages/{0}/number/plural_unigrams.txt".format(properties.lang))
try:
    plural_words = utils.load_file(_name)
except IOError as ex:
    logger.warning("Error Loading plural word file: %s", _name)

_name = os.path.join(
    properties.module_path, "resources/languages/{0}/number/singular_unigrams.txt".format(properties.lang))
try:
    singular_words = utils.load_file(_name)
except IOError as ex:
    logger.warning("Error loading singular word file: %s", _name)
