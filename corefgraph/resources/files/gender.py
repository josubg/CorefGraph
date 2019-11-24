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

neutral_words = ()
male_words = ()
female_words = ()
female_names = ()
male_names = ()
bergma_counter = {}

_name = os.path.join(module_path, "resources/languages/{0}/gender/neutral_unigrams.txt".format(lang))
try:
    neutral_words = utils.load_file(_name)
except IOError as ex:
    logger.exception("Error loading neutral word file: %s", _name)


_name = os.path.join(module_path, "resources/languages/{0}/gender/male_unigrams.txt".format(lang))
try:
    male_words = utils.load_file(_name)
except IOError as ex:
    logger.warning("Error loading male word file: %s", _name)


_name = os.path.join(module_path, "resources/languages/{0}/gender/female_unigrams.txt".format(lang))
try:
    female_words = utils.load_file(_name)
except IOError as ex:
    logger.warning("Error loading female word file: %s", _name)


_name = os.path.join(module_path, "resources/languages/{0}/gender/names_combine.txt".format(lang))
try:
    female_names, male_names = utils.split_gendername_file(_name)
except IOError as ex:
    logger.warning("Error loading names file: %s", _name)

try:
    bergma_counter = utils.bergma_split(
        os.path.join(module_path, "resources/languages/{0}/gender/data.txt".format(lang)))
    logger.debug("Bergma dict: %i", len(bergma_counter))
except IOError as ex:
    logger.warning("Error loading Bersgma file")

