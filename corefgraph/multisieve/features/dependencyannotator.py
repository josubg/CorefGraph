# coding=utf-8
""" Set mention features based on dependency relations

"""

from corefgraph.constants import POS
from .baseannotator import FeatureAnnotator
from corefgraph.resources.tagset import pos_tags, dependency_tags
from .constants import OBJECT, SUBJECT
from logging import getLogger

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '3/19/14'


class DependencyAnnotator(FeatureAnnotator):
    """ Check mention dependencies and annotate any feature from it.

    """
    name = "dependency"

    features = [OBJECT, SUBJECT]

    def extract_and_mark(self, mention):
        """Check and set the mention subject-object relation attributes
        
        :param mention: The mention to check
        :return Nothing
        """
        base_word = self.graph_builder.get_head_word(mention)
        dependants = self.graph_builder.get_governor_words(base_word)
        mention[SUBJECT] = False
        mention[OBJECT] = False

        for dependant in dependants:
            dependency = dependant[1]["value"]
            linked_word = dependant[0]
            if pos_tags.verb(linked_word[POS]):
                if dependency_tags.subject(dependency):
                    mention[SUBJECT] = linked_word
                    mention[OBJECT] = False
                    return
                if dependency_tags.object(dependency):
                    mention[SUBJECT] = False
                    mention[OBJECT] = linked_word
                    return
