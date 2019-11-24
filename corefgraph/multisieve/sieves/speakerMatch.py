# coding=utf-8
""" The sieves that uses the speaker and utterance checks.

"""

from corefgraph.constants import ID, FORM, QUOTED, UTTERANCE
from corefgraph.multisieve.features.constants import PERSON, FIRST_PERSON, SECOND_PERSON,\
    NUMBER, PLURAL, SINGULAR, SPEAKER, IS_SPEAKER
from corefgraph.multisieve.sieves.base import PronounSieve
from corefgraph.resources.dictionaries import pronouns
from corefgraph.resources.rules import rules
from corefgraph.resources.tagset import dependency_tags

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class SpeakerSieve(PronounSieve):
    """ Check the coreference of two mentions with rules based in speaker
    relations."""

    short_name = "SPM"

    # Filter options
    NO_PRONOUN_MENTION = False

    # Default behavior.
    configs = {"SPEAKER_WE_WE", "SPEAKER_I_I", "SPEAKER_YOU_YOU", "SPEAKER_I",
               "SPEAKER_I_YOU", "SPEAKER_REFLEX"}
    WE_MATCH = False
    I_MATCH = True
    YOU_MATCH = True
    SPEAKER_I_MATCH = True
    YOU_I_MATCH = True
    SPEAKER_REFLEX = True
    EQUAL_SPEAKERS = True

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """ Mention and candidate are the same person in a Discourse.

        :param mention: The selected mention to represent the entity.
        :param entity: The entitpy that mention is part.
        :param candidate: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.
        :return: True or false
        """
        if not super(self.__class__, self).are_coreferent(
                entity, mention, candidate_entity, candidate):
            return False

        person_candidate = candidate.get(PERSON)
        person_mention = mention.get(PERSON)

        number_candidate = candidate[NUMBER]
        number_mention = mention[NUMBER]

        doctype = mention[self.graph_builder.doc_type]
        distance = abs(mention[UTTERANCE] - candidate[UTTERANCE])

        if self.EQUAL_SPEAKERS and self.equal_speakers(mention, candidate):
            self.logger.debug("LINK VALID SPEAKER_REFLEX Match")
            return True

        if self.SPEAKER_REFLEX and self.reflexive(mention, candidate, entity, candidate_entity):
            self.logger.debug("LINK VALID SPEAKER_REFLEX Match")
            return True
        # "I" and the speaker
        if self.are_speaker_speech(speaker=mention, speech=candidate):
            if person_candidate == FIRST_PERSON and\
                    number_candidate == SINGULAR:
                self.logger.debug("LINK VALID SPEAKER_I_MATCH")
                if self.SPEAKER_I_MATCH:
                    return True

        if self.are_speaker_speech(speaker=candidate, speech=mention):
            if person_mention == FIRST_PERSON and number_mention == SINGULAR:
                self.logger.debug("LINK VALID SPEAKER_I_MATCH")
                if self.SPEAKER_I_MATCH:
                    return True

        # Two "I" in the same speaker speech
        if (person_mention == FIRST_PERSON) and (number_mention == SINGULAR) \
                and (person_candidate == FIRST_PERSON) and\
                (number_candidate == SINGULAR):
            if self.same_speaker(mention, candidate):
                self.logger.debug("LINK VALID SPEAKER_I_I_MATCH")
                if self.I_MATCH:
                    return True

        # Two "We" in the same speaker speech
        if (person_mention == FIRST_PERSON) and (number_mention == PLURAL) \
                and (person_candidate == FIRST_PERSON) and\
                (number_candidate == PLURAL):
            if self.same_speaker(mention, candidate):
                self.logger.debug("LINK VALID SPEAKER_WE_WE_MATCH")
                if self.WE_MATCH:
                    return True

        # Two "you" in the same speaker Speech
        # TODO CHECK number
        if person_mention == SECOND_PERSON and person_candidate == SECOND_PERSON:
            if self.same_speaker(mention, candidate):
                self.logger.debug("LINK VALID SPEAKER_YOU_YOU_MATCH")
                if self.YOU_MATCH:
                    return True
        # previous I - you or previous you - I in
        # two person conversation (NOT IN PAPER)
        # TODO CHECK NUMBER
        if self.YOU_I_MATCH and \
                doctype == self.graph_builder.doc_conversation and \
                ((
                    person_mention == SECOND_PERSON and
                    person_candidate == FIRST_PERSON and
                    number_candidate == SINGULAR
                ) or (
                    person_mention == FIRST_PERSON and
                    person_candidate == SECOND_PERSON and
                    number_mention == SINGULAR
                )):
            if not self.same_speaker(mention, candidate) and (distance == 1):
                self.logger.debug("LINK VALID SPEAKER_YOU_I_MATCH")
                return True
            else:
                self.logger.debug("LINK INVALID: YOU an I but not in sequence.")
                # TODO check
                # self.invalid(entity, mention,candidate_entity, candidate)

        if doctype != self.graph_builder.doc_article:
            for mention_a in entity:
                for mention_b in candidate_entity:
                    distance = \
                        abs(mention_a[UTTERANCE] - mention_b[UTTERANCE])
                    person_a = mention_a.get(PERSON)
                    person_b = mention_b.get(PERSON)
                    number_a = mention_a[NUMBER]
                    number_b = mention_b[NUMBER]
                    if distance == 1 and person_a == person_b \
                            and number_a == number_b and not self.same_speaker(
                            mention_a, mention_b):
                        if person_a in (FIRST_PERSON, SECOND_PERSON):
                            # We scape route
                            if person_a == FIRST_PERSON and number_a == PLURAL:
                                return False
                            self.invalid(entity_a=entity, mention_a=mention_a,
                                         entity_b=candidate_entity,
                                         mention_b=mention_b)
                            return False

        self.logger.debug("LINK IGNORED")
        return False

    def log_candidate(self, candidate):
        """ Generate a human readable string with the relevant information of
        the candidate mention.

        :param candidate: The candidate to show.
        :return: Nothing
        """
        self.logger.debug(
            "CANDIDATE: -%s-  speaker-%s- utterance:%d quoted: %s",
            candidate[FORM],
            candidate[SPEAKER], candidate.get(UTTERANCE, "-"),
            candidate.get(QUOTED, "-"))

    def log_mention(self, mention):
        """ Generate a human readable string with the relevant information of
        the mention.

        :param mention: The mention to show.
        :return: Nothing
        """
        self.logger.debug(
            "MENTION: -%s-  speaker-%s- utterance:%d quoted: %s",
            mention[FORM], mention[SPEAKER], mention.get("utterance", "-"),
            mention.get(QUOTED, "-"))

    def reflexive(self, mention, candidate, mention_entity, candidate_entity):
        """check if the mention candidate is a reflexive relation.

        :param candidate: The candidate that may corefer the entity.
        :param mention: The selected mention to represent the entity.
        :param mention_entity: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.
        """
        if not pronouns.reflexive(mention["form"].lower()):
            return False
        if not self.graph_builder.same_sentence(mention, candidate):
            return False
        mention_head = self.graph_builder.get_head_word(mention)
        candidate_head = self.graph_builder.get_head_word(candidate)
        mention_deps = self.graph_builder.get_governor_words(mention_head)
        candidate_deps = self.graph_builder.get_governor_words(candidate_head)
        for node, relation in mention_deps:
            if dependency_tags.subject(relation["value"]):
                for node_b, relation_b in candidate_deps:
                    if node[ID] == node_b[ID] and\
                            dependency_tags.object(relation_b["value"]):
                        return True
            if dependency_tags.object(relation["value"]):
                for node_b, relation_b in candidate_deps:
                    if node[ID] == node_b[ID] and \
                            dependency_tags.subject(relation_b["value"]):
                        return True
        if not(mention_deps or candidate_deps):
            if self.agree_attributes(mention_entity, candidate_entity):
                return True

        return False

    @staticmethod
    def is_speech(mention):
        """The mention is in a direct speech text?
        :param mention: A mention"""
        return mention.get(QUOTED, False)

    def context(self, mention_entity, mention, candidate_entity, candidate):
        """ Return a Human readable and sieve specific info string of the
        mention, the candidate and the link for logging proposes.

        :param mention_entity: The entity of the linked mention.
        :param mention: The mention.
        :param candidate_entity: The candidate entity
        :param candidate: The candidate of the link
        :return: A ready to read string.
        """
        return "{0} -{1}- | {2} -{3}-".format(
            mention[FORM], mention[SPEAKER],
            candidate[FORM], candidate[SPEAKER])

    def equal_speakers(self, mention, candidate):
        if mention.get(IS_SPEAKER, False) and candidate.get(IS_SPEAKER, False):
            return rules.get_head_word_form(self.graph_builder, mention).lower() == \
                   rules.get_head_word_form(self.graph_builder, candidate).lower()
        return False
