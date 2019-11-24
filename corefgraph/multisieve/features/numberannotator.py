# coding=utf-8
""" Annotation of the mention number.
"""

from logging import getLogger

from corefgraph.multisieve.features.constants import UNKNOWN, SINGULAR, PLURAL, NUMBER, MENTION, ENUMERATION_MENTION

from corefgraph.constants import NER, FORM, POS
from corefgraph.multisieve.features.baseannotator import FeatureAnnotator
from corefgraph.resources.dictionaries import pronouns
from corefgraph.resources.files.number import singular_words, plural_words
from corefgraph.resources.tagset import ner_tags, pos_tags

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '3/19/14'


class NumberAnnotator(FeatureAnnotator):
    """ Annotator of the mention number.
    """
    name = "number"
    features = [NUMBER]

    use_bergsma_number_lists = True

    def extract_and_mark(self, mention):
        """ Annotate the mention with the number feature (SINGULAR, PLURAL
        or UNKNOWN)

        :param mention: The mention to annotate.
        :return NOTHING
        """

        number = self._get_number(mention=mention)
        self.logger.debug("Number: Result -%s- #%s", number, mention[FORM])
        mention[NUMBER] = number

    def _get_number(self, mention):
        """Determines the number of the mention and return a constant.
        :param mention: The mention to determine number.
        :return PLURAL, SINGULAR or UNKNOWN constants.
        """

        head_word = self.graph_builder.get_head_word(mention)
        word_pos = head_word.get(POS)
        ner = mention.get(NER)

        # Normalize parameters
        word_form = head_word[FORM].lower()
        word_form_lower = word_form.lower()
        # Pronouns
        if pos_tags.pronoun(word_pos) or pronouns.all_pronouns(word_form_lower):
            self.logger.debug("Number: Pronoun")
            if pronouns.plural(word_form_lower):
                return PLURAL
            elif pronouns.singular(word_form_lower):
                return SINGULAR
            else:
                return UNKNOWN

        # Enumeration
        try:
            if mention[MENTION] == ENUMERATION_MENTION:
                self.logger.debug("Number: Enumeration")
                return PLURAL
        except KeyError:
            self.logger.warning("Number without TYPE")

        # Use the mention POS to determine the feature
        if pos_tags.singular(word_pos):
            self.logger.debug("Number: POS")
            return SINGULAR
        if pos_tags.plural(word_pos):
            self.logger.debug("Number: POS")
            return PLURAL

        # Bergsma Lists
        if self.use_bergsma_number_lists:
            if word_form in singular_words:
                self.logger.debug("Number: Bergsma list")
                return SINGULAR
            if word_form in plural_words:
                self.logger.debug("Number: Bergsma list")
                return PLURAL

        # Ner are singular by default except organizations
        if ner_tags.singular(ner):
            self.logger.debug("Number: NER")
            return SINGULAR
        return UNKNOWN
