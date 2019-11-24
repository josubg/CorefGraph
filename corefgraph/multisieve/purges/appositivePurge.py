# coding=utf-8
"""Import(this module) and inherit(BasePurge) to create a new purge.
The system will call the constructor(once) and the purge_mention and
purge_entity function for each entity and mention obtained in the system.

The filter calling order is not reliable.
"""

from basepurge import BasePurge
from corefgraph.constants import FORM, ID
from corefgraph.multisieve.features.constants import APPOSITIVE

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class AppositivePurge(BasePurge):
    """ Purge any appositive in the system
    """

    short_name = "Appositive"

    def purge_mention(self, mention):
        """ Purge relative Pronouns.

        :param mention: The mention to test
        :return: True or False.
        """
        app = mention.get(APPOSITIVE)
        # The appositive flag is not
        #if app is True:
        if app:
            self.logger.debug("Purged Apposition:  %s(%s)", mention[FORM], mention[ID])
            return True
        return False

    def purge_entity(self, entity):
        """ Nothing to do here.

        :param entity: Nothing to do here.
        :return: Nothing to do here.
        """
        pass
        return False
