# coding=utf-8
""" Annotate the generic mentions.

"""

from corefgraph.multisieve.features.constants import GENERIC

from corefgraph.constants import POS, FORM, SPAN, LEMMA, ID
from corefgraph.multisieve.features.baseannotator import FeatureAnnotator
from corefgraph.resources.dictionaries import pronouns, verbs
from corefgraph.resources.tagset import pos_tags

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '3/19/14'


class GenericsAnnotator(FeatureAnnotator):
    """Annotator of the generic mentions.
    """
    name = "generic"
    features = [GENERIC]

    def extract_and_mark(self, mention):
        """Check and set generic feature for generic mentions.

        :param mention: The mention to check.
        :return Nothing.
        """
        mention[GENERIC] = False
        head_word = self.graph_builder.get_head_word(mention)
        # Bare plural
        if pos_tags.plural_common_noun(head_word[POS]) and \
                (mention[SPAN][1] - mention[SPAN][0] == 0):
            if pronouns.all_pronouns(mention[FORM]):
                #return False
                pass
            mention[GENERIC] = True
        # Generic you as in "you know"
        elif mention[self.graph_builder.doc_type] != self.graph_builder.doc_article and \
                pronouns.second_person(mention[FORM].lower()):
            you = head_word
            sentence = self.graph_builder.get_root(you)
            words = [word
                     for word
                     in self.graph_builder.get_sentence_words(sentence)]
            you_index = words.index(you)
            if (you_index + 1 < len(words)) and \
                    verbs.generics_you_verbs(
                         words[you_index + 1][FORM].lower()):
                        # words[you_index + 1][LEMMA].lower()):
                mention[GENERIC] = True
