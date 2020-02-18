# coding=utf-8
""" The main module of the Corefgraph system. See process.file o process.corpus for CLI usage.

"""

import logging
from collections import Counter, defaultdict

from corefgraph.constants import ID
from corefgraph.graph.nafbuilder import NafAndTreeGraphBuilder
from corefgraph.multisieve import features
from corefgraph.multisieve.core import CoreferenceProcessor
from corefgraph.output import writers


__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


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
            mention_features=self.mention_features)

        self.feature_extractor.load_extractors()

        self.meta = defaultdict(Counter)

    def build_graph(self, document):
        """Build a graph form external parser.

        :param document: The document to generate the graph.
        """
        self.graph_builder.process_document(document=document)
        sentences_parsed = self.graph_builder.get_sentences()

        # for index, sentence in enumerate(sentences_parsed):
        #     self.logger.debug("Loading Sentence %d", index)
        #     # syntax graph construction
        #     sentence_root = self.graph_builder.process_sentence(
        #         sentence=sentence,
        #         sentence_namespace="text@{0}".format(index),
        #         root_index=index)
        #     # Generate Coreference Candidatures for the sentence
        #
        #     self.coreference_processor.process_sentence(sentence=sentence_root)
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

    def get_meta(self, ):
        """ Get meta info"""
        self.meta.update(self.coreference_processor.get_meta())
        self.meta["features"] = self.feature_extractor.get_meta()
        return self.meta

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


class FeatureExtractor:

    def __init__(self, graph_builder, mention_features):
        self.graph_builder = graph_builder
        self.mention_features = mention_features
        self.meta = {
            'counters': defaultdict(Counter),
            'mentions': defaultdict(dict)}

    def load_extractors(self):
        self.feature_extractors = [
            features.annotators_by_name[annotator](self.graph_builder)
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

                self.meta['mentions'][mention[ID]][feature] = feature_value
                try:
                    self.meta['counters'][feature][feature_value] += 1
                except TypeError:
                    self.meta['counters'][feature]["NO_HASH"] += 1

    def get_meta(self):
        return self.meta
