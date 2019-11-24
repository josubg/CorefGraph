# coding=utf-8
from corefgraph.constants import ID
from .baseannotator import FeatureAnnotator

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '3/19/14'

#
# class GoldAnnotator(FeatureAnnotator):
#
#     """Annotate the mention appearance in the gold mentions."""
#
#     features = ["GOLD_MENTION"]
#     name = "gold"
#
#
#     def extract_and_mark(self, mention):
#         """ Determine the type of the mention. Also check some mention related
#         features.
#
#         :param mention: The mention to be classified.
#         """
#         mention_id = mention[ID]
#         if mention_id in self.extractor.gold_mentions_by_constituent:
#             for gold_mention in \
#                     self.extractor.gold_mentions_by_constituent.pop(mention_id):
#                 mention["GOLD_MENTION"] = True
#                 return
#         mention["GOLD_MENTION"] = False
