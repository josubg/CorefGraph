# coding=utf-8
""" This module contains the essential to filter extracted mention. Also
  autodiscover and publish to the system any class that comply this requisites:

+ Is a subclass of  BaseFilter
+ Is in a module inside this package

The filters classes are published in a dictionary ordered by short name. The
dictionary is called filters_by_name.
"""
from collections import defaultdict, Counter
from pkgutil import iter_modules

from baseannotator import FeatureAnnotator
from corefgraph.constants import ID

__author__ = 'Josu Bermúdez <josu.bermudez@deusto.es>'


def _annotators_by_name():
    annotators = dict()

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
                    annotators[annotator_class.name] = annotator_class
    return annotators


class FeatureExtractor:
    annotators_by_name = _annotators_by_name()

    def __init__(self, graph_builder, mention_features, meta_info):
        self.graph_builder = graph_builder
        self.mention_features = mention_features
        self.feature_extractors = []
        self.meta_info = meta_info
        self.meta = {}
        if meta_info:
            self.prepare_meta()

    def load_extractors(self):
        self.feature_extractors = [
            self.annotators_by_name[annotator](self.graph_builder)
            for annotator in self.mention_features]

    def characterize_mention(self, mention):
        for feature_extractor in self.feature_extractors:
            # Feature Mention
            feature_extractor.extract_and_mark(mention=mention)
            # Save meta info from Features
            for feature in feature_extractor.features:
                feature_value = mention.get(feature, "unset")
                if isinstance(feature_value, dict):
                    feature_value = feature_value[ID]
                if isinstance(feature_value, set) or isinstance(feature_value, list):
                    feature_value = list()
                    for f in feature_value:
                        if isinstance(f, dict):
                            feature_value.append(f[ID])
                        else:
                            feature_value.append(f)
                else:
                    feature_value = feature_value
                if self.meta_info:
                    self.add_meta(feature, feature_value, mention)

    def add_meta(self, feature, feature_value, mention):
        self.meta['mentions'][mention[ID]][feature] = feature_value
        try:
            self.meta['counters'][feature][feature_value] += 1
        except TypeError:
            self.meta['counters'][feature]["NO_HASH"] += 1

    def get_meta(self):
        return self.meta

    def prepare_meta(self):
        self.meta = {
            'counters': defaultdict(Counter),
            'mentions': defaultdict(dict)}
