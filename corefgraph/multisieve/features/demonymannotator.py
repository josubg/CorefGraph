# coding=utf-8
""" Provides the class necessary for annotate mentions with the number feature.

"""

from corefgraph.multisieve.features.constants import DEMONYM, LOCATION

from corefgraph.constants import FORM
from corefgraph.multisieve.features.baseannotator import FeatureAnnotator
from corefgraph.resources.files.demonym import *

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '3/19/14'


class DemonymAnnotator(FeatureAnnotator):
    """ Add number annotations for mentions
    """
    name = "demonym"

    features = [DEMONYM, LOCATION]

    def extract_and_mark(self, mention):
        """ Annotate the mention with the known demonym if is a location and
        with the known location if is a demonym

        :param mention: The mention to annotate
        """
        form = mention[FORM]
        if form in locations:
            mention[LOCATION] = demonym_by_location[form]
        if form in demonyms:
            mention[DEMONYM] = locations_by_demonyms[form]
