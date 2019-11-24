# coding=utf-8
""" Filter to remove invalid word mentions.

"""

from .basefilter import BaseFilter
from corefgraph.resources.dictionaries import stopwords
from corefgraph.constants import FORM, ID

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class InvalidWordsFilter(BaseFilter):
    """ Class that filter mentions that are interjection."""

    short_name = "InvalidWordFilter"

    def filter(self, mention, prev_mentions):
        """ Check if the mention is a non-word.

        :param mention: The mention to test.
        :return: True or False.
        """
        form = mention[FORM]
        if stopwords.invalid_words(form.lower()):
            self.logger.debug("Mention trigger invalid word:  %s(%s)",
                              mention[FORM], mention[ID])
            return True
        return False
