# coding=utf-8
""" Filter for remove interjection mentions from the system."""

from corefgraph.multisieve.filters.basefilter import BaseFilter
from corefgraph.resources.tagset import pos_tags, constituent_tags
from corefgraph.constants import POS, FORM, TAG, ID

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class InterjectionFilter(BaseFilter):
    """ Class that filter mentions that are interjection."""

    short_name = "InterjectionFilter"

    def filter(self, mention, prev_mentions):
        """ check if the mention is a interjection.

        :param mention: The mention to text
        :return: True or False
        """

        tag = mention.get(TAG)
        head_word = self.graph_builder.get_head_word(mention)
        head_word_pos = head_word[POS]

        if pos_tags.interjection(head_word_pos) or \
                constituent_tags.interjection(tag):
            self.logger.debug(
                "Mention is interjection:  %s(%s)", mention[FORM], mention[ID])
            return True
        return False
