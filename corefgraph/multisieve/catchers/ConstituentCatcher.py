# coding=utf-8
""" Catcher for retrieve constituent mentions for the system."""

from .baseCatcher import BaseCatcher

from corefgraph.resources.tagset import constituent_tags
from corefgraph.constants import TAG, FORM

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class ConstituentCatcher(BaseCatcher):
    """ Class that catch mentions that are NPs(Noun Phrases) and not inside NEs(Named Entities)."""

    short_name = "ConstituentCatcher"

    def _catch_mention(self, mention_candidate):
        """ Check if the mention is a NP(Noun Phrase).

        :param mention_candidate : The mention candidate to test.
        :return: True or False.
        """

        mention_tag = mention_candidate.get(TAG)
        if constituent_tags.mention_constituents(mention_tag):
            self.logger.debug(
                "Mention is valid constituent: %s", mention_candidate[FORM])
            return True
        return False


class PermissiveConstituentCatcher(ConstituentCatcher):
    """ Class that catch mentions that are NPs and can be inside NE(Named Entities)."""

    short_name = "PermissiveConstituentCatcher"
    soft_ne = True
