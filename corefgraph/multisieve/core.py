# coding=utf-8
""" This module contains the primary infrastructure and the entry point class
for usage the module.

"""
from corefgraph.multisieve.extractor import SentenceCandidateExtractor
from corefgraph.multisieve.sieves import sieves_by_name
from corefgraph.constants import SPAN, ID, FORM
from corefgraph.multisieve.purges import purges_by_name
from logging import getLogger


__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '14-11-2012'


class MultiSieveProcessor:
    """A coreference detector based on the lee et all. 2013 Multisieve system
    of Stanford University.
    """
    logger = getLogger(__name__)

    def __init__(self, sieves_list, meta_info):
        self.links = []
        self.meta_info = meta_info
        self.logger.info("Sieves: %s", sieves_list)
        self.sieves_names = sieves_list
        # dynamically load the sieves
        self.sieves = self.load_sieves(sieves_list)

    def get_meta(self):
        # Create the meta structure
        meta = {
            "names": self.sieves_names
        }
        # Retrieve Meta info for each sieve
        for sieve in self.sieves:
            meta[sieve.short_name] = sieve.get_meta()

        return meta

    def process(self, graph_builder, mentions_text_order, mentions_candidate_order):
        """ Process a candidate cluster list thought the sieves using the output
         of the each sieve as input of the next.
        """
        sieve_output = {}
        # create the base entity inside each mention in each sentence
        for sentence in mentions_text_order:
            for mention in sentence:
                # mention is identified for first mention in its span
                entity = (mention[SPAN], [mention, ])
                # Store the entity reference in the mention
                mention["entity"] = entity
                # backup output in case of run with no sieves
                sieve_output[mention[SPAN]] = [mention, ]
        # Pass each sieve through all mentions
        for sieve in self.sieves:
            # Store sieve output for output, only last one is used
            sieve_output = sieve.resolve(graph_builder=graph_builder, mentions_order=mentions_text_order,
                                         candidates_order=mentions_candidate_order)
        # plain the output
        return [sieve_output[key] for key in sorted(sieve_output.keys())]

    def load_sieves(self, sieves_list):
        """ Load the sieves from a list of string. The id of the sieves to load
         is its short name.

        :param sieves_list: A list of string containing the short name of the
            strings to load.

        :return: A list of ready to use sieve objects.
        """
        # Load in order each sieve, initialize it and return a list with all sieves
        return [
            sieves_by_name[sieve_class](meta_info=self.meta_info)
            for sieve_class in sieves_list]


