# coding=utf-8
"""Import(this module) and inherit(BasePurge) to create a new purge.
The system will call the constructor(once) and the purge_mention and
purge_entity function for each entity and mention obtained in the system.

The filter calling order is not reliable.
"""

from basepurge import BasePurge
from corefgraph.constants import FORM, ID

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class SingletonPurge(BasePurge):
    """ Purge any singleton in the system
    """

    short_name = "Singleton"

    def purge_mention(self, mention):
        """ Nothing to do here.

        :param mention: The mention to test
        :return: True or False.
        """
        return False

    def purge_entity(self, entity):
        """ Purge any .

        :param entity: The entity to test
        :return: True or False.
        """
        if len(entity) < 2:
            mention = entity[0]
            self.logger.debug("Purged singleton: %s(%s)", mention[FORM], mention[ID])
            return True
        return False
