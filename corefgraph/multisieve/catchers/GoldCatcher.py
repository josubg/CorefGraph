# coding=utf-8
""" Catcher for retrieve valid constituent mentions for the system."""

from corefgraph.multisieve.catchers.baseCatcher import BaseCatcher
from corefgraph.constants import SINGLETON, GOLD_ENTITY

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class GoldCatcher(BaseCatcher):
    """ Class that catch Gold mentions."""

    short_name = "GoldCatcher"

    soft_ne = True

    unique = False

    def __init__(self, graph_builder, extractor):
        BaseCatcher.__init__(self, graph_builder, extractor)
        self.logger.warning("Gold catcher Active")

    def _catch_mention(self, mention_candidate):
        """ check if the mention is in gold mention dict.

        :param mention_candidate : The mention candidate to test.
        :return: True or False.
        """

        return mention_candidate.get(GOLD_ENTITY, False)


class GoldNSCatcher(BaseCatcher):
    """ Class that catch Gold mentions."""

    short_name = "GoldNSCatcher"

    soft_ne = True

    def __init__(self, graph_builder, extractor):
        BaseCatcher.__init__(self, graph_builder, extractor)
        self.logger.warning("Gold catcher Active")

    def _catch_mention(self, mention_candidate):
        """ check if the mention is in gold mention dict.

        :param mention_candidate : The mention candidate to test.
        :return: True or False.
        """

        return mention_candidate.get(GOLD_ENTITY, False) and not mention_candidate.get(SINGLETON, False)