class CoreferenceProcessor:
    """ Detect chunks or word of a graph as coreferent with each others.
    """

    logger = getLogger(__name__)

    local_mentions_constant = "LOCAL_MENTIONS"
    soft_purge_constant = "SOFT_PURGES"
    soft_filter_constant = "SOFT_FILTERS"
    gold_boundaries_constant = "GOLD_BOUNDARIES"

    def __init__(self,
                 graph_builder,
                 extractor_options,
                 sieves_list,
                 mention_extractor,
                 candidate_extractor,
                 mention_catchers,
                 mention_filters,
                 mention_purges,
                 meta_info
                 ):

        self.graph_builder = graph_builder
        self.meta_info = meta_info
        self.purges_names = mention_purges
        self.purges = self.load_purges(mention_purges)

        if self.gold_boundaries_constant in extractor_options:
            self.logger.info("Gold boundaries")
            self.gold_boundaries = True
        else:
            self.gold_boundaries = False

        if self.soft_filter_constant in extractor_options:
            self.logger.info("Filters in soft mode")
            self.soft_filters = True
        else:
            self.soft_filters = False

        if self.soft_purge_constant in extractor_options:
            self.logger.info("Purges in soft mode")
            self.soft_purges = True
        else:
            self.soft_purges = False

        self.extractor = SentenceCandidateExtractor(
            graph_builder=self.graph_builder,
            mention_extractor=mention_extractor,
            candidate_extractor=candidate_extractor,
            mention_catchers=mention_catchers,
            mention_filters=mention_filters,
            soft_filter=self.soft_filters,
            gold_boundaries=self.gold_boundaries,
            meta_info=self.meta_info
        )
        self.multi_sieve = MultiSieveProcessor(
            sieves_list=sieves_list,
            meta_info=self.meta_info
        )
        self.mentions_textual_order = []
        self.mentions_candidate_order = []

        self.coreference_proposal = []
        self.coreference_gold = []

        # meta info structures
        self.wrong_purged = {}
        self.lost_purged = {}
        self.ok_purged = {}
        self.not_purged = {}
        self.entities_purged = []

    def get_meta(self):
        """  Recover the statistics obtained while processing the graph.

        :return: A struck of dictionaries.
        """

        return {"sieves": self.multi_sieve.get_meta(),
                "extractor": self.extractor.get_meta(),
                "purges":  {
                    "names": self.purges_names,
                    "WRONG": self.wrong_purged,
                    "LOST": self.lost_purged,
                    "OK": self.ok_purged,
                    "NO": self.not_purged
                }}

    def load_purges(self, mention_purges):
        """ Load the purges based on short-names list.

        :param mention_purges: List of short-names of purges.
        :return: a list of purge objects.
        """
        self.logger.info("Purges: %s", mention_purges)
        return [purges_by_name[purge_name](
                self.graph_builder, self)
                for purge_name in mention_purges]

    def process_sentence(self, sentence):
        """ Fetch the sentence mentions and generate candidates for they.

        :param sentence: The sentence syntactic tree root node.
        """
        # Extract the mentions
        mentions_candidate_order, mentions_text_order = \
            self.extractor.process_sentence(sentence=sentence)
        # Add new clusters and candidates
        self.mentions_candidate_order.append(mentions_candidate_order)
        self.mentions_textual_order.append(mentions_text_order)

    def resolve_text(self):
        """ For a candidate marked graph, resolve the coreference.
        """

        # self.logger.info("Processing Coreference (%s candidates)", len(self.mentions))
        # Keep track the index of the entities
        indexed_clusters = 0
        # Resolve the coreference
        coreference_proposal = self.multi_sieve.process(
            graph_builder=self.graph_builder,
            mentions_text_order=self.mentions_textual_order,
            mentions_candidate_order=self.mentions_candidate_order)
        # Get the gold mentions spans
        gold_mentions = [m[SPAN] for m in self.graph_builder.get_all_gold_mentions()]

        indexed_clusters = self.post_process(coreference_proposal, gold_mentions, indexed_clusters)

        self.logger.info("Indexed clusters: %d", indexed_clusters)

    def purge_mention(self, unfiltered_mention):
        for purge in self.purges:
            # Pass mention for each purge
            if purge.purge_mention(unfiltered_mention):
                self.logger.debug("purged mention(%s): %s",
                                  purge.short_name, unfiltered_mention[FORM])
                # Store the meta info
                return True, purge.short_name
        return False, "NONE"

    def purge_entity(self, mentions):
        for purge in self.purges:
            if purge.purge_entity(mentions):
                self.entities_purged.append((",".join((mention[ID] for mention in mentions)), purge.short_name))
                self.logger.debug("Purged entity: %s", purge.short_name)
                return True, purge.short_name
        return False, "NONE"

    def post_process(self, coreference_proposal, gold_mentions, indexed_clusters):
        self.logger.info("POST-Processing Coreference (%s clusters)", len(coreference_proposal))
        # Purge the coreference clusters add the acceptable ones to the graph
        filtered_mentions = []
        for index, entity in enumerate(coreference_proposal):
            clean_mentions = []
            # Filter the mentions of the entity
            for unfiltered_mention in entity:
                # Purge the mention
                purged, purge = self.purge_mention(unfiltered_mention)
                if purged:
                    if self.soft_purges:
                        # If soft purges are activated, not ignore the mention create a new entity for it
                        coreference_proposal.append([unfiltered_mention])
                    else:
                        filtered_mentions.append((unfiltered_mention, purge))
                else:
                    # If no purge breaks the cycle then the mention is valid
                    clean_mentions.append(unfiltered_mention)

            # Skip empty entities
            if len(clean_mentions) == 0:
                continue

            # Check the full entity Against the purges
            purged, purge = self.purge_entity(clean_mentions)
            if purged:
                filtered_mentions.extend([(mention, purge) for mention in clean_mentions])
            else:
                # Add the entity tho the response
                self.graph_builder.add_coref_entity(
                    entity_id="EN{0}".format(index), mentions=clean_mentions)
                # Increment the entity index
                indexed_clusters += 1
                # Store the meta
                if self.meta_info:
                    for mention in clean_mentions:
                        span_str = str(mention[SPAN])
                        if mention[SPAN] in gold_mentions:
                            # A wrong purge false positive
                            self.logger.debug("Wrong purged(Entity purge)")
                            self.not_purged[span_str] = [mention[ID], "NONE"]
                        else:
                            # A correct purge True positive
                            self.lost_purged[span_str] = [mention[ID], "NONE"]

        # Store meta for purged mentions
        if self.meta_info:
            for filtered_mention, purge in filtered_mentions:
                span_str = str(filtered_mention[SPAN])

                if filtered_mention[SPAN] in gold_mentions:
                    # A wrong purge false positive
                    self.logger.debug("Wrong purged(Entity purge)")
                    self.wrong_purged[span_str] = [filtered_mention[ID], purge, ]
                else:
                    # A correct purge True positive
                    self.ok_purged[span_str] = [filtered_mention[ID], purge, ]
        # Not a valid entity skip the adding stage
        return indexed_clusters
