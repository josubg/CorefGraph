# coding=utf-8
""" Conll format document writer,

 Not all columns filled with real data, some always contains '-'.
"""

from .basewriter import BaseDocument


__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class DebugDocument(BaseDocument):
    """ Store the results into a plain text evaluable by the Conll script
    """
    short_name = "ARFF"

    def store(self, graph_builder,  **kwargs):
        """ Stores the graph content in Conll format into the object file.
        :param graph: The graph to store.
        :param kwargs: Unused
        """
        import arff
        data = []
        entities = graph_builder.get_all_coref_entities()
        self.logger.debug("entities: %s", len(entities))
        for entity in entities:
            mentions = graph_builder.get_all_entity_mentions(entity)
            self.logger.debug("Mentions: %s", len(mentions))
            for mention in mentions:
                surface_learn = mention.get("surface_learn", {})

                self.logger.debug("links: %s", len(surface_learn))
                for link in surface_learn:
                    data.append(surface_learn[link])
                    self.logger.debug("link: %s: ", surface_learn[link])

        boolean = [str(True), str(False)]

        arff_file = {
            'attributes': [
                ('relax_match', boolean),
                ('mention_enumeration', boolean),
                ('candidate_enumeration', boolean),
                ('mention_appositive', boolean),
                ('candidate_appositive', boolean),
                ('equal_names', 'REAL'),
                ('equal_adjectives', 'REAL'),
                ('equal_rest', 'REAL'),
                ('extra_mention_names', 'REAL'),
                ('extra_mention_adjectives', 'REAL'),
                ('extra_mention_rest', 'REAL'),
                ('extra_candidate_names', 'REAL'),
                ('extra_candidate_adjectives', 'REAL'),
                ('extra_candidate_rest', 'REAL'),
                ('mention', 'STRING'),
                ('candidate', 'STRING'),
                ('sentence_distance', 'INTEGER'),
                

                ('linked', boolean)],
            'description': 'surface relations between mentions',
            'relation': 'surface',
            'data': data
        }
        if len(data):
            self.file.write(arff.dumps(arff_file))
        else:
            self.logger.info("Empty data")
