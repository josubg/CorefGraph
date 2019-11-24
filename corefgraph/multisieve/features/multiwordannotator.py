# coding=utf-8
""" Annotation of the mention multiwords.
"""


from corefgraph.constants import FORM, SPAN, BEGIN, END
import corefgraph.properties

from corefgraph.multisieve.features.baseannotator import FeatureAnnotator
from corefgraph.constants import MULTIWORD
from pynaf import NAFDocument
from socket import socket, error

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class MultiWordAnnotator(FeatureAnnotator):
    """Annotate the type of a mention(nominal, pronominal, pronoun) also search
    some relevant features of the mention(Mention subtype)"""

    name = "multiword"
    server_ip = "127.0.0.1"
    server_port = 1337
    features = [MULTIWORD]
    retry = 3

    def __init__(self, graph_builder):
        FeatureAnnotator.__init__(self, graph_builder)


        # try:
        #     self.server.connect((self.server_ip, self.server_port))
        #     self.error = False
        # except error as ex:
        #     self.logger.error("Error in IXA POS server: %s", ex.strerror)
        #     self.error = True

    def extract_and_mark(self, mention):
        """ Determine the type of the mention. Also check some mention related
        features.

        :param mention: The mention to be classified.
        """
        # if self.error:
        #     return

        form = mention[FORM]
        if "_" in form and len(form) > 1:
            for word in self.graph_builder.get_words(mention):
                word_form = word[FORM]
                if "_" in word_form and len(word_form) > 1 and MULTIWORD not in word:
                    word[MULTIWORD] = self.expand_words(word)

    def expand_words(self, word):
        form = word[FORM]
        form = form.replace("_", " ")


        # # TODO form += " es así."
        doc = NAFDocument(language=corefgraph.properties.lang)
        offset = 0
        for index, token in enumerate(form.split(" ")):
            if token:
                doc.add_word(token.decode(corefgraph.properties.encoding), "w{0}".format(index),
                             offset=str(offset), length=str(len(token)), sent="1")
                offset += len(token) + 1
        retry = self.retry
        while retry:
            try:
                self.server = socket()
                self.server.connect((self.server_ip, self.server_port))
                self.server.sendall(str(doc))
                retry = 0
            except error as ex:
                from time import sleep
                sleep(0.5)
                retry -= 1
                if not retry:
                    self.logger.error("Error in IXA POS server (retry exhausted): %s", ex.strerror)
        full_response = ""
        while True:
            response = self.server.recv(1024)
            full_response += response
            if not response:
                self.server.close()
                break
        naf = NAFDocument(input_stream=full_response)
        naf_pos = naf.get_words()
        naf_terms = naf.get_terms()
        words = []
        for index in range(len(naf_pos)):
            word_node = self.graph_builder.add_word(
                form=naf_pos[index].text.encode(naf.encoding),
                node_id="{0}_{1}".format(word["id"],index),
                label="{0}_{1}".format(word["label"],index),
                lemma=naf_terms[index].attrib['lemma'].encode(naf.encoding),
                pos=naf_terms[index].attrib['morphofeat'],
                span=word[SPAN],
                begin=word[BEGIN],
                end=word[END])
            words.append(word_node)
        return words
