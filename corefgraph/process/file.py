#!/usr/bin/python
# coding=utf-8
"""
Implements Stanford Multi-Sieve Pass Coreference System as their 2013
Computational Linguistics paper

"""
import json
import logging.config

import sys
import codecs
import time
import configargparse as argparse
from corefgraph import properties

__author__ = 'Josu Bermúdez <josu.bermudez@deusto.es>, ' \
             'Rodrigo Agerri <rodrigo.agerri@ehu.es>'


logger = logging.getLogger(__name__)


def process(config, text, parse_tree, speakers_list, output):
    """Process a document through the corefgraph system.info

    :param config: The parameters used to tune the resolution and output format.
    :param text: The KAF file of the document
    :param parse_tree: A list o treebank parse trees
    :param speakers_list: A list of the speaker per token.
    :param output: The stream where the output is write.
    """
    # Start of processing

    # Setting the system
    # This is used to spread the language all over the module
    logger.info("Setting language to %s", config.language)
    properties.set_lang(config.language, config.encoding)
    from corefgraph import Corefgraph

    # End of voodoo

    meta_parameters(config)
    config.start_time = time.gmtime()
    processor = Corefgraph(
        verbose=config.verbose, reader=config.reader,
        secure_tree=config.secure_tree, lang=config.language,
        sieves=config.sieves,
        extractor_options=config.extractor_options,
        mention_extractor=config.mention_extractor,
        candidate_extractor=config.candidate_extractor,
        mention_catchers=config.mention_catchers,
        mention_filters=config.mention_filters,
        mention_purges=config.mention_purges,
        mention_features=config.mention_features,
        meta_info=config.meta
    )

    document = (text, parse_tree, speakers_list)
    # Process the coreference of the document
    processor.process_text(document)
    # End of processing
    config.end_time = time.gmtime()
    # Write the result
    processor.store(stream=output, config=config)
    if config.meta:
        return processor.get_meta()
    else:
        return None


def meta_parameters(config):
    """ Process the parameters that changes the parameters.
    :param config:
    :return: Nothing
    """
    # Sieves
    if "NO" in config.sieves or "no" in config.sieves or\
            "False" in config.sieves or "false" in config.sieves or "FALSE" in config.sieves:
        logger.info("Sieves: NO")
        config.sieves = []
    elif "All" in config.sieves or "all" in config.sieves:
        logger.info("Sieves: ALL")
        import corefgraph.multisieve.sieves as sieves
        config.sieves = sieves.all_sieves
    elif len(config.sieves) == 0:
        logger.info("Sieves: Default")
        config.sieves = [
            'SPM', 'RSM', 'ESM', 'PCM', 'SHMA', 'SHMB', 'SHMC', 'SHMD', 'RHM', 'PNM']
    logger.info("Sieves: %s ", config.sieves)

    # purges
    if "all" in config.mention_purges or "ALL" in config.mention_purges:
        logger.debug("Purges: ALL")
        import corefgraph.multisieve.purges as purges
        config.mention_purges = purges.purges_by_name.keys()
    elif "no" in config.mention_purges or "NO" in config.mention_purges or \
            "false" in config.mention_purges or "False" in config.mention_purges or "FALSE" in config.mention_purges:
        logger.debug("Purges: NO")
        config.mention_purges = []
    elif len(config.mention_purges) == 0:
        logger.debug("Purges: DEFAULT")
        config.mention_purges = [
            'Appositive', 'Singleton', 'RelativePronoun', 'PredicativeNominative']
    logger.info("Purges: %s", config.mention_purges)

    # Filters
    if "all" in config.mention_filters or "ALL" in config.mention_filters:
        logger.info("Filters: ALL")
        import corefgraph.multisieve.filters as filters
        config.mention_filters = filters.filters_by_name.keys()
    elif "no" in config.mention_filters or "NO" in config.mention_filters or \
            "False" in config.mention_filters or "FALSE" in config.mention_filters \
            or "false" in config.mention_filters:
        logger.info("Filters: NO")
        config.mention_filters = []
    elif len(config.mention_filters) == 0:
        logger.debug("Filters: DEFAULT")
        config.mention_filters = [
            'QuantityFilter', 'PleonasticFilter', 'DemonymFilter', 'InterjectionFilter',
            'PartitiveFilter', 'BareNPFilter', 'QuantifierFilter', 'InvalidWordFilter',
            'NonWordFilter', 'ConllSameHeadFilter']
    logger.info("Filters: %s", config.mention_filters)

    # Catchers
    if "all" in config.mention_catchers or "ALL" in config.mention_catchers:
        logger.info("Catchers: ALL")
        import corefgraph.multisieve.catchers as catchers
        config.mention_catchers = catchers.catchers_by_name.keys()
    elif "no" in config.mention_catchers or "NO" in config.mention_catchers:
        logger.info("Catchers: NO")
        config.mention_catchers = []
    elif len(config.mention_catchers) == 0:
        logger.debug("Catchers: DEFAULT")
        config.mention_catchers = ['NamedEntitiesCatcher', 'PronounCatcher', 'EnumerableCatcher', 'ConstituentCatcher']
    logger.info("Catchers: %s", config.mention_catchers)

    # Features
    if "all" in config.mention_features or "ALL" in config.mention_features:
        logger.info("Features: ALL")
        import corefgraph.multisieve.features as features
        config.mention_features = features.all_annotators
    elif "no" in config.mention_features or "NO" in config.mention_features or \
            "false " in config.mention_features or "FALSE" in config.mention_features or \
            "False" in config.mention_features:
        logger.info("Features: NO")
        config.mention_features = []
    elif len(config.mention_features) == 0:
        logger.debug("Features: DEFAULT")
        config.mention_features = [
            'ner', 'type', 'construction', 'number', 'gender', 'animacy', 'speaker',
            'generic', 'person', 'dependency', 'demonym']
    logger.info("Features: %s", config.mention_features)


