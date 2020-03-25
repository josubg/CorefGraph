# coding=utf-8
""" Filter for remove mentions that are pleonastic pronouns."""


from corefgraph.multisieve.filters.basefilter import BaseFilter
from corefgraph.constants import FORM, ID, POS
from corefgraph.resources.tagset import pos_tags
from corefgraph.resources.dictionaries import pronouns

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class RelativesFilter(BaseFilter):
    """ Class to remove mentions thar are pleonastic pronouns."""

    short_name = "RelativesFilter"

    def filter(self, mention, prev_mentions):
        """ check if the mention is pleonastic.

        :param mention: The mention to test.
        :return: True or False.
        """
        if pos_tags.relative_pronoun(mention.get(POS, "")):
            words = self.graph_builder.get_words(self.graph_builder.get_root(mention))
            mention_words = self.graph_builder.get_words(mention)
            first_word_index = words.index(mention_words[0])
            last_word_index = words.index(mention_words[-1])
            if first_word_index > 0:
                if pos_tags.determinant(words[first_word_index-1][POS]):
                    return True
            next_word = words[last_word_index+1]
            if pos_tags.pronoun(next_word[POS]) or pronouns.all(next_word[FORM]):
                if mention[FORM].lower() == "que":
                    self.logger.debug(
                        "Mention is relative  %s(%s)",
                        mention[ID], self.graph_builder.get_root(mention)[FORM])
                    return True
        return False
