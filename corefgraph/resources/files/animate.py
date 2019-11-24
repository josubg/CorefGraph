# coding=utf-8
""" This modules load language specific gazetteers files into lists. As fallback create empty list for missing files or
in case of unexpected errors.
"""

import os
from logging import getLogger
from corefgraph.properties import lang, module_path
from corefgraph.resources.files import utils

__author__ = 'josubg'


logger = getLogger(__name__)
_name = os.path.join(module_path, "resources/languages/{0}/animate/animate_unigrams.txt".format(lang))
try:
    animate_words = utils.load_file(_name)
except IOError as ex:
    logger.warning("Error loading animate word file: %s", _name)
    animate_words = ()

_name = os.path.join(module_path, "resources/languages/{0}/animate/inanimate_unigrams.txt".format(lang))
try:
    inanimate_words = utils.load_file(_name)
except IOError as ex:
    logger.warning("Error loading inanimate word file: %s", _name)
    inanimate_words = ()

