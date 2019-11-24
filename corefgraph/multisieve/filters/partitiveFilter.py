# coding=utf-8
""" Filter for remove mentions that are part of a partitive construction."""

from corefgraph.multisieve.filters.basefilter import BaseFilter
from corefgraph.constants import FORM, SPAN, ID
from corefgraph.resources.dictionaries import determiners

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class PartitiveFilter(BaseFilter):
    """ Class to remove mentions thar are part of a partitive construction."""

    short_name = "PartitiveFilter"

    def filter(self, mention, prev_mentions):
        """ Check if the mention is part of a partitive expression.

        :param graph:
        :param mention: The mention to test.
        :return: True or False.
        """

        span = mention[SPAN]
        sentence = self.graph_builder.get_root(element=mention)
        sentence_words = self.graph_builder.get_sentence_words(sentence=sentence)
        sentence_span = sentence[SPAN]
        relative_span_start = span[0] - sentence_span[0]
        if (relative_span_start > 2) and determiners.partitive_particle(
                sentence_words[relative_span_start - 1][FORM].lower()) and \
                determiners.partitives(
                    sentence_words[relative_span_start - 2][FORM].lower()):
            self.logger.debug(
                "Mention is inside partitive expression:  %s(%s)",
                mention[FORM], mention[ID])
            return True
        return False
