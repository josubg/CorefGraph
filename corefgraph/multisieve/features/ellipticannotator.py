# coding=utf-8
""" Annotate the mentions with gender. Available values are UNKNOWN, MALE and
FEMALE from feature.constants module.

This module can use POS, NER and dictionaries from resources.

"""

from corefgraph.multisieve.features.constants import GENDER, MALE, FEMALE, NEUTRAL, \
    UNKNOWN, NUMBER, PLURAL,  SINGULAR, ANIMACY, ANIMATE

from corefgraph.constants import FORM, POS ,LEMMA
from corefgraph.multisieve.features.baseannotator import FeatureAnnotator
from corefgraph.resources.dictionaries import verbs

from corefgraph.resources.tagset import pos_tags

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '3/19/14'


class EllipticAnnotator(FeatureAnnotator):
    """ Annotate mention gender.

    """
    name = "elliptic"

    def extract_and_mark(self, mention):
        """ Extract the gender and annotate it into the mention.

        :param mention: The mention to annotate.
        :return: Nothing.
        """
        if mention[FORM] == "_":
            sentence_words = self.graph_builder.get_words(self.graph_builder.get_root(mention))
            words = self.graph_builder.get_words(mention)

            first_word_index = sentence_words.index(words[0])
            last_word_index = sentence_words.index(words[-1])

            if last_word_index + 1 < len(sentence_words):
                next_word = sentence_words[last_word_index+1]
                if pos_tags.verb(next_word[POS]):
                    self._extract(mention, next_word)
                    if next_word[LEMMA] == "haber" and \
                            pos_tags.verb(sentence_words[last_word_index + 2][POS]):
                        self._set_animate(mention, sentence_words[last_word_index + 2])
                    else:
                        self._set_animate(mention, sentence_words[last_word_index + 1])

                elif ((last_word_index + 2 < len(sentence_words))
                    and pos_tags.verb(sentence_words[last_word_index + 2][POS])):
                        self._extract(mention, sentence_words[last_word_index + 2])
                        self._set_animate(mention, sentence_words[last_word_index + 2])

            if first_word_index > 0:
                prev_word = sentence_words[first_word_index - 1]
                if pos_tags.verb(prev_word[POS]):
                    self._set_animate(mention, prev_word)
                    if first_word_index > 1 and \
                        pos_tags.verb(sentence_words[first_word_index - 2][POS]):
                            self._extract(mention, sentence_words[first_word_index - 2])
                    else:
                        self._extract(mention, prev_word)

    def _extract(self, mention, next_word):
        word_pos = next_word[POS]
        if pos_tags.singular(word_pos):
            mention[NUMBER] = SINGULAR
        elif pos_tags.plural(word_pos):
            mention[NUMBER] = PLURAL
        else:
            mention[NUMBER] = UNKNOWN

        if pos_tags.male(word_pos):
            mention[GENDER] = MALE
        if pos_tags.female(word_pos):
            mention[GENDER] = FEMALE
        if pos_tags.neutral(word_pos):
            mention[GENDER] = NEUTRAL
        else:
            mention[GENDER] = UNKNOWN

    def _set_animate(self, mention, next_word):
        if verbs.reporting(next_word[LEMMA]):
            mention[ANIMACY] = ANIMATE
