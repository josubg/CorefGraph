# coding=utf-8
""" This module contains the essential to filter extracted mention. Also
  autodiscover and publish to the system any class that comply this requisites:

+ Is a subclass of  BaseFilter
+ Is in a module inside this package

The filters classes are published in a dictionary ordered by short name. The
dictionary is called filters_by_name.
"""

from pkgutil import iter_modules
from basefilter import BaseFilter

__author__ = 'Josu Bermúdez <josu.bermudez@deusto.es>'

filters_by_name = dict()

for element, name, is_package in \
        iter_modules(path=__path__, prefix=__name__+"."):
        module = element.find_module(name).load_module(name)
        for class_name in dir(module):
            filter_class = getattr(module, class_name)
            # duck typing
            if hasattr(filter_class, "filter")\
                    and hasattr(filter_class, "short_name") \
                    and callable(filter_class.filter)\
                    and filter_class.short_name != "base":
                filters_by_name[filter_class.short_name] = filter_class
all_filters = filters_by_name.keys()
