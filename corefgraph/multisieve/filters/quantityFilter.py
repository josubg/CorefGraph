# coding=utf-8
""" Filter for remove mentions that are quantities."""

from corefgraph.multisieve.filters.basefilter import BaseFilter
from corefgraph.constants import ID, FORM, SPAN, NER

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class QuantityFilter(BaseFilter):
    """ Class to remove mentions thar are quantities."""

    short_name = "QuantityFilter"

    def filter(self, mention, prev_mentions):
        """ check if the mention is a non-word

        :param mention: The mention to test.
        :return: True or False.
        """
        head_word = self.graph_builder.get_head_word(mention)

        if self._inside_money(head_word[SPAN]):
            self.logger.debug(
                "Mention is money or perceptual:  %s(%s)", mention[FORM], mention[ID])
            return True
        return False

    def _inside_money(self, mention_span):
        """ Check if a span is inside any Named entity Mention span  and is not
        the mention.

        :param mention_span: The span of the mention.
        """
        for entity in self.extractor.named_entities:
            if entity[NER] == "MONEY" or entity[NER] == "PERCENT":
                if self.graph_builder.is_inside(mention_span, entity[SPAN]):
                    return True
        return False
