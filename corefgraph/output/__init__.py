# coding=utf-8
""" Find all class in the submodules that complains with output interface.
"""


from pkgutil import iter_modules
from basewriter import BaseDocument

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '11/28/12'

writers = {}

for element, name, is_package in \
        iter_modules(path=__path__, prefix=__name__+"."):
        module = element.find_module(name).load_module(name)
        for class_name in dir(module):
            writer_class = getattr(module, class_name)
            # duck typing
            if hasattr(writer_class, "store")\
                    and hasattr(writer_class, "short_name") \
                    and callable(writer_class.store)\
                    and writer_class.short_name != "base":
                writers[writer_class.short_name] = writer_class
