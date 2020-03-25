# coding=utf-8
""" All the sieves that are related with the same head coreference phenomena.

"""
from corefgraph.multisieve.features import constants
from corefgraph.constants import POS, NER, FORM, MULTIWORD
from corefgraph.multisieve.sieves.base import Sieve
from corefgraph.resources.dictionaries import stopwords, pronouns
from corefgraph.resources.rules import rules
from corefgraph.resources.tagset import pos_tags, ner_tags

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class StrictHeadMatching(Sieve):
    """ A relative pronoun is referent to the NP that modified."""
    short_name = "SHM"
    # Filter options
    NO_PRONOUN_MENTION = True
    NO_STOP_WORDS = True
    ONLY_FIRST_MENTION = True

    # sieve variants
    I_WITHIN_I = False
    WORD_INCLUSION = False
    COMPATIBLE_MODIFIERS = False
    SAME_PROPER_HEAD_LAST = False
    DIFFERENT_LOCATION = False
    LATER_NUMBER = False
    ATTRIBUTES_AGREE = False
    SAME_START = False
    auto_load = False

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """ Check if the candidate and the entity are related by checking heads.

        :param entity: The entity cluster.
        :param mention: The current mention of the entity.
        :param candidate: The mention candidate to the cluster.
        :param candidate_entity: The entity where the candidate appears.

        :return: True or false
        """

        if not super(StrictHeadMatching, self).are_coreferent(
                entity, mention, candidate_entity, candidate):
            return False

        mention = self.entity_representative_mention(entity)

        if self.is_pronoun(mention) or self.is_pronoun(candidate):
            return False

        if not self.head_match(
                mention=mention, entity=entity,
                candidate=candidate, candidate_entity=candidate_entity):
            self.meta["link_filtered_no_head_match"] += 1
            self.logger.debug(
                "LINK FILTERED No head match: %s", candidate[FORM])
            return False

        if self.SAME_START:
            if not mention[FORM].lower().startswith(candidate[FORM].lower()):
                return False
        if self.SAME_PROPER_HEAD_LAST:
            if not self.same_proper_head_last_word(
                    entity=entity, candidate_entity=candidate_entity):
                self.meta["link_filtered_no_same_proper_head"] += 1
                self.logger.debug(
                    "LINK FILTERED No same proper head last: %s", candidate[FORM])
                return False

        if self.WORD_INCLUSION and \
                not self.word_inclusion(
                    entity=entity, mention=mention,
                    candidate_entity=candidate_entity):
            self.meta["link_filtered_no_word_inclusion"] += 1
            self.logger.debug(
                "LINK FILTERED No word inclusion: %s", candidate[FORM])
            return False

        if self.COMPATIBLE_MODIFIERS and \
                not self.compatible_modifiers_only(
                    entity=entity, candidate_entity=candidate_entity):
            self.meta["link_filtered_incompatible_modifiers"] += 1
            self.logger.debug(
                "LINK FILTERED Incompatible modifiers: %s", candidate[FORM])
            return False

        if self.DIFFERENT_LOCATION and \
                self.different_location_modifier(
                    mention_a=mention, mention_b=candidate):
            self.meta["link_filtered_different_location"] += 1
            self.logger.debug(
                "LINK FILTERED Different location modifier : %s",
                candidate[FORM])
            return False

        if self.LATER_NUMBER and \
                self.number_in_later_mention(
                    first_mention=candidate, second_mention=mention):
            self.meta["link_filtered_late_number"] += 1
            self.logger.debug(
                "LINK FILTERED later number modifier : %s", candidate[FORM])
            return False

        if self.ATTRIBUTES_AGREE and \
                not self.agree_attributes(
                    entity=entity, candidate_entity=candidate_entity):
            self.meta["link_filtered_incompatible_attributes"] += 1
            self.logger.debug(
                "LINK FILTERED Incompatible attributes: %s", candidate[FORM])
            return False

        self.logger.debug("LINK MATCH: %s",  candidate[FORM])
        return True

    def get_words(self, element):
        return self.graph_builder.get_words(element)

    def get_all_words_forms(self, element):
        """ Get the forms of every word of a syntactic element.

        :param element: A syntactic element
        :return: List of strings, the forms of the words that appears in the
        element.
        """
        all_words = set(
            rules.clean_string(word[FORM])
            for word in self.get_words(element))
        if "" in all_words:
            all_words.remove("")
        return all_words

    def get_modifiers(self, element):
        """ Get the forms of the modifiers of a syntactic element.

        :param element: A syntactic element
        :return: List of strings, the forms of the words that appears in the
        element and are mods.
        """
        element_head = rules.clean_string(rules.get_head_word_form(self.graph_builder, element))
        all_mods = set([rules.clean_string(word[FORM])
                        for word in self.get_words(element)
                        if pos_tags.mod_forms(word[POS])])
        all_mods.difference_update({element_head})
        return all_mods

    def compare_heads(self, head_a, head_b):
        return rules.clean_string(rules.get_head_word_form(
            self.graph_builder, head_a)) == rules.clean_string(rules.get_head_word_form(self.graph_builder, head_b))

    def head_match(self, mention, entity, candidate, candidate_entity):
        """Checks if the head word form of the mention is equals to the head
        word of any of the candidate entity mentions.

        :param mention: The mention of reference.
        :param entity: The entity of the current mention.
        :param candidate: The candidate to evaluate.
        :param candidate_entity: The entity where the candidate appears.

        :return True of False
        """
        for candidate_entity_mention in candidate_entity:
            if self.compare_heads(candidate_entity_mention, mention):
                return True
        return False

    def word_inclusion(self, entity, mention, candidate_entity):
        """ Check if every word in the candidate entity(s) is included in the
        mention entity words except stop words.

        :param entity: The entity cluster.
        :param mention: The current mention of the entity.
        :param candidate_entity: all the entities where the candidate appears.
        :return: True or false
        """
        # Change mention / candidates form
        candidate_words = set([
                                  word
                                  for candidate_mention in candidate_entity
                                  if candidate_mention[constants.MENTION] != constants.PRONOUN_MENTION
                                  for word in self.get_all_words_forms(candidate_mention)])
        entity_words = set([
                               word
                               for n_mention in entity
                               if n_mention[constants.MENTION] != constants.PRONOUN_MENTION
                               for word in self.get_all_words_forms(n_mention)
                               if not stopwords.stop_words(word)
                               if not stopwords.extended_stop_words(word)
                               if not pronouns.all(word)]
                           )
        head_word_form = rules.get_head_word_form(self.graph_builder, mention).lower()
        if head_word_form in entity_words:
            entity_words.remove(head_word_form)

        if len(entity_words - candidate_words) > 0:
            return False
        return True

    def compatible_modifiers_only(self, entity, candidate_entity):
        """Check if all the modifiers of the mention appears in the candidate.
        Check all pairs.
        Also check if the antecedent contains

        :param entity: The entity cluster.
        :param candidate_entity: the entity where the candidate appears.
        :return: True or false
        """
        for candidate_mention in candidate_entity:
            candidate_words = self.get_all_words_forms(candidate_mention)
            for entity_mention in entity:
                if not self.compare_heads(candidate_mention, entity_mention):
                    continue
                mention_modifiers = self.get_modifiers(entity_mention)
                for candidate_word in candidate_words:
                    if stopwords.location_modifiers(candidate_word) and \
                            candidate_word not in mention_modifiers:
                        return False
                if len(mention_modifiers - candidate_words) > 0:
                    return False
        return True

    def get_head_word(self, mention):
        return self.graph_builder.get_head_word(mention)

    def same_proper_head_last_word(self, entity, candidate_entity):
        """Check if all the modifiers of the candidate appears in the first
        mention of the entity.

        :param entity: The entity cluster.
        :param candidate_entity: The entity where the candidate appears.
        :return: True or false
        """

        for candidate_mention in candidate_entity:
            # Heads must match and be NNP
            candidate_head = self.get_head_word(candidate_mention)
            if not pos_tags.proper_noun(candidate_head[POS]):
                continue
            # The head word must be the last word of the relaxed form
            candidate_head_string = rules.get_head_word_form(
                self.graph_builder, candidate_mention).lower()
            candidate_relaxed_form = self.relaxed_form(candidate_mention)
            if not candidate_relaxed_form.endswith(candidate_head_string):
                continue
            # Get al the proper Nouns until the head word
            candidate_words = self.relaxed_form_word(candidate_mention)
            candidate_proper_noun = set([
                word[FORM].lower()
                for word
                in candidate_words
                if pos_tags.proper_noun(word[POS])])
            for entity_mention in entity:
                # Heads must match and be NNP
                mention_head = self.get_head_word(entity_mention)
                if not pos_tags.proper_noun(mention_head[POS]):
                    continue
                mention_head_string = rules.get_head_word_form(
                    self.graph_builder, entity_mention).lower()
                if not (mention_head_string == candidate_head_string):
                    # heads must be the last word of the relaxed form of the mention
                    continue
                # The head word must be the last word of the relaxed form
                mention_relaxed_form = self.relaxed_form(entity_mention)
                if not mention_relaxed_form.endswith(mention_head_string):
                    continue
                mention_words = self.relaxed_form_word(entity_mention)
                mention_proper_noun = set(
                    [word[FORM].lower()
                        for word
                        in mention_words
                        if pos_tags.proper_noun(word[POS])])
                if candidate_proper_noun.difference(mention_proper_noun) and \
                        mention_proper_noun.difference(candidate_proper_noun):
                    continue
                return True
        return False

    def different_location_modifier(self, mention_a, mention_b):

        # TODO Mojo Not nation-division coreference

        mention_a_locations = set()
        for word_form in self.get_all_words_forms(mention_a):
            if stopwords.location_modifiers(word_form):
                # TODO Mojo to change estate abbreviation into full name
                mention_a_locations.add(word_form)

        mention_b_locations = set()
        for word_form in self.get_all_words_forms(mention_b):
            if stopwords.location_modifiers(word_form):
                # TODO Mojo to change estate abbreviation into full name
                mention_b_locations.add(word_form)
        if mention_a_locations == mention_b_locations:
            return False
        return True

    def number_in_later_mention(self, first_mention, second_mention):
        """ Check if a Number appear in the latter mention but not in the first.

        :param first_mention: The mention that appear first in the text.
        :param second_mention:  The mention that appear later in the text.
        :return: True or False.
        """
        antecedent_words = [
            word.lower()
            for word in self.get_all_words_forms(first_mention)]
        for word in self.get_words(second_mention):
            word_form = word[FORM].lower()
            if pos_tags.cardinal(word[POS]) and \
                    word_form not in antecedent_words:
                return True
        return False

    def context(self, mention_entity, mention, candidate_entity, candidate):
        """ Return a Human readable and sieve specific info string of the
        mention, the candidate and the link for logging proposes.

        :param mention_entity: The entity of the linked mention.
        :param mention: The mention.
        :param candidate_entity: The candidate entity
        :param candidate: The candidate of the link
        :return: A ready to read string.
        """
        candidate_words = set([
                                  word
                                  for candidate_mention in candidate_entity
                                  if candidate_mention[constants.MENTION] != constants.PRONOUN_MENTION
                                  for word in self.get_all_words_forms(candidate_mention)])
        entity_words = set([
                               word
                               for n_mention in mention_entity
                               if n_mention[constants.MENTION] != constants.PRONOUN_MENTION
                               for word in self.get_all_words_forms(n_mention)
                               if not stopwords.extended_stop_words(word)])
        rules.get_head_word_form(self.graph_builder, mention).lower()
        head_word_form = rules.get_head_word_form(self.graph_builder, mention).lower()
        if head_word_form in entity_words:
            entity_words.remove(head_word_form)
        return (
            "%s -%s- %s %s| %s -%s- %s ",
            mention[FORM], self.graph_builder.get_root(mention)[FORM],
            entity_words, mention_entity, candidate[FORM],
            self.graph_builder.get_root(candidate)[FORM], candidate_words)


