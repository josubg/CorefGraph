# coding=utf-8
""" All the sieves are published here for the multi-sieve system. They are
accessible to the multi-sieve system by their sort name. Also the default sieve
pack is defined here.
"""


from pkgutil import iter_modules
from logging import getLogger


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