# coding=utf-8
""" Annotation of the mention type and subtype.
"""

from corefgraph.constants import HEAD_OF_NER, NER
from corefgraph.multisieve.features.baseannotator import FeatureAnnotator

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '3/19/14'


class MentionTypeAnnotator(FeatureAnnotator):
    """Annotate ner type of the head word in the mention."""

    name = "ner"
    features = [NER]

    def extract_and_mark(self, mention):
        """ Determine the type of the mention. Also check some mention related
        features.

        :param mention: The mention to be classified.
        """
        mention[NER] = self.graph_builder.get_head_word(mention).get(HEAD_OF_NER, "O")
