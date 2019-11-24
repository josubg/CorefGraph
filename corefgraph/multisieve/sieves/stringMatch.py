# coding=utf-8
""" The sieves that check form similarity features.

"""

from corefgraph.constants import FORM
from corefgraph.multisieve.sieves.base import Sieve
from corefgraph.resources.rules import rules

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class ExactStringMatch(Sieve):
    """ Two mentions are coreferent if their surfaces are equals."""
    short_name = "ESM"

    # Filter options
    ONLY_FIRST_MENTION = False
    NO_PRONOUN_MENTION = True
    NO_PRONOUN_CANDIDATE = True
    NO_STOP_WORDS = True
    DISCOURSE_SALIENCE = False

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """ Candidate an primary mention have the same form


        :param mention: The selected mention to represent the entity.
        :param entity: The entity that mention is part.
        :param candidate: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.

        :return: True or false
        """
        if not super(ExactStringMatch, self).are_coreferent(
                entity, mention, candidate_entity, candidate):
            return False

        mention_form = self.get_form(mention)
        candidate_form = self.get_form(candidate)

        # Check empty results
        if not candidate_form:
            self.logger.debug("FILTERED LINK Empty candidate processed form")
            self.meta["Filtered_mention_form_empty"] += 1
            return False
        if not mention_form:
            self.logger.debug("FILTERED LINK Empty processed form")
            self.meta["Filtered_candidate_form_empty"] += 1
            return False

        if mention_form == candidate_form:
            self.logger.debug("Linked")
            self.meta["linked"] += 1
            return True

        self.meta["ignored"] += 1
        return False

    def get_form(self, mention):
        return rules.clean_string(mention[FORM])

    def context(self, mention_entity, mention, candidate_entity, candidate):
        """ Return a Human readable and sieve specific info string of the
        mention, the candidate and the link for logging proposes.

        :param mention_entity: The entity of the linked mention.
        :param mention: The mention.
        :param candidate_entity: The candidate entity
        :param candidate: The candidate of the link

        :return: A ready to read string.
        """
        return "{0} -{1}- | {2} -{3}- ".format(
            mention[FORM], self.graph_builder.get_root(mention)[FORM],
            candidate[FORM], self.graph_builder.get_root(candidate)[FORM])


class RelaxedStringMatch(ExactStringMatch):
    """ Two mentions are coreferent if their surfaces are similar."""
    short_name = "RSM"
    # Filter options
    NO_ENUMERATION_MENTION = True
    NO_ENUMERATION_CANDIDATE = True
    NO_PRONOUN_MENTION = True
    NO_PRONOUN_CANDIDATE = True
    NO_STOP_WORDS = True
    NO_APPOSITIVE_CANDIDATE = True
    NO_APPOSITIVE_MENTION = True

    def get_form(self, mention):
        return rules.clean_string(self.relaxed_form(mention))