class StrictHeadMatchingVariantA(StrictHeadMatching):
    """ A variation of SHM that checks compatible modifiers and word
    inclusion. """

    short_name = "SHMA"

    WORD_INCLUSION = True
    COMPATIBLE_MODIFIERS = True
    # Inclusion head match is by default


class StrictHeadMatchingVariantB(StrictHeadMatching):
    """ A variation of SHM that checks compatible modifiers."""

    short_name = "SHMB"

    WORD_INCLUSION = True
    # Inclusion head match is by default


class StrictHeadMatchingVariantC(StrictHeadMatching):
    """ A variation of SHM that checks words inclusions. """

    short_name = "SHMC"

    COMPATIBLE_MODIFIERS = True
    INCOMPATIBLE_DISCOURSE = True
    NO_SUBJECT_OBJECT = True
    # Inclusion head match is by default


class StrictHeadMatchingVariantD(StrictHeadMatching):
    """ A variation of SHM that checks same proper head last. """

    short_name = "SHMD"

    INCOMPATIBLE_DISCOURSE = True
    NO_SUBJECT_OBJECT = True
    SAME_PROPER_HEAD_LAST = True
    DIFFERENT_LOCATION = True
    LATER_NUMBER = True
    ATTRIBUTES_AGREE = True
    # Inclusion head match is by default


