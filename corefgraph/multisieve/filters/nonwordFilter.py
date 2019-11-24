# coding=utf-8
""" Filter to remove mentions that are Non-words."""


from .basefilter import BaseFilter
from corefgraph.resources.dictionaries import stopwords
from corefgraph.constants import FORM, ID

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class NonWordFilter(BaseFilter):
    """Class that filter mentions that have non word heads."""

    short_name = "NonWordFilter"

    def filter(self, mention, prev_mentions):
        """ check if the mention head is a non-word.
        The check is case insensitive.

        :param mention: The mention to test
        :return: True or False
        """
        head_word = self.graph_builder.get_head_word(mention)
        head_form = head_word[FORM].lower()
        if stopwords.non_words(head_form):
            self.logger.debug(
                "Mention is non word:  %s(%s)", mention[FORM], mention[ID])
            return True
        return False
