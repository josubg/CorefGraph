# coding=utf-8
""" Conll format document writer,

 Not all columns filled with real data, some always contains '-' or cloned data.
"""

from corefgraph.output.basewriter import BaseDocument
from corefgraph.constants import POS, NER,FORM, LEMMA, ID


__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class SemevalDocument(BaseDocument):
    """ Store the results into a plain text evaluable by the Semeval 2010 script
    """
    short_name = "semeval"

    def store(self, graph_builder, **kwargs):
        """ Stores the graph content in Semeval 2010 format into the object file.
        :param graph_builder: The graph to store.
        :param kwargs: Unused
        """
        self._annotate_ner(graph_builder, graph_builder.get_all_named_entities())
        for coref_index, entity in enumerate(graph_builder.get_all_coref_entities(), 1):
            self._annotate_mentions(graph_builder, graph_builder.get_all_entity_mentions(entity), coref_index)
            self.logger.debug(coref_index, entity, [x[ID] for x in graph_builder.get_all_entity_mentions(entity)])
        self.file.write("#begin document {0}".format(self.document_id))
        sentences_roots = graph_builder.get_all_sentences()
        for root in sentences_roots:
            self.file.write("\n")
            for word_index, word in enumerate(graph_builder.get_sentence_words(root), start=1):
                self.file.write(self._word_to_conll(word, str(word_index)))
        self.file.write("\n#end document\n")

    @staticmethod
    def _annotate_ner(graph_builder, named_entities):
        for ner in named_entities:
            # For each ner word assign ner value
            # and mark start and end with '(' and ')'
            words = graph_builder.get_words(ner)
            ner = ner.get(NER, "O")
            if len(words) > 1:
                words[0][NER] = words[0].get(NER, "") + "(" + ner
                words[-1][NER] = words[-1].get(NER, "") + ner + ")"
            else:
                words[0][NER] = words[0].get(NER, "") + "(" + ner + ")"

    def _annotate_mentions(self, graph_builder, mentions, cluster_index):
        for mention in mentions:
            # For each mention word assign the cluster id to cluster attribute
            # and mark start and end with '(' and ')'
            terms = graph_builder.get_words(mention)
            # Valid for 0, 1 and n list sides

            entity_mark = mention.get("entityx_id", str(cluster_index)).replace("c","")
            if terms:
                if len(terms) == 1:
                    self._mark_coreference(terms[0], "({0})".format(entity_mark))
                else:
                    self._mark_coreference(terms[0], "({0}".format(entity_mark))
                    self._mark_coreference(terms[-1], "{0})".format(entity_mark))

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

    @staticmethod
    def _word_to_conll(word, word_id):
        """A word in ConLL is represented with a line of text that is composed by a list of features separated by tabs.
        :param word: The word that is going to be parsed.
        """
        features = [
            word_id,
            word[FORM],
            word[LEMMA],
            word[LEMMA],
            word[POS],
            word[POS],
            word[POS],
            word[POS],
            "0",
            "0",
            "_",
            "_",
            word.get(NER, "O"),
            word.get(NER, "O"),
            "_",
            "_",
            "_",
            "_",
        ]
        if "coreference" in word:
            features.append("|".join(word["coreference"]))
        else:
            features.append("_")
        return "\t".join(features) + "\n"


class SemevalCONLLDocument(SemevalDocument):
    """ Store Semeval document int conll 2012 compatible format
    """
    short_name = "semevalCONLL"

    def store(self, graph_builder, **kwargs):
        """ Stores the graph content in Semeval 2010 format into the object file.
        :param graph_builder: The graph to store.
        :param kwargs: Unused
        """
        self._annotate_ner(graph_builder, graph_builder.get_all_named_entities())
        for coref_index, entity in enumerate(graph_builder.get_all_coref_entities(), 1):
            self._annotate_mentions(graph_builder, graph_builder.get_all_entity_mentions(entity), coref_index)
            self.logger.debug(coref_index, entity, [x[ID] for x in graph_builder.get_all_entity_mentions(entity)])
        self.file.write("#begin document ({0}); part 000".format(self.document_id))
        sentences_roots = graph_builder.get_all_sentences()
        for root in sentences_roots:
            self.file.write("\n")
            for word_index, word in enumerate(graph_builder.get_sentence_words(root), start=1):
                self.file.write(self._word_to_conll(word, str(word_index)))
        self.file.write("\n#end document\n")

    @staticmethod
    def _annotate_ner(graph_builder, named_entities):
        for ner in named_entities:
            # For each ner word assign ner value
            # and mark start and end with '(' and ')'
            words = graph_builder.get_words(ner)
            ner = ner.get(NER, "O")
            if len(words) > 1:
                words[0][NER] = words[0].get(NER, "") + "(" + ner
                words[-1][NER] = words[-1].get(NER, "") + ner + ")"
            else:
                words[0][NER] = words[0].get(NER, "") + "(" + ner + ")"

    def _word_to_conll(self,word, word_id):
        """A word in ConLL is represented with a line of text that is composed by a list of features separated by tabs.
        :param word: The word that is going to be parsed.
        """
        features = [
            self.document_id,
            "0",  # PART ID
            word_id,
            word[FORM],
            word[POS],
            word[LEMMA],
            "0",  # SPEAKER
            "_",
            "_",
            "_",
            word.get(NER, "O"),
        ]
        if "coreference" in word:
            features.append("|".join(word["coreference"]))
        else:
            features.append("-")
        return "\t".join(features) + "\n"
