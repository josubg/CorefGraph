# coding=utf-8
""" Conll format document writer,

 Not all columns filled with real data, some always contains '-'.
"""

from corefgraph.constants import FORM, UTTERANCE, NER, ID, LEMMA
from corefgraph.constants import POS
from corefgraph.multisieve.features.constants import SPEAKER, GENDER, ANIMACY, NUMBER
from .basewriter import BaseDocument

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class DebugDocument(BaseDocument):
    """ Store the results into a plain text evaluable by the Conll script
    """
    short_name = "DEBUG"

    def store(self, graph_builder, graph,  **kwargs):
        """ Stores the graph content in Conll format into the object file.
        :param graph: The graph to store.
        :param kwargs: Unused
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

        self.logger.error("DOCTYPE: {0}#{1} {2}".format(document_id, part_id, graph_builder.get_doc_type()))
        self._annotate_ner(graph_builder, graph_builder.get_all_named_entities())
        for coref_index, entity in enumerate(graph_builder.get_all_coref_entities(), 0):
            self._annotate_mentions(graph_builder, graph_builder.get_all_entity_mentions(entity), coref_index)
            self.logger.debug(coref_index, entity, [x[ID] for x in graph_builder.get_all_entity_mentions(entity)])

        self.file.write("#begin document ({0}); part {1}".format(document_id, part_id))
        sentences_roots = graph_builder.get_all_sentences()
        for sentence_index, root in enumerate(sentences_roots):
            self.file.write("\n")
            for word_index, word in enumerate(graph_builder.get_sentence_words(root)):
                self.file.write(self._word_to_conll(word, document_id, str(int(part_id)), str(word_index)))
        self.file.write("\n#end document\n")

    @staticmethod
    def _annotate_ner(graph_builder, named_entities):
        for ner in named_entities:
            # For each ner word assign ner value
            # and mark start and end with '(' and ')'
            words = graph_builder.get_words(ner)
            ner = ner.get(NER, "O")
            words[0][NER] = words[0].get(NER, "") + "("
            for word in words:
                word[NER] = word.get(NER, "") + ner
            words[-1][NER] = words[-1].get(NER, "") + ")"

    def _annotate_mentions(self, graph_builder, mentions, cluster_index):
        for mention in mentions:
            # For each mention word assign the cluster id to cluster attribute
            # and mark start and end with '(' and ')'
            terms = graph_builder.get_words(mention)
            # Valid for 0, 1 and n list sides
            self.logger.debug(
                "ANNOTATED: %s %s:%s",
                mention[ID],
                mention[FORM],
                " ".join([word[FORM] for word in terms])
            )
            speaker = mention[SPEAKER]
            gender = mention[GENDER]
            animacy = mention[ANIMACY]
            number = mention[NUMBER]
            mention = mention["mention"]
            for term in terms:
                term[SPEAKER] = speaker
                term[GENDER] = gender
                term[ANIMACY] = animacy
                term[NUMBER] = number
                term["mention"] = mention

            if terms:
                if len(terms) == 1:
                    self._mark_coreference(terms[0], "({0})".format(cluster_index))
                else:
                    self._mark_coreference(terms[0], "({0}".format(cluster_index))
                    self._mark_coreference(terms[-1], "{0})".format(cluster_index))

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
    def _word_to_conll(word, document_id, part_id, word_id):
        """A word in ConLL is represented with a line of text that is composed by a list of features separated by tabs.
        :param word: The word that is going to be parsed.
        """
        speaker = word.get(SPEAKER, "X")
        if type(speaker) is dict:
            speaker = speaker[FORM]
        features = [
            document_id,
            part_id,
            word_id,
            word[FORM],
            word[POS],
            word[LEMMA],
            word.get(GENDER, 'X'),
            word.get(ANIMACY, 'X'),
            word.get(NUMBER, 'X'),
            speaker,
            str(word.get(UTTERANCE, 1337)),
            word.get(NER, "O"),
            word.get("mention", 'X'),
        ]
        if "coreference" in word:
            sorted_ids = []
            for coreference_id in reversed(word["coreference"]):
                if coreference_id.startswith("("):
                    sorted_ids.append(coreference_id)
            for coreference_id in word["coreference"]:
                if not coreference_id.startswith("("):
                    sorted_ids.append(coreference_id)
            features.append("|".join(sorted_ids))
        else:
            features.append("-")
        return "   ".join(features) + "\n"
