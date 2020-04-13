# coding=utf-8
""" All the sieves are published here for the multi-sieve system. They are
accessible to the multi-sieve system by their sort name. Also the default sieve
pack is defined here.
"""


from pkgutil import iter_modules
from logging import getLogger

from corefgraph.constants import SPAN

__author__ = 'Josu Bermúdez <josu.bermudez@deusto.es>'

logger = getLogger(__name__)

sieves_by_name = dict()
all_sieves = []
default = []

for element, name, is_package in \
        iter_modules(path=__path__, prefix=__name__+"."):
        module = element.find_module(name).load_module(name)
        for class_name in dir(module):
            sieve_class = getattr(module, class_name)
            # duck typing
            if hasattr(sieve_class, "are_coreferent")\
                    and hasattr(sieve_class, "short_name") \
                    and callable(sieve_class.are_coreferent)\
                    and sieve_class.short_name != "base":
                sieves_by_name[sieve_class.short_name] = sieve_class
                logger.debug("Sieve Loaded: %s", sieve_class.short_name)
                all_sieves.append(sieve_class.short_name)
                if hasattr(sieve_class, "auto_load") and sieve_class.auto_load:
                    default.append(sieve_class.short_name)


class MultiSieveProcessor:
    """A coreference detector based on the lee et all. 2013 Multisieve system
    of Stanford University.
    """
    logger = getLogger(__name__)

    def __init__(self, sieves_list, meta_info):
        self.links = []
        self.meta_info = meta_info
        self.logger.info("Sieves: %s", sieves_list)
        self.sieves_names = sieves_list
        # dynamically load the sieves
        self.sieves = self.load_sieves(sieves_list)

    def get_meta(self):
        # Create the meta structure
        meta = {
            sieve.short_name: sieve.get_meta()
            for sieve in self.sieves
        }
        return meta

    def process(self, graph_builder, mentions_text_order, mentions_candidate_order):
        """ Process a candidate cluster list thought the sieves using the output
         of the each sieve as input of the next.
        """
        sieve_output = {}
        # create the base entity inside each mention in each sentence
        for sentence in mentions_text_order:
            for mention in sentence:
                # mention is identified for first mention in its span
                entity = (mention[SPAN], [mention, ])
                # Store the entity reference in the mention
                mention["entity"] = entity
                # backup output in case of run with no sieves
                sieve_output[mention[SPAN]] = [mention, ]
        # Pass each sieve through all mentions
        for sieve in self.sieves:
            # Store sieve output for output, only last one is used
            sieve_output = sieve.resolve(graph_builder=graph_builder, mentions_order=mentions_text_order,
                                         candidates_order=mentions_candidate_order)
        # plain the output
        return [sieve_output[key] for key in sorted(sieve_output.keys())]

    def load_sieves(self, sieves_list):
        """ Load the sieves from a list of string. The id of the sieves to load
         is its short name.

        :param sieves_list: A list of string containing the short name of the
            strings to load.

        :return: A list of ready to use sieve objects.
        """
        # Load in order each sieve, initialize it and return a list with all sieves
        return [
            sieves_by_name[sieve_class](meta_info=self.meta_info)
            for sieve_class in sieves_list]