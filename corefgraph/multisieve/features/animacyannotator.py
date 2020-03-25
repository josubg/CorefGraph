# coding=utf-8
""" Annotator of the animacy feature
"""

import re

from corefgraph.multisieve.features.constants import ANIMACY, INANIMATE, ANIMATE, UNKNOWN

from corefgraph.constants import POS, NER
from corefgraph.multisieve.features.baseannotator import FeatureAnnotator
from corefgraph.resources.dictionaries import pronouns
from corefgraph.resources.files.animate import animate_words, inanimate_words
from corefgraph.resources.rules import rules
from corefgraph.resources.tagset import pos_tags, ner_tags


__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '3/19/14'


class AnimacyAnnotator(FeatureAnnotator):
    """ Marks the animacy of the mentions using their NER, POS and form.
    """
    name = "animacy"
    features = [ANIMACY]

    use_bergsma_number_lists = True

    def extract_and_mark(self, mention):
        """ Extract and mark the animacy of the mention.

        The animacy is marked as ANIMATE, INANIMATE or UNKNOWN constant in the
        ANIMACY attribute of the mention.

        :param mention: The mention to mark.
        :return: Nothing
        """
        mention[ANIMACY] = self._get_animacy(mention=mention)

    def _get_animacy(self, mention):
        """Determines the gender of the word.

        :param mention: The mention which animacy is wanted.
        :return: ANIMATE, INANIMATE or UNKNOWN constant
        """
        head_word = self.graph_builder.get_head_word(mention)
        word_form = rules.get_head_word_form(self.graph_builder, mention)
        word_ner = mention.get(NER)
        word_pos = head_word.get(POS)
        # Normalize parameters
        normalized_ner = word_ner
        normalized_form = word_form.lower()
        normalized_form = re.sub("\d", "0", normalized_form)
        normalized_pos = word_pos.replace("$", "")
        # Pronouns
        if pos_tags.pronoun(normalized_pos) or pronouns.all(normalized_form):
            if pronouns.inanimate(normalized_form):
                return INANIMATE
            elif pronouns.animate(normalized_form):
                return ANIMATE
            else:
                return UNKNOWN
        # NER
        if ner_tags.animate(normalized_ner):
            return ANIMATE
        if ner_tags.inanimate(normalized_ner):
            return INANIMATE

        # Use the mention POS to determine the feature
        if pos_tags.inanimate(word_pos):
            return INANIMATE
        if pos_tags.animate(word_pos):
            return ANIMATE
        # Bergsma Lists
        if self.use_bergsma_number_lists:
            if word_form in animate_words:
                return ANIMATE
            if word_form in inanimate_words:
                return INANIMATE
        return UNKNOWN
