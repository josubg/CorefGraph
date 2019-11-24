# coding=utf-8
"""Import(this module) and inherit(BasePurge) to create a new purge.
The system will call the constructor(once) and the purge_mention and
purge_entity function for each entity and mention obtained in the system.

The filter calling order is not reliable if not set by parameter.
"""

from logging import getLogger

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class BasePurge:
    """ Base class for purges. To create a new purge import and inherit from
     this class.
    """

    short_name = "base"

    def __init__(self, graph_builder, extractor):
        self.logger = getLogger("{0}.{1}".format(__name__, self.short_name))
        self.graph_builder = graph_builder
        self.extractor = extractor

    def purge_mention(self, mention):
        """ Overload this in each purge.

        :param mention: The mention to test
        :return: True or False.
        """
        self.logger.warning("mention_mention not override!")
        return False

    def purge_entity(self, entity):
        """ Overload this in each purge.

        :param entity: The entity to test
        :return: True or False.
        """
        self.logger.warning("purge_entity not override!")
        return False
