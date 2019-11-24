# coding=utf-8
""" This module contains the essential to create  and manage mention extractors.
 Also  autodiscover and publish to the system any class that comply this requisites:

+ Is a subclass of  BaseCatcher
+ Is in a module inside this package

The filters classes are published in a dictionary ordered by short name. The
dictionary is called filters_by_name
"""

from pkgutil import iter_modules
from baseCatcher import BaseCatcher

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"

catchers_by_name = dict()

for element, name, is_package in \
        iter_modules(path=__path__, prefix=__name__+"."):
    if "Catcher" in name and not is_package:
        module = element.find_module(name).load_module(name)
        for class_name in dir(module):
            catcher_class = getattr(module, class_name)
            # duck typing Have a catch method, a short_name and is not the base class
            if hasattr(catcher_class, "catch")\
                    and hasattr(catcher_class, "short_name") \
                    and callable(catcher_class.catch)\
                    and catcher_class.short_name != "base":
                catchers_by_name[catcher_class.short_name] = catcher_class

all_catchers = catchers_by_name.keys()
