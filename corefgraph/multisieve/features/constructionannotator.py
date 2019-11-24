# coding=utf-8
""" Annotation of the features based on syntax constructions.

"""

from .baseannotator import FeatureAnnotator
from .constants import APPOSITIVE, PREDICATIVE_NOMINATIVE, ATTRIBUTIVE, PLEONASTIC
from corefgraph.resources.rules import rules

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '3/19/14'


class ConstructionAnnotators(FeatureAnnotator):
    """ Annotator of the syntax construction features.
    """
    name = "construction"

    # True/False features
    features = [APPOSITIVE, PREDICATIVE_NOMINATIVE, ATTRIBUTIVE, PLEONASTIC]

    def extract_and_mark(self, mention):
        """ Annotate syntax constructions(appositive, predicative nominative).

        :param mention: The mention thar is going to be annotated.
        """
        mention[APPOSITIVE] = rules.is_appositive_construction_child(self.graph_builder, mention)
        mention[PREDICATIVE_NOMINATIVE] = rules.is_predicative_nominative(self.graph_builder, mention)
        mention[PLEONASTIC] = rules.is_pleonastic(constituent=mention, graph_builder=self.graph_builder)
        #mention[ATTRIBUTIVE] = rules.is_attributive(self.graph_builder, mention)