class StrictHeadMatchingVariantE(StrictHeadMatching):
    """ A variation of SHM that checks same proper head last. """

    short_name = "SHME"

    DIFFERENT_LOCATION = True
    ATTRIBUTES_AGREE = True
    SAME_START = True
    NO_ENUMERATION_MENTION = True
    NO_ENUMERATION_CANDIDATE = True

    # Inclusion head match is by default


class RelaxHeadMatchingVariantA(StrictHeadMatching):
    """ A variation of SHM that checks compatible modifiers and word
    inclusion. """

    short_name = "RHM"

    WORD_INCLUSION = True
    ATTRIBUTES_AGREE = True

    def head_match(self, mention, entity, candidate, candidate_entity):
        """Checks if the mention an candidate head are related in more relaxed algorithm.

        :param mention: The mention of reference.
        :param entity: The entity of the current mention.
        :param candidate: The candidate to evaluate.
        :param candidate_entity: The entity where the candidate appears.

        :return True of False
        """

        mention_head = self.get_head_word(mention)
        mention_head_form = rules.get_head_word_form(self.graph_builder, mention).lower()
        candidate_head = self.get_head_word(candidate)
        candidate_head_form = \
            rules.get_head_word_form(self.graph_builder, candidate).lower()
        if ner_tags.mention_ner(mention.get(NER)):
            if mention.get(NER) == candidate.get(NER):
                if pos_tags.proper_noun(mention_head[POS]):
                    for word_form in self.get_all_words_forms(candidate):
                        if mention_head_form == word_form:
                            return True
                        if len(mention_head_form) > 2 and \
                                word_form.startswith(mention_head_form):
                            return True
                if pos_tags.proper_noun(candidate_head[POS]):
                    for word_form in self.get_all_words_forms(mention):
                        if candidate_head_form == word_form:
                            return True
                        if len(candidate_head_form) > 2 and \
                                word_form.startswith(candidate_head_form):
                            return True

        if rules.get_head_word_form(self.graph_builder, mention).lower() == \
                rules.get_head_word_form(self.graph_builder, candidate):
            return True
        return False


