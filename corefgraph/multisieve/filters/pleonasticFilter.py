# coding=utf-8
""" Filter for remove mentions that are pleonastic pronouns."""
from corefgraph.resources.rules import rules
from corefgraph.multisieve.filters.basefilter import BaseFilter
from corefgraph.constants import FORM, ID
from corefgraph.resources.dictionaries import pronouns


__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class PleonasticFilter(BaseFilter):
    """ Class to remove mentions thar are pleonastic pronouns."""

    short_name = "PleonasticFilter"

    def filter(self, mention, prev_mentions):
        """ check if the mention is pleonastic.

        :param mention: The mention to test.
        :return: True or False.
        """
        if not pronouns.pleonastic(mention[FORM].lower()):
            return False
        if rules.is_pleonastic(constituent=mention, graph_builder=self.graph_builder):
            self.logger.debug(
                "Mention is pleonastic it:  %s(%s)",
                mention[ID], self.graph_builder.get_root(mention)[FORM])
            return True
        self.logger.debug(
                "Mention is not pleonastic  %s(%s)",
                mention[ID], self.graph_builder.get_root(mention)[FORM])
        return False
