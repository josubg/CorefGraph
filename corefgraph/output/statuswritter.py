# coding=utf-8
""" Store the document in a KAF format(2.1).
"""


from corefgraph.output.basewriter import BaseDocument
from corefgraph.constants import SPAN, ID


__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class StatusDocument(BaseDocument):
    """ Store the document in a KAF format(2.1).
    """
    short_name = "STATUS"

    def store(self, graph_builder, encoding, coreference_processor, **kwargs):
        """ Store the graph in a string and return it.

        :param graph_builder: the graph to be stored.
        :param encoding: Encoding set on kaf document
        :param coreference_processor: A link to the coreference processor of the module.
        :param kwargs: Unused
        """

        gold_coreference = coreference_processor.coreference_gold
        proposed_coreference = coreference_processor.coreference_proposal

        gold_mentions_spans = set(
            [mention[SPAN]
             for entity in gold_coreference for mention in gold_coreference[entity]
             ])
        response_mentions_spans = set([mention[SPAN] for entity in proposed_coreference for mention in entity])

        predicted_links = coreference_processor.links

        found_mentions = []
        wrong_mentions = []
        lost_mentions = []
        processed_mentions = []
        for entity in proposed_coreference:
            processed_mentions_entity = []
            for mention in entity:
                if mention in processed_mentions:
                    self.logger.error("Repeated mention")
                    if mention in processed_mentions_entity:
                        self.logger.error("Same entity %s", [mention[ID] for mention in entity])
                processed_mentions_entity.append(mention)
                processed_mentions.append(mention)
                if mention[SPAN] in gold_mentions_spans:
                    found_mentions.append(mention)
                else:
                    wrong_mentions.append(mention)
                # del mention["entities"]

        for entity in gold_coreference:
            for mention in gold_coreference[entity]:
                if mention[SPAN] not in response_mentions_spans:
                    lost_mentions.append(mention)

        # link tupla: mention, candidate, entity, sieve_sort_name
        wrong_links = []
        for link in predicted_links:
            for gold_entity in gold_coreference:
                if link[0][SPAN] in gold_coreference[gold_entity]:
                    if link[1][SPAN] not in gold_coreference[gold_entity]:
                        wrong_links.append(link)

        for wrong_link in wrong_links:
            self.logger.info(
                "Wrong link: {3} {0} {1} ".format(*wrong_link)
            )

        sentences_roots = graph_builder.get_all_sentences()
        sentences = []
        for sentence_index, root in enumerate(sentences_roots):
            self.file.write("\n")
            sentences.append(graph_builder.get_sentence_words(root))

        # Store the info

        state = {
            "mention": {
                "found": list(found_mentions),
                "lost": list(lost_mentions),
                "wrong": list(wrong_mentions),
            },
            "links": {
                "predicted": predicted_links,
                "wrong": wrong_links,
            },
            "sentences": sentences
        }
