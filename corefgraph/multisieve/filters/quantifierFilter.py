# coding=utf-8
""" Filter for remove mentions that starts with a quantifier."""

from corefgraph.multisieve.filters.basefilter import BaseFilter
from corefgraph.resources.dictionaries import determiners
from corefgraph.constants import FORM, ID

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class QuantifierFilter(BaseFilter):
    """ Class to remove mentions that  starts with a quantifier."""

    short_name = "QuantifierFilter"

    def filter(self, mention, prev_mentions):
        """ Check if the mention starts with a quantifier.

        :param mention: The mention to test.
        :return: True or False.
        """
        form = mention[FORM].lower()
        if determiners.quantifiers(form.split()[0]):
            self.logger.debug(
                "Mention starts with quantifier: %s(%s)", mention[FORM], mention[ID])
            return True
        return False
