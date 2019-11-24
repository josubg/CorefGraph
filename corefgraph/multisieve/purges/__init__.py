# coding=utf-8
""" This module contains the essential to purge system response. Also
  autodiscover and publish to the system any class that comply this requisites:

+ Is a subclass of  BasePurge
+ Is in a module inside this package

The purges classes are published in a dictionary ordered by short name. The
dictionary is called purges_by_name
"""

from pkgutil import iter_modules
from basepurge import BasePurge

purges_by_name = dict()

for element, name, is_package in \
        iter_modules(path=__path__, prefix=__name__+"."):
        module = element.find_module(name).load_module(name)
        for class_name in dir(module):
            purge_class = getattr(module, class_name)
            # duck typing
            if hasattr(purge_class, "purge_mention")\
                    and hasattr(purge_class, "purge_entity") \
                    and hasattr(purge_class, "short_name") \
                    and callable(purge_class.purge_mention)\
                    and callable(purge_class.purge_entity)\
                    and purge_class.short_name != "base":
                purges_by_name[purge_class.short_name] = purge_class

all_purges = purges_by_name.keys()
