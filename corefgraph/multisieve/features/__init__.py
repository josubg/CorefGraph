# coding=utf-8
""" This module contains the essential to filter extracted mention. Also
  autodiscover and publish to the system any class that comply this requisites:

+ Is a subclass of  BaseFilter
+ Is in a module inside this package

The filters classes are published in a dictionary ordered by short name. The
dictionary is called filters_by_name.
"""

from pkgutil import iter_modules
from baseannotator import FeatureAnnotator

__author__ = 'Josu Bermúdez <josu.bermudez@deusto.es>'

annotators_by_name = dict()

for element, name, is_package in \
        iter_modules(path=__path__, prefix=__name__+"."):
        module = element.find_module(name).load_module(name)
        for class_name in dir(module):
            annotator_class = getattr(module, class_name)
            # duck typing
            if hasattr(annotator_class, "extract_and_mark")\
                    and hasattr(annotator_class, "name") \
                    and callable(annotator_class.extract_and_mark)\
                    and annotator_class.name != "base":
                annotators_by_name[annotator_class.name] = annotator_class
all_annotators = annotators_by_name.keys()

