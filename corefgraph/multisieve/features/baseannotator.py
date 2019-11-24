# coding=utf-8
""" The base class for the annotators.
"""
from logging import getLogger

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '19/3/14'  # DD/MM/YY


class FeatureAnnotator(object):
    """ The base class for the annotators

    """

    # Fill with the features that annotator will fill
    name = "base"
    features = []

    def __init__(self, graph_builder):
        self.logger = getLogger("{0}.{1}".format(__name__, self.name))
        self.graph_builder = graph_builder

    def extract_and_mark(self, mention):
        """ Override with the annotation of the mention.

        :param mention: The mention that is going to be  annotated.

        :return: Nothing.
        """
        pass
