# coding=utf-8
""" Filter for remove the bare NP mentions out of the system."""

from .basefilter import BaseFilter
from corefgraph.resources.rules import rules


__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class BareNPFilter(BaseFilter):
    """ Class that filter mentions that are bare NPs."""

    short_name = "BareNPFilter"

    def filter(self, mention, prev_mentions):
        """ check if the mention is a bare NP.

        :param mention: The mention to test.
        :return: True or False.
        """
        return rules.is_bare_np(self.graph_builder, mention)
