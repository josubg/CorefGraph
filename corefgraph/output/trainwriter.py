# coding=utf-8
""" Conll format document writer,

 Not all columns filled with real data, some always contains '-'.
"""


from .basewriter import BaseDocument
from pickle import dump

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class TrainDocument(BaseDocument):
    """ Store the results into a plain text evaluable by the Conll script
    """
    short_name = "TRAIN"

    def store(self, graph_builder, **kwargs):
        """ Stores the graph content in Conll format into the object file.
        :param graph: The graph to store.
        :param kwargs: Unused
        """
        features = []
        target = []
        data = {"data": features, "target": target}

        for entity in graph_builder.get_all_coref_entities():
            for mention_candidate in graph_builder.get_all_entity_mentions(entity):

                target.append(mention_candidate["mention_gold"])
                features.append(mention_candidate["features"])
        dump(data, self.file)
