# coding=utf-8
""" Catcher for retrieve pronouns mentions for the system."""

from corefgraph.multisieve.catchers.baseCatcher import BaseCatcher
from corefgraph.resources.tagset import pos_tags
from corefgraph.resources.dictionaries import pronouns
from corefgraph.constants import POS, FORM, SPAN

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class PronounCatcher(BaseCatcher):
    """ Class that catch mentions that are pronouns."""

    short_name = "PronounCatcher"

    def _catch_mention(self, mention_candidate):
        """ check if the mention is a pronoun by its POS.

        :param mention_candidate: The mention candidate to test.
        :return: True or False.
        """

        mention_pos = mention_candidate.get(POS)
        if pos_tags.mention_pronoun(mention_pos):
            self.logger.debug("Mention is pronoun: %s  POS %s",
                              mention_candidate[FORM], mention_pos)
            return True
        return False


class PronounPermissiveCatcher(PronounCatcher):
    """ Class that catch mentions that are pronouns."""

    short_name = "PermissivePronounCatcher"
    soft_ne = True

    def _catch_mention(self, mention_candidate):
        """ check if the mention is a pronoun by form.

        :param mention_candidate : The mention candidate to test.
        :return: True or False.
        """

        mention_pos = mention_candidate.get(POS)
        if pos_tags.mention_pronoun(mention_pos) or pronouns.all_pronouns(mention_candidate[FORM]):
            self.logger.debug("Mention is pronoun: %s  POS %s",
                              mention_candidate[FORM], mention_pos)
            return True
        return False