def generate_parser():
    """ Parse command line arguments and get values needed to process a file."""
    logger.debug("Creating parser")
    parser = argparse.ArgumentParser(description="Process an annotated  text file \
        with corefgraph")
    parser.add_argument(
        '--config', '-c', is_config_file=True,
        help='config file path')
    parser.add_argument(
        '--verbose', '-v', dest='verbose', action='store_true',
        help="Add more output to the system")
    parser.add_argument(
        '--file', '-f', dest='input', action='store',
        default=None,
        help='File to process. If not specified standard input is used.')
    parser.add_argument(
        '--document_id', "-ID", dest='document_id', action='store',
        default=None,
        help='The id used to identify the document used in writing output process.')
    parser.add_argument(
        '--treebank', '-t', dest='parse_tree', action='store',
        default=None,
        help="An additional file with the document syntactic parse trees if base one don't have it")
    parser.add_argument(
        '--speakers', '-s', dest='speakers', action='store',
        default=None,
        help='an additional file with the speakers of the tokens.')
    parser.add_argument(
        '--language', '-l', dest='language', action='store',
        default="en_conll",
        help='The language-annotation to use')
    parser.add_argument(
        '--unsafe_tree', dest='secure_tree', action='store_false',
        help="Use slower method to process NAF trees in case of wrong ordered edges list.")
    parser.add_argument(
        '--reader', '-r', dest='reader', action='store',
        default="NAF",
        help='The input file reader to use. Default NAF.')
    parser.add_argument(
        '--writer', '-w', dest='writer', action='store',
        default="NAF",
        help='The output file writer to use. Default NAF.')
    parser.add_argument(
        '--encoding', dest='encoding', action='store',
        default="utf-8",
        help='Set File encoding.')
    parser.add_argument(
        '--sieves', dest='sieves', action="append",
        default=[],
        help="The plain name of the sieves that must be used.")
    parser.add_argument(
        "--mention_extractor", dest="mention_extractor",
        default="DFE",
        help="The extractor that collect mentions from the text")
    parser.add_argument(
        "--candidate_extractor", dest="candidate_extractor",
        default="BFE",
        help="The extractor that collect candidates from the text")
    parser.add_argument(
        '--mention_catchers', dest='mention_catchers',  action="append",
        default=[],
        help="The catchers used during mention extraction.")
    parser.add_argument(
        '--mention_purges', dest='mention_purges', action="append",
        default=[],
        help="The catchers used during mention purges.")
    parser.add_argument(
        '--mention_filters', dest='mention_filters', action="append",
        default=[],
        help="The filters used during mention extraction.")
    parser.add_argument(
        '--mention_features', dest='mention_features', action="append",
        default=[],
        help="The annotators that describe the mention.")
    parser.add_argument(
        '--extractor_options', dest='extractor_options', action="append",
        default=[],
        help="The options passed  during mention extraction.")
    parser.add_argument(
        '--writer_options', dest='writer_options', action="append",
        default=[],
        help="The options passed to writer module.")
    parser.add_argument(
        '--meta_json', dest='meta', action="store_true",
        help="Generate meta info during process.")
    return parser


def main(config_files=False):
    """ Invoked when the module is uses directly from as CLI tool.
    Uses the argument parser from def generate_parser().

    :return: NOTHING
    """
    parser = generate_parser()
    if config_files:
        parser._default_config_files = config_files
    arguments = parser.parse_args()

    if arguments.input:
        input_text = codecs.open(
            filename=arguments.input, mode="r",
            encoding=arguments.encoding).read()
    else:
        logger.info("kaf from standard input")
        input_text = sys.stdin.read()
    if arguments.parse_tree:
        parse_tree = codecs.open(
            filename=arguments.parse_tree, mode="r",
            encoding=arguments.encoding).read()
    else:
        parse_tree = None
    if arguments.speakers:
        logger.info("No speaker annotation")
        speakers_list = codecs.open(
            filename=arguments.speakers, mode="r",
            encoding=arguments.encoding).read()
    else:
        speakers_list = None

    info = process(config=arguments, text=input_text, parse_tree=parse_tree,
                   speakers_list=speakers_list, output=sys.stdout)
    if info:
        with codecs.open("info.json", "w") as output_file:
            json.dump(info, output_file)


if __name__ == "__main__":
    main()
