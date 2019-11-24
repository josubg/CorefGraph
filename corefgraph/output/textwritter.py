# coding=utf-8
from corefgraph.constants import NER, FORM, ID
from .basewriter import BaseDocument

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class TextDocument(BaseDocument):
    """ Store the results into a plain text evaluable by the Conll script
    """

    def store(self, graph_builder):
        """ Stores the graph content in Conll format into the object file.

        :param graph_builder: The graph is going to be stored.
        """
        if self.document_id:
            if "#" in self.document_id:
                document_id = self.document_id.split("#")[0]
                part_id = self.document_id.split("#")[1]
            else:
                self.logger.warning("unknown Document ID part : using 000")
                document_id = self.document_id
                part_id = "000"
        else:
            self.logger.warning("unknown Document ID: using document 000")
            document_id = "document"
            part_id = "000"

        self.annotate_ner(graph_builder, graph_builder.get_all_named_entities())

        for coref_index, entity in enumerate(graph_builder.get_all_coref_entities(), 1):
            self.annotate_mentions(
                graph_builder, graph_builder.get_all_entity_mentions(entity), coref_index)
            self.logger.debug(
                coref_index, entity,
                [x[ID] for x in graph_builder.get_all_entity_mentions(entity)])

        self.file.write("#begin document ({0}); part {1}\n".format(document_id, part_id))

        sentences_roots = graph_builder.get_all_sentences()
        for sentence_index, root in enumerate(sentences_roots):
            for word_index, word in enumerate(graph_builder.get_sentence_words(root)):
                coref = list(word.get("coreference", []))
                pre_mark = []
                post_mark = []
                for mark in coref:
                    if mark[0] == "[":
                        pre_mark += mark
                    if mark[-1] == "]":
                        post_mark += mark
                self.file.write("".join(pre_mark))
                self.file.write(word[FORM])
                self.file.write("".join(post_mark))
                self.file.write(" ")
            self.file.write("\n")
        self.file.write("\n#end document\n")

    @staticmethod
    def annotate_ner(graph_builder, ners):
        for ner in ners:
            # For each ner word assign ner value
            # and mark start and end with '(' and ')'
            words = graph_builder.get_words(ner)
            ner = ner.get(NER, "O")
            words[0][NER] = words[0].get(NER, "") + "("
            for word in words:
                word[NER] = word.get(NER, "") + ner
            words[-1][NER] = words[-1].get(NER, "") + ")"

    def annotate_mentions(self, graph_builder, mentions, cluster_index):
        for mention in mentions:
            # For each mention word assign the cluster id to cluster attribute
            # and mark start and end with '(' and ')'
            terms = graph_builder.get_words(mention)
            # Valid for 0, 1 and n list sides
            if terms:
                if len(terms) == 1:
                    self._mark_coreference(terms[0], "[{0}".format(cluster_index))
                    self._mark_coreference(terms[0], "{0}]".format(cluster_index))
                else:
                    self._mark_coreference(terms[0], "[{0}".format(cluster_index))
                    self._mark_coreference(terms[-1], "{0}]".format(cluster_index))

    @staticmethod
    def _mark_coreference(word, coreference_string):
        """ Append to a word a coreference string
        :param word: The word that forms part of a mention
        :param coreference_string: The coreference string
        """
        if "coreference" not in word:
            word["coreference"] = [coreference_string]
        else:
            word["coreference"].append(coreference_string)
