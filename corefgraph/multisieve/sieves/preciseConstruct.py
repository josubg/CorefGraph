# coding=utf-8
""" The sieves that check construction that denotes coreference.
"""


from corefgraph.constants import SPAN, NER, ID, TAG, FORM
from corefgraph.multisieve.features.constants import APPOSITIVE, PROPER_MENTION, MENTION, \
    PREDICATIVE_NOMINATIVE, GENDER, NEUTRAL, \
    ANIMACY, INANIMATE, RELATIVE_PRONOUN, DEMONYM, LOCATION
from corefgraph.multisieve.sieves.base import Sieve
from corefgraph.resources.dictionaries import verbs
from corefgraph.resources.rules import rules
from corefgraph.resources.tagset import constituent_tags, ner_tags

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class AppositiveConstruction(Sieve):
    """Two nominal mentions  in an appositive construction are coreferent
    """
    short_name = "ACC"
    # Filter options
    NO_PRONOUN_MENTION = False
    NO_STOP_WORDS = False
    USE_INCOMPATIBLES = False
    IS_INSIDE = False
    auto_load = False

    def validate(self, mention, entity):
        """Entity must be in appositive construction.

        :param mention: The mention to check.
        :param entity: The entity of the mention.
       """
        if not super(self.__class__, self).validate(mention, entity):
            return False
        # if mention[APPOSITIVE]:
        #     return True
        return True

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """Candidate is The NP that cover the appositive construction.

        :param mention: The selected mention to represent the entity.
        :param entity: The entity that mention is part.
        :param candidate: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.

        :return: True or false
        """

        if not Sieve.are_coreferent(
                self, entity, mention, candidate_entity, candidate):
            return False

        # mention = self.entity_representative_mention(entity)
        # If candidate or mention are NE use their constituent as mentions

        if PROPER_MENTION == mention[MENTION] == candidate[MENTION]:
            self.logger.debug("LINK IGNORED are proper nouns")
            self.meta["filtered_two_proper_mentions"] += 1
            return False

        if not self.agree_attributes(
                entity=entity, candidate_entity=candidate_entity):
            self.logger.debug("LINK IGNORED attributes disagree")
            self.meta["filtered_attribute_disagree"] += 1
            return False

        if self.is_location(mention):
            self.meta["filtered_location"] += 1
            self.logger.debug("LINK IGNORED is a location: %s",
                              mention.get(NER, "NO NER"))
            return False
        # Check the apposition
        if mention[APPOSITIVE] and mention[APPOSITIVE][SPAN] == candidate[SPAN]:
                self.meta["linked_" + self.short_name] += 1
                return True
        if candidate[APPOSITIVE] and candidate[APPOSITIVE][SPAN] == mention[SPAN]:
                self.meta["linked_" + self.short_name] += 1
                return True
        # if candidate.get("constituent", candidate) == mention[APPOSITIVE]:
        #     self.meta["linked_" + self.short_name] += 1
        #     mention[APPOSITIVE] = True
        #     return True
        # if mention.get("constituent", mention) == candidate[APPOSITIVE]:
        #     self.meta["linked_" + self.short_name] += 1
        #     candidate[APPOSITIVE] = True
        #     return True
        self.meta["ignored"] += 1
        return False