class StrictHeadMatchingSemeval(StrictHeadMatching):
    """ A variation of SHM that checks compatible modifiers and word
    inclusion. """

    short_name = "SEMEVAL_SHM"
    auto_load = False

    def get_words(self, element):
        return [token
                for word in self.graph_builder.get_words(element)
                for token in word.get(MULTIWORD, [word])]


class SemevalStrictHeadMatchingVariantA(StrictHeadMatchingSemeval):
    """ A variation of SHM that checks compatible modifiers and word
    inclusion. """

    short_name = "SSHMA"

    WORD_INCLUSION = True
    COMPATIBLE_MODIFIERS = True
    # Inclusion head match is by default


class SemevalStrictHeadMatchingVariantB(StrictHeadMatchingSemeval):
    """ A variation of SHM that checks compatible modifiers."""

    short_name = "SSHMB"

    WORD_INCLUSION = True
    # Inclusion head match is by default


class SemevalStrictHeadMatchingVariantC(StrictHeadMatchingSemeval):
    """ A variation of SHM that checks words inclusions. """

    short_name = "SSHMC"

    COMPATIBLE_MODIFIERS = True
    INCOMPATIBLE_DISCOURSE = True
    NO_SUBJECT_OBJECT = True
    # Inclusion head match is by default


class SemevalStrictHeadMatchingVariantD(StrictHeadMatchingSemeval):
    """ A variation of SHM that checks same proper head last. """

    short_name = "SSHMD"

    INCOMPATIBLE_DISCOURSE = True
    NO_SUBJECT_OBJECT = True
    SAME_PROPER_HEAD_LAST = True
    DIFFERENT_LOCATION = True
    LATER_NUMBER = True
    ATTRIBUTES_AGREE = True
    # Inclusion head match is by default


class SemevalStrictHeadMatchingVariantE(StrictHeadMatching):
    """ A variation of SHM that checks same proper head last. """

    short_name = "SSHME"

    DIFFERENT_LOCATION = True
    ATTRIBUTES_AGREE = True
    SAME_START = True
    NO_ENUMERATION_MENTION = True
    NO_ENUMERATION_CANDIDATE = True
    # Inclusion head match is by default
