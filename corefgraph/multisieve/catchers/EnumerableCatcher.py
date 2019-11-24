# coding=utf-8
""" Catcher for retrieve enumeration mentions for the system."""

from corefgraph.constants import POS, TAG, FORM, NER, SPAN
from corefgraph.resources.tagset import constituent_tags, pos_tags, ner_tags
from .baseCatcher import BaseCatcher

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class EnumerableCatcher(BaseCatcher):
    """ Class that catch mentions that are part of a enumeration."""

    short_name = "EnumerableCatcher"

    def _catch_mention(self, mention_candidate):
        """ check if the mention is part of an enumeration.

        :param mention_candidate : The mention candidate to test.
        :return: True or False.
        """

        # mention is usable NP|NNP|NML
        mention_pos = mention_candidate.get(POS)
        mention_tag = mention_candidate.get(TAG)
        if not (pos_tags.enumerable_mention_words(mention_pos) or constituent_tags.enumerable(mention_tag)):
            return False
        # parent is NP
        mention_candidate_parent = self.graph_builder.get_syntactic_parent(
            mention_candidate)
        if not constituent_tags.noun_phrase(
                mention_candidate_parent.get(TAG)):
            return False
        if ner_tags.mention_ner(mention_candidate_parent.get(NER)):
            return False
        # Search if the next brother is usable
        siblings = self.graph_builder.get_syntactic_sibling(
            mention_candidate)
        position = siblings.index(mention_candidate)
        # Search for a coma or a conjunction between mention and the end
        for index, brother in enumerate(siblings[position+1:]):
            brother_pos = brother.get(POS)
            if pos_tags.conjunction(brother_pos) or brother[FORM] == ",":
                # Check if next to conjunction (or comma) exist a
                # enumerable sibling
                for post_comma_brother in siblings[index + 1:]:
                    brother_pos = post_comma_brother.get(POS)
                    brother_tag = post_comma_brother.get(TAG)
                    if pos_tags.enumerable_mention_words(brother_pos) or\
                            constituent_tags.noun_phrase(brother_tag):
                        self.logger.debug(
                            "Mention is inside enumeration(Forward): %s",
                            mention_candidate[FORM])
                        return True
        # Check comma or conjunction before mention and previous sibling is usable
        for index, brother in enumerate(siblings[:position]):
            brother_pos = brother.get(POS)
            if pos_tags.conjunction(brother_pos) or brother[FORM] == ",":
                for post_comma_brother in siblings[:index]:
                    post_comma_brother_pos = post_comma_brother.get(POS)
                    post_comma_brother_tag = post_comma_brother.get(TAG)
                    if pos_tags.enumerable_mention_words(post_comma_brother_pos) or \
                            constituent_tags.noun_phrase(post_comma_brother_tag):
                        self.logger.debug(
                            "Mention is inside enumeration(Backward): %s",
                            mention_candidate[FORM])
                        return True
        return False


class PermissibleEnumerableCatcher(EnumerableCatcher):
    """ Class that catch mentions that are part of a enumeration."""

    short_name = "PermissiveEnumerableCatcher"
    soft_ne = True


class AppositiveCatcher(BaseCatcher):
    """ Class that catch mentions that are part of a enumeration."""

    short_name = "AppositiveCatcher"
    soft_ne = True

    def _catch_mention(self, mention_candidate):
        """ check if the mention is part of an apposition.

        :param mention_candidate : The mention candidate to test.
        :return: True or False.
        """

        # mention is usable NP|NNP|NML
        mention_pos = mention_candidate.get(POS)
        mention_tag = mention_candidate.get(TAG)
        if not (pos_tags.enumerable_mention_words(mention_pos) or constituent_tags.enumerable(mention_tag)):
            return False
        # parent is NP
        mention_candidate_parent = self.graph_builder.get_syntactic_parent(
            mention_candidate)
        if not constituent_tags.noun_phrase(
                mention_candidate_parent.get(TAG)):
            return False
        if ner_tags.mention_ner(mention_candidate_parent.get(NER)):
            return False
        # Search if the next brother is usable
        siblings = self.graph_builder.get_syntactic_sibling(
            mention_candidate)
        position = siblings.index(mention_candidate)
        # Search for a coma or a conjunction between mention and the end
        if position+1 < len(siblings):
            brother = siblings[position+1]
            if constituent_tags.noun_phrase(brother.get(TAG)):
                # Check if next to conjunction (or comma) exist a
                # enumerable sibling
                if self.graph_builder.get_words(brother)[0][FORM] == ",":
                    self.logger.info(
                        "Mention is apposition(First Element): %s",
                        mention_candidate[FORM])
                    return True
        # Check comma or conjunction before mention and previous sibling is usable
        if position > 0:
            brother = siblings[position-1]
            if constituent_tags.noun_phrase(brother.get(TAG)):
                # Check if next to conjunction (or comma) exist a
                # enumerable sibling
                if self.graph_builder.get_words(mention_candidate)[-1][FORM] == ",":
                    self.logger.info(
                        "Mention is apposition(First Element): %s",
                        mention_candidate[FORM])
                    return True
        return False