class PredicativeNominativeConstruction(Sieve):
    """ The mention and the candidate are in a subject-object copulative
    relation."""
    short_name = "PNC"
    # Filter options
    ONLY_FIRST_MENTION = False
    USE_INCOMPATIBLES = False
    auto_load = False

    def validate(self, mention, entity):
        """Entity must be in a predicative-nominative construction.

        :param mention: The mention to check.
        :param entity: The entity of the mention"""
        if not super(self.__class__, self).validate(mention, entity):
            return False
        if not mention[PREDICATIVE_NOMINATIVE]:
            self.logger.debug("MENTION FILTERED Not predicative nominative")
            return False
        return True

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """ Candidate is the subject of the predicative-nominative relation of
        the mention.

        :param mention: The selected mention to represent the entity.
        :param entity: The entity that mention is part.
        :param candidate: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.

        :return: True or false
        """
        if not Sieve.are_coreferent(
                self, entity, mention, candidate_entity, candidate):
            return False
        mention = self.entity_representative_mention(entity)

        if (self.graph_builder.is_inside(mention[SPAN], candidate[SPAN]) or
                self.graph_builder.is_inside(
                    candidate[SPAN], mention[SPAN])):
            return False

        if self.graph_builder.same_sentence(mention, candidate):
            # S < (NP=m1 $.. (VP < ((/VB/ < /^(am|are|is|was|were|'m|'re|'s|be)$/) $.. NP=m2)))
            # S < (NP=m1 $.. (VP < (VP < ((/VB/ < /^(be|been|being)$/) $.. NP=m2))))
            mention_parent = self.graph_builder.get_syntactic_parent(mention)
            mention_grandparent = self.graph_builder.get_syntactic_parent(
                mention_parent)
            if constituent_tags.verb_phrase(mention_parent[TAG]):
                enclosing_verb_phrase = mention_parent
            else:
                self.logger.debug("LINK FILTERED No enclosing verb")
                self.meta["filtered_no_enclosing_verb"] += 1
                return False
            if constituent_tags.verb_phrase(mention_grandparent[TAG]):
                enclosing_verb_phrase = mention_grandparent
            if not verbs.copulative(self.graph_builder.get_syntactic_sibling(
                    mention)[0]["form"]):
                self.logger.debug("LINK FILTERED verb is not copulative")
                self.meta["filtered_enclosing_verb_no_copulative"] += 1
                return False
            siblings = []
            enclosing_verb_phrase_id = enclosing_verb_phrase[ID]
            for sibling in self.graph_builder.get_syntactic_sibling(
                    enclosing_verb_phrase):
                if sibling[ID] == enclosing_verb_phrase_id:
                    break
                siblings.append(sibling)
            siblings = [sibling[ID] for sibling in siblings]
            # or siblings[X] == candidate?
            if candidate[ID] in siblings:
                self.meta["linked_" + self.short_name] += 1
                mention[PREDICATIVE_NOMINATIVE] = candidate
                return True
        self.meta["ignored"] += 1
        return False


class RoleAppositiveConstruction(Sieve):
    """ Find role appositive relations withing the mentions.
    """

    short_name = "RAC"
    # Filter options
    ONLY_FIRST_MENTION = False
    USE_INCOMPATIBLES = False
    auto_load = False
    IS_INSIDE = False

    def validate(self, mention, entity):
        """Entity must be in role appositive construction.

        :param mention: The mention to check.
        :param entity: the entity where the mention is """
        if not super(self.__class__, self).validate(mention, entity):
            return False
            # constrain(a) The mention must be labeled as person
        ner = mention.get(NER, None)
        if not ner_tags.person(ner):
            self.logger.debug("MENTION FILTERED Not a person -%s-", ner)
            return False
        return True

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """ Candidate is the NP that the relative pronoun modified.

        :param mention: The selected mention to represent the entity.
        :param entity: The entity that mention is part.
        :param candidate: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.

        :return: True or false
        """
        if not Sieve.are_coreferent(
                self, entity, mention, candidate_entity, candidate):
            return False

        # mention = self.entity_representative_mention(entity)
        # (b) and (c) constrains The candidate must be animate
        # and can not be neutral.
        if not self.agree_attributes(entity, candidate_entity):
            return False

        if candidate[GENDER] == NEUTRAL:
            self.logger.debug("LINK FILTERED Candidate is neutral")

            return False
        if candidate[ANIMACY] == INANIMATE:
            self.logger.debug("LINK FILTERED Candidate is inanimate")
            self.meta["filtered_inanimate"] += 1
            return False
        if rules.is_role_appositive(self.graph_builder, candidate, mention):
            self.meta["linked_" + self.short_name] += 1
            mention[APPOSITIVE] = candidate
            return True
        self.meta["ignored"] += 1
        return False


class AcronymMatch(Sieve):
    """ A demonym is coreferent to their location."""
    # Filter options
    short_name = "AMC"
    ONLY_FIRST_MENTION = False
    USE_INCOMPATIBLES = False
    auto_load = False

    def are_coreferent(self,  entity, mention, candidate_entity, candidate):
        """ Mention and candidate are one acronym of the other.

        :param mention: The selected mention to represent the entity.
        :param entity: The entity that mention is part.
        :param candidate: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.

        :return: True or false
        """
        # TODO limpiar acronimos
        # TODO No tiene en cuenta los posibles plurales
        if not Sieve.are_coreferent(
                self, entity, mention, candidate_entity, candidate):
            return False

        for candidate in candidate_entity:
            candidate_form = candidate[FORM]
            if self.is_pronoun(candidate):
                self.logger.debug(
                    "LINK FILTERED Candidate is a pronoun: %s", candidate_form)
                self.meta["loop_filtered_pronoun"] += 1
                continue
            for mention in entity:
                mention_form = mention[FORM]
                if self.is_pronoun(mention):
                    self.logger.debug(
                        "Mention is a pronoun: %s next entity mention",
                        mention["form"])
                    continue
                if len(candidate_form) > len(mention_form):
                    sort, large = mention_form, candidate_form
                else:
                    sort, large = candidate_form, mention_form
                if sort in large:
                    self.meta["loop_filtered_short_in_large"] += 1
                    continue
                if not sort.isupper():
                    self.meta["loop_filtered_short_no_uppercase"] += 1
                    continue
                # generated_acronyms = (filter(str.isupper, large),)
                if sort == filter(str.isupper, large):
                    self.logger.debug("ACRONYM MATCH: %s ", sort)
                    self.meta["linked_" + self.short_name] += 1
                    return True
            self.meta["ignored"] += 1
        return False


