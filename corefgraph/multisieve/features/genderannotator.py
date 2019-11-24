# coding=utf-8
""" Annotate the mentions with gender. Available values are UNKNOWN, MALE and
FEMALE from feature.constants module.

This module can use POS, NER and dictionaries from resources.

"""

from corefgraph.multisieve.features.constants import GENDER, MALE, FEMALE, NEUTRAL, \
    UNKNOWN, NUMBER, PLURAL, MENTION, PRONOUN_MENTION

from corefgraph.constants import FORM, NER, POS, ID
from corefgraph.multisieve.features.baseannotator import FeatureAnnotator
from corefgraph.resources.dictionaries import pronouns
from corefgraph.resources.files.gender import bergma_counter, female_names, \
    female_words, male_names, male_words, neutral_words
from corefgraph.resources.rules import rules
from corefgraph.resources.tagset import ner_tags, pos_tags

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '3/19/14'


class GenderAnnotator(FeatureAnnotator):
    """ Annotate mention gender.

    """
    name = "gender"

    features = [GENDER]

    use_bergsma_gender_lists = True
    use_names_list = True
    use_probabilistic_gender_classification = True

    prominence_boost = 0.5
    threshold = 2

    def extract_and_mark(self, mention):
        """ Extract the gender and annotate it into the mention.

        :param mention: The mention to annotate.
        :return: Nothing.
        """

        gender = self._get_gender(mention)
        self.logger.debug("Gender: Result -%s- #%s", gender, mention[FORM])
        mention[GENDER] = gender

    def _get_gender(self, mention):
        """ Pass trough a list of selector to get mention gender.

        :param mention: The mention to get gender
        :return: MALE, FEMALE, NEUTRAL or UNKNOWN constant.
        """
        head_word = self.graph_builder.get_head_word(mention)
        headword_pos = head_word[POS]
        headstring = rules.get_head_word_form(self.graph_builder, mention).lower()
        # Words until headwords
        mention_string = []
        for word in self.graph_builder.get_words(mention):
            mention_string.append(word[FORM])
            if word[ID] == head_word[ID]:
                break
        mention_string = " ".join(mention_string).lower()

        try:
            mention_type = mention[MENTION]
        except KeyError:
            self.logger.warning("warning: Gender without MENTION TYPE")
            mention_type = UNKNOWN
        try:
            mention_number = mention[NUMBER]
        except KeyError:
            self.logger.warning("warning: Gender without MENTION NUMBER")
            mention_number = UNKNOWN

        gender = self._pronoun_gender(mention_string, mention_type)
        if gender is not None:
            self.logger.debug("Gender: Pronoun")
            return gender

        if self.use_probabilistic_gender_classification and mention_number != PLURAL:
            gender_statistic = self._get_statistic_gender(headstring)
            if gender_statistic is not None:
                self.logger.debug("Gender: Statistical")
                return gender_statistic

        gender = self._person_gender(mention)
        if gender is not None:
            self.logger.debug("Gender: Person")
            return gender

        gender = self._pos_gender(headword_pos)
        if gender:
            self.logger.debug("Gender: Part-of-speech")
            return gender

        if self.use_names_list:
            gender = self._name_gender(mention_string)
            if gender:
                self.logger.debug("Gender: Name list -%s-", headstring)
                return gender

        if self.use_bergsma_gender_lists:
            gender = self._list_gender(mention_string)
            if gender:
                self.logger.debug("Gender: List -%s-", headstring)
                return gender

        return UNKNOWN

    @staticmethod
    def _pos_gender(word_pos):
        """ Use the mention POS to determine the feature.

        :param word_pos: The POS of the mention as String.
        :return: MALE, FEMALE, NEUTRAL constant or None.
        """
        if pos_tags.male(word_pos):
            return MALE
        if pos_tags.female(word_pos):
            return FEMALE
        if pos_tags.neutral(word_pos):
            return NEUTRAL
        return None

    @staticmethod
    def _pronoun_gender(word_form, mention_type):
        """ Check if is a pronoun and determine gender

        :param word_form: The lower case word form
        :return: if pronoun MALE, FEMALE, NEUTRAL or UNKNOWN constant,
            else None.
        """
        if mention_type == PRONOUN_MENTION:
            if pronouns.male(word_form):
                return MALE
            if pronouns.female(word_form):
                return FEMALE
            if pronouns.neutral(word_form):
                return NEUTRAL
            return UNKNOWN
        return None

    @staticmethod
    def _list_gender(word_form):
        """ Try to annotate the gender with a constant of names.

        :param word_form: The original-cased word form.
        :return: MALE, FEMALE, NEUTRAL constants or none.
        """
        if word_form.lower() in male_words:
            return MALE
        if word_form.lower() in female_words:
            return FEMALE
        if word_form.lower() in neutral_words:
            return NEUTRAL
        return None

    @staticmethod
    def _name_gender(word_form):
        """ Try to annotate gender with name by gender lists.

        :param word_form: The original-cased word form.
        :return: MALE, FEMALE constants or None.
        """
        if word_form.lower() in female_names:
            return FEMALE
        elif word_form.lower() in male_names:
            return MALE
        return None

    def _person_gender(self, mention):
        """ Check if the mention is a  person and use different approach to
        get word relevant to gender detection.

        :param mention: The mention to annotate.
        :return: if person MALE, FEMALE, NEUTRAL or UNKNOWN constant,
            else None.
        """
        if ner_tags.person(mention.get(NER)):
            for token in self.graph_builder.get_words(mention):
                word_form = token[FORM].lower()
                if word_form in male_words or word_form in male_names:
                    return MALE
                if word_form in female_words or word_form in female_names:
                    return FEMALE
            return UNKNOWN
        return None

    def _get_statistic_gender(self, mention_string):
        """ Use the Bergsma-Lin algorithm to set the gender of the mention.

        :param mention_string:  The lowe-case form of the mention.
        :return:  MALE, FEMALE, NEUTRAL constants or None.
        """
        if mention_string not in bergma_counter:
            return None
        male, female, neutral, plural = \
            bergma_counter.get(mention_string)
                    
        if (male * self.prominence_boost > female + neutral) and \
                (male > self.threshold):
            return MALE
        elif (female * self.prominence_boost > male + neutral) and \
                (female > self.threshold):
            return FEMALE
        elif (neutral * self.prominence_boost > male + female) and \
                (neutral > self.threshold):
            return NEUTRAL
        return None
