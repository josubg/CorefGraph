# coding=utf-8
"""Import(this module) and inherit(BaseFilter) to create a new filter.
The system will call the constructor(once) and the filter_mention function for
each mention obtained in the system. The filter calling order is not reliable.
"""


from logging import getLogger

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class BaseFilter(object):
    """ Base class for filters. To create a new filter import and inherit from
     this class.
    """

    short_name = "base"

    def __init__(self, graph_builder, extractor):
        self.logger = getLogger("{0}.{1}".format(__name__, self.short_name))
        self.graph_builder = graph_builder
        self.extractor = extractor

    def filter(self, mention, prev_mentions):
        """ Overload this in each filter.

        :param mention: The mention to test
        :return: True or False.
        """
        self.logger.warning("filter_mention not override!")
        return False