class RelativePronoun(Sieve):
    """ A relative pronoun is coreferent to the NP that modified."""

    short_name = "RPC"
    # Filter options
    IS_INSIDE = False
    ONLY_FIRST_MENTION = False
    USE_INCOMPATIBLES = False
    NO_PRONOUN_MENTION = False
    auto_load = False

    def validate(self, mention, entity):
        """Entity must be relative pronoun.

        :param mention: The mention to check.
        :param entity: The entity og the mention.
        """
        if not super(self.__class__, self).validate(mention, entity):
            return False

        if not mention[RELATIVE_PRONOUN]:
            self.logger.debug("MENTION FILTERED Not a relative pronoun")
            return False
        return True

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """ Candidate is the NP that the relative pronoun modified.

        :param mention: The selected mention to represent the entity.
        :param entity: The entity that mention is part.
        :param candidate: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.

        :return: True or false
        """

        if not Sieve.are_coreferent(
                self, entity, mention, candidate_entity, candidate):
            return False

        mention = self.entity_representative_mention(entity)
        candidate_tag = candidate.get(TAG)

        # TODO ESTO
        if not constituent_tags.noun_phrase(candidate_tag):
            self.logger.debug("LINK FILTERED Candidate is not a noun phrase")
            self.meta["filtered_no_NP"] += 1
            return False
        if rules.is_relative_pronoun(self.graph_builder, candidate, mention):
            self.meta["linked"] += 1
            return True
        self.meta["ignored"] += 1
        return False


class DemonymMatch(Sieve):
    """ A demonym is coreferent to their location."""
    short_name = "DMC"
    # Filter options
    ONLY_FIRST_MENTION = False
    USE_INCOMPATIBLES = False
    auto_load = False

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """ Mention and candidate are one demonym of the other.

        :param mention: The selected mention to represent the entity.
        :param entity: The entity that mention is part.
        :param candidate: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.

        :return: True or false
        """
        if not Sieve.are_coreferent(
                self, entity, mention, candidate_entity, candidate):
            return False

        mention = self.entity_representative_mention(entity)
        # TODO Change this
        candidate_form = candidate[FORM].lower().replace("the ", "")
        mention_form = mention[FORM].lower().replace("the ", "")
        if mention_form in candidate.get(LOCATION, ()) or \
                candidate_form in mention.get(DEMONYM, ()):
            self.meta["linked_" + self.short_name] += 1
            return True
        self.meta["ignored"] += 1
        return False


class PreciseConstructSieve(Sieve):
    """Two nominal mentions in an appositive construction are coreferent
    """
    short_name = "PCM"

    def __init__(self, meta_info):
        super(self.__class__, self).__init__(meta_info)
        self.sieves = (
            AppositiveConstruction(meta_info),
            PredicativeNominativeConstruction(meta_info),
            AcronymMatch(meta_info),
            RelativePronoun(meta_info),
            DemonymMatch(meta_info),
            RoleAppositiveConstruction(meta_info),
        )
        for sieve in self.sieves:
            self.meta[sieve.short_name] = sieve.meta

    def validate(self, mention, entity):
        """  The validations is made in each sub sieve.


        :param mention: The mention to check.
        :param entity: The entity of the mention.
        """
        return True

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """ Check if the candidate and the entity are coreferent with
        a sub-sieve pack.

        :param mention: The selected mention to represent the entity.
        :param entity: The entity that mention is part.
        :param candidate: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.
        :return: True or false
        """
        for sieve in self.sieves:
            sieve.graph_builder = self.graph_builder
            if sieve.validate(mention=mention, entity=entity):
                if sieve.are_coreferent(
                        entity, mention, candidate_entity, candidate):
                    self.logger.debug("Match with -%s-", Sieve.short_name)
                    self.meta["linked"] += 1
                    return True
            self.meta["ignored"] += 1
        return False
