# coding=utf-8

from importlib import import_module
from corefgraph.properties import pos_tag_set, default_pos_tag_set, constituent_tag_set, default_constituent_tag_set, \
    ner_tag_set, default_ner_tag_set, dep_tag_set, default_dep_tag_set
import logging

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

logger = logging.getLogger(__name__)

try:
    pos_tags = import_module("corefgraph.resources.tagsets.{0}.partofspeech".format(pos_tag_set), __name__)
except IOError:
    logger.exception("Error loading part of speech tagset Using default tagset")
    pos_tags = import_module("corefgraph.resources.tagsets.{0}.partofspeech".format(default_pos_tag_set), __name__)

try:
    constituent_tags = import_module("corefgraph.resources.tagsets.{0}.constituent".format(constituent_tag_set), __name__)
except IOError:
    logger.exception("Error loading constituent tagset. Using default tagset")
    constituent_tags = import_module("corefgraph.resources.tagsets.{0}.constituent".format(default_constituent_tag_set),
                                     __name__)

try:
    ner_tags = import_module("corefgraph.resources.tagsets.{0}.namedentities".format(ner_tag_set), __name__)
except IOError:
    logger.exception("Error loading named entities tagset. Using default tagset")
    ner_tags = import_module("corefgraph.resources.tagsets.{0}.namedentities".format(default_ner_tag_set), __name__)

try:
    dependency_tags = import_module("corefgraph.resources.tagsets.{0}.dependency".format(dep_tag_set), __name__)
except IOError:
    logger.exception("Error loading dependency tagset. Using default tagset")
    dependency_tags = import_module("corefgraph.resources.tagsets.{0}.dependency".format(default_dep_tag_set), __name__)
