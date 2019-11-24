# coding=utf-8
""" The sieves that check form similarity features.

"""

from corefgraph.multisieve.sieves.base import Sieve
from corefgraph.constants import ID

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class GoldMatch(Sieve):
    """ Two mentions are coreferent if their surfaces are equals."""
    short_name = "GOLD"
    auto_load = False
    # Filter options
    ONLY_FIRST_MENTION = False
    NO_PRONOUN_MENTION = False
    NO_STOP_WORDS = False
    DISCOURSE_SALIENCE = False
    INCOMPATIBLE_DISCOURSE = False

    def valid_mention(self, entity):
        """ Bypass the filtering of mentions.

        :param entity: The entity.
        :return: Always True
        """
        return entity

    def validate(self, mention, entity):
        return True

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """ Candidate an primary mention have the same form

        :param mention: The selected mention to represent the entity.
        :param entity: The entity that mention is part.
        :param candidate: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.
        """

        mention_entity_id = mention.get("entity_id", None)
        candidate_entity_id = candidate.get("entity_id", None)
        if mention_entity_id == candidate_entity_id and mention_entity_id is not None:
            self.logger.debug("EXACT MATCH:%s %s", mention[ID], candidate[ID])
            return True
        self.logger.debug("IGNORED LINK: %s  %s", mention[ID], candidate[ID])
        return False


class GoldMatchX(GoldMatch):
    """ Two mentions are coreferent if their surfaces are equals."""
    short_name = "GOLDX"
    limit = 10

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """ Candidate an primary mention have the same form

        :param mention: The selected mention to represent the entity.
        :param entity: The entity that mention is part.
        :param candidate: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.
        """

        mention_entity_id, mention_index = mention[ID].split("#")
        candidate_entity_id, candidate_index = candidate[ID].split("#")

        if max(mention_index, candidate_index) < self.limit:
            return False
        if mention_entity_id == candidate_entity_id:
            self.logger.debug("EXACT MATCH:%s %s", mention[ID], candidate[ID])

            return True
        self.logger.debug("IGNORED LINK: %s  %s", mention[ID], candidate[ID])
        return False


class GoldMatchV(GoldMatchX):
    """ Two mentions are coreferent if their surfaces are equals."""
    short_name = "GOLDV"
    limit = 5


class GoldMatchZ(GoldMatchX):
    """ Two mentions are coreferent if their surfaces are equals."""
    short_name = "GOLDZ"
    limit = 0
