# coding=utf-8
""" Annotate the person of the mention.
"""
from corefgraph.constants import FORM
from .baseannotator import FeatureAnnotator
from corefgraph.resources.dictionaries import pronouns
from .constants import PERSON, UNKNOWN, FIRST_PERSON, SECOND_PERSON, \
    THIRD_PERSON

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '3/19/14'


class PersonAnnotator(FeatureAnnotator):
    """ Annotator of the person of the mention.
    """
    name = "person"
    features = [PERSON, ]

    def extract_and_mark(self, mention):
        """ Return a representative string for the person of the mention.

        :param mention: The mention to annotate
        """
        form = mention[FORM].lower()
        if pronouns.first_person(form):
            mention[PERSON] = FIRST_PERSON
        elif pronouns.second_person(form):
            mention[PERSON] = SECOND_PERSON
        elif pronouns.third_person(form):
            mention[PERSON] = THIRD_PERSON
        else:
            mention[PERSON] = UNKNOWN
