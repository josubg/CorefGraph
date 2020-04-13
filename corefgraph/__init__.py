# coding=utf-8
"""CorefGraph Main module.
The system is not a replica of the system described in the papers. The system is a reimplementation that describes using
the base approach of sieves. This system includes the sieves and the specifics algorithm described in the paper, but it
designed to be able to dynamically load almost any feature, any catching or any sieve in any language. It also includes
some of these  possible algorithms but as said its capable of accommodate new algorithms(classes) to meet your needs.


Heeyoung Lee, Angel Chang, Yves Peirsman, Nathanael Chambers, Mihai Surdeanu and Dan Jurafsky.
Deterministic coreference resolution based on entity-centric, precision-ranked rules.
Computational Linguistics 39(4), 2013.

"""
import logging
from collections import defaultdict, Counter

from corefgraph.constants import ID

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>, Rodrigo Agerri <rodrigo.agerri@ehu.es>'
__version__ = '1.1.0'
__license__ = 'Apache License Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0> '


class Corefgraph:
    """ Process a single text or corpus with several NLP stages managing the
    result as graphs.
    """

    def __init__(self, verbose, reader, secure_tree, lang, sieves,
                 extractor_options, mention_extractor, candidate_extractor, mention_catchers,
                 mention_filters, mention_features, mention_purges, meta_info):
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        self.logger.info("Extractor Options %s", extractor_options)
        # Options
        self.lang = lang
        self.sieves = sieves
        self.extractor_options = extractor_options
        self.mention_extractor = mention_extractor
        self.candidate_extractor = candidate_extractor
        self.mention_catchers = mention_catchers
        self.mention_filters = mention_filters
        self.mention_purges = mention_purges
        self.meta_info = meta_info

        # Graph builder and manager
        self.graph_builder = None
        self.coreference_processor = None
        self.feature_extractor = None
        self.meta = {}
        self.mention_features = mention_features
        self.reader = reader
        self.secure_tree = secure_tree

    def reset_graph(self):
        """Reset the graph and the elements that used a graph reference."""
        # Prepare graph Builder
        from corefgraph.multisieve.features import FeatureExtractor
        from graph.nafbuilder import NafAndTreeGraphBuilder
        from corefgraph.multisieve import CoreferenceProcessor

        self.graph_builder = NafAndTreeGraphBuilder(
            self.reader, self.secure_tree)
        # Prepare coreference processor
        self.coreference_processor = CoreferenceProcessor(
            graph_builder=self.graph_builder,
            extractor_options=self.extractor_options,
            mention_extractor=self.mention_extractor,
            candidate_extractor=self.candidate_extractor,
            mention_catchers=self.mention_catchers,
            mention_filters=self.mention_filters,
            mention_purges=self.mention_purges,
            sieves_list=self.sieves,
            meta_info=self.meta_info
        )
        # Prepare Feature extractor
        self.feature_extractor = FeatureExtractor(
            graph_builder=self.graph_builder,
            mention_features=self.mention_features,
            meta_info=self.meta_info
        )

        self.feature_extractor.load_extractors()

        self.meta = defaultdict(Counter)

    def build_graph(self, document):
        """Build a graph form external parser.

        :param document: The document to generate the graph.
        """
        self.graph_builder.process_document(document=document)
        sentences_parsed = self.graph_builder.get_sentences()

        sentence_roots = [self.graph_builder.process_sentence(
                sentence=sentence,
                sentence_namespace="text@{0}".format(index),
                root_index=index)
                for index, sentence in enumerate(sentences_parsed)
                ]
        for sentence_root in sentence_roots:
            self.coreference_processor.process_sentence(sentence=sentence_root)

    def process_graph(self):
        """ Prepare the graph for output.
        """
        self.meta[self.graph_builder.doc_type] = self.graph_builder.get_doc_type()
        self.meta["sentences"] = []
        self.meta["features"] = {
            'counters': defaultdict(Counter),
            'mentions': defaultdict(dict)}
        for index, sentence in enumerate(self.coreference_processor.mentions_textual_order):
            self.logger.debug("Featuring Sentence %d", index)
            sentence_mentions = []
            self.meta["sentences"].append(sentence_mentions)
            for mention in sentence:
                # Store mentions id in the meta
                sentence_mentions.append(mention[ID])
                self.feature_extractor.characterize_mention(mention)
        # Resolve the coreference
        self.logger.debug("Resolve Coreference...")
        self.coreference_processor.resolve_text()

    def show_graph(self):
        """Show the graph in screen"""
        self.graph_builder.show_graph()

    def store(self, stream, config):
        """ Store the graph into a document with the format provided by the
        config.
        :param stream: The stream where the document is going to be write
        :param config: The config namespace that contains all the options needed
            for write the document.
        """
        from output import writers

        kwargs = {}
        for option in config.writer_options:
            key, value = option.split()
            kwargs[key] = value

        writer = writers[config.writer](stream=stream, document_id=config.document_id)
        writer.store(
            graph_builder=self.graph_builder,
            encoding=config.encoding,
            language=config.language,
            coreference_processor=self.coreference_processor,
            start_time=config.start_time,
            end_time=config.end_time,
            **kwargs
        )

    def process_text(self, document):
        """ Generate a graph with all linguistic info from de document, resolve
        the coreference and output the results.

        :param document:
        """
        self.reset_graph()
        self.build_graph(document)
        self.process_graph()

    def get_meta(self, ):
        """ Get meta info"""
        self.meta.update(self.coreference_processor.get_meta())
        # Fill the features of unprocessed mentions
        for entity in self.coreference_processor.extractor._mentions:
            if entity[ID] not in self.feature_extractor.meta['mentions']:
                self.feature_extractor.characterize_mention(entity)
        self.meta["features"] = self.feature_extractor.get_meta()
        return self.meta
