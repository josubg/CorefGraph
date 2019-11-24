# coding=utf-8
""" Filter for remove the demonym mentions from the system."""

from .basefilter import BaseFilter
from corefgraph.resources.files.demonym import demonyms, locations
from corefgraph.constants import FORM, ID

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class DemonymFilter(BaseFilter):
    """ Class that filter mentions that are demonym."""

    short_name = "DemonymFilter"

    def filter(self, mention, prev_mentions):
        """ check if the mention have the demonym feature mark.

        :param mention: The mention to test.
        :return: True or False.
        """
        form = mention[FORM]
        if form in demonyms and form not in locations:
            self.logger.debug(
                "Mention is demonym:  %s(%s)", mention[FORM], mention[ID])
            return True
        return False
