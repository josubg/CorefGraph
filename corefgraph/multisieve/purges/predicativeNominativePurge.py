# coding=utf-8
""" Add the ability to purge Predicative nominative relation to the system.
"""

from basepurge import BasePurge
from corefgraph.constants import FORM, ID
from corefgraph.multisieve.features.constants import PREDICATIVE_NOMINATIVE

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class PredicativeNominativePurge(BasePurge):
    """ Purge any predicative nominative relation in the graph.
    """

    short_name = "PredicativeNominative"

    def purge_mention(self, mention):
        """ Purge relative Pronouns.

        :param mention: The mention to test
        :return: True or False.
        """
        if mention.get(PREDICATIVE_NOMINATIVE, False):
            self.logger.debug("Purged predicative nominative:  %s(%s)", mention[FORM], mention[ID])
            return True
        return False

    def purge_entity(self, entity):
        """ Nothing to do here.

        :param entity: Nothing to do here.
        :return: Nothing to do here.
        """
        return False
