# coding=utf-8
""" Filter for remove mentions that have same head of previous mentions."""

from .basefilter import BaseFilter
from corefgraph.resources.tagset import pos_tags
from corefgraph.constants import FORM, SPAN, POS, ID

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class SameHeadFilter(BaseFilter):
    """ Class to remove mentions that is inside another one and have the same
    head."""

    short_name = "SameHeadFilter"
    prev_comma = True
    end_comma = True
    next_comma = True

    def filter(self, mention):
        """ check if the mention is inside a mention and have the same head.

        @param mention: The mention to test.
        @return: True or False.
        """
        sentence = self.graph_builder.get_root(mention)
        sentence_words = self.graph_builder.get_sentence_words(sentence)
        sentence_span = sentence[SPAN]
        span = mention[SPAN]
        head_word = self.graph_builder.get_head_word(mention)
        relative_span = (
            span[0] - sentence_span[0], span[1] - sentence_span[0])
        # TODO get rid of this insane reference
        for prev_mention in self.extractor.sentence_mentions_bft_order:
            # Not check with itself
            if prev_mention[ID] == mention[ID]:
                continue
            # Check if those have the same head
            prev_head_word = self.graph_builder.get_head_word(prev_mention)
            if head_word[ID] == prev_head_word[ID] and\
                    self.graph_builder.is_inside(span, prev_mention[SPAN]):
                # If the next word is a comma, it may be an enumeration
                if self.next_comma and (relative_span[1] + 1 < len(sentence_words)):
                    next_word = sentence_words[relative_span[1] + 1]
                    if pos_tags.conjunctions(next_word[POS]) or next_word[FORM] == ",":
                        self.logger.debug(
                            "NO filtered inside an ENUMERATION/APPOSITION:(%s)",
                            prev_mention[FORM])
                        continue
                last_word = sentence_words[relative_span[1]]
                if self.end_comma:
                        if pos_tags.conjunctions(last_word[POS]) or last_word[FORM] == ",":
                            self.logger.debug(
                                "NO filtered inside an ENUMERATION/APPOSITION:(%s)",
                                prev_mention[FORM])
                            continue
                if self.prev_comma and (relative_span[0] - 1 > 0):
                    prev_word = sentence_words[relative_span[0] - 1]
                    if pos_tags.conjunctions(prev_word[POS]) or prev_word[FORM] == ",":
                        self.logger.debug(
                            "NO filtered inside an ENUMERATION:(%s)",
                            prev_mention[FORM])
                        continue
                self.logger.debug(
                    "Filtered: have same head word %s(%s) prev:%s",
                    mention[FORM], mention[ID], prev_mention[ID])
                return True
        return False


class ConllSameHeadFilter(SameHeadFilter):
    """ Class to remove mentions that is inside another one and have the same
    head."""

    short_name = "ConllSameHeadFilter"
    prev_comma = False
    end_comma = False
    next_comma = True
