# coding=utf-8
"""Import(this module) and inherit(BasePurge) to create a new purge.
The system will call the constructor(once) and the purge_mention and
purge_entity function for each entity and mention obtained in the system.

The filter calling order is not reliable.
"""

from basepurge import BasePurge
from corefgraph.constants import FORM, ID
from corefgraph.multisieve.features.constants import RELATIVE_PRONOUN

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class RelativePronounPurge(BasePurge):
    """ Purge any singleton in the system
    """

    short_name = "RelativePronoun"

    def purge_mention(self, mention):
        """ Purge relative Pronouns.

        :param mention: The mention to test
        :return: True or False.
        """
        if mention.get(RELATIVE_PRONOUN):
            self.logger.debug("Purged relative Pronoun:  %s(%s)", mention[FORM], mention[ID])
            return True
        return False

    def purge_entity(self, entity):
        """Nothing to do here.

        :param entity: Nothing to do here.
        :return: Nothing to do here.
        """
        return False
