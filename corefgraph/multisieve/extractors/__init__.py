# coding=utf-8
""" This module contains the essential to extract and order mentions. Also
  autodiscover and publish to the system any class that comply this requisites:

+ Is a subclass of  BaseExtractor
+ Is in a module inside this package

The extractors classes are published in a dictionary ordered by short name. The
dictionary is called extractors_by_name.
"""

from pkgutil import iter_modules

__author__ = 'Josu Bermúdez <josu.bermudez@deusto.es>'

extractors_by_name = dict()

for element, name, is_package in \
        iter_modules(path=__path__, prefix=__name__+"."):
        module = element.find_module(name).load_module(name)
        for class_name in dir(module):
            annotator_class = getattr(module, class_name)
            # duck typing
            if hasattr(annotator_class, "extract")\
                    and hasattr(annotator_class, "name") \
                    and callable(annotator_class.extract)\
                    and annotator_class.name != "base":
                extractors_by_name[annotator_class.name] = annotator_class
all_extractors = extractors_by_name.keys()
