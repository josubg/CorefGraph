# coding=utf-8
""" Main module of the system
"""
from collections import defaultdict
from logging import getLogger

from corefgraph.constants import SPAN, FORM, ID

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '14-11-2012'


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

        from corefgraph.multisieve.extractors import SentenceCandidateExtractor
        from corefgraph.multisieve.sieves import MultiSieveProcessor

        self.graph_builder = graph_builder
        self.meta_info = meta_info
        self.purges_names = mention_purges
        self.purges = self.load_purges(mention_purges)

        self.gold_boundaries = self.gold_boundaries_constant in extractor_options
        if self.gold_boundaries:
            self.logger.info("Gold boundaries")

        self.soft_filters = self.soft_filter_constant in extractor_options
        if self.soft_filters:
            self.logger.info("Filters in soft mode")

        self.soft_purges = self.soft_purge_constant in extractor_options
        if self.soft_purges:
            self.logger.info("Purges in soft mode")

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

        self.prepare_meta()

    def load_purges(self, mention_purges):
        """ Load the purges based on short-names list.

        :param mention_purges: List of short-names of purges.
        :return: a list of purge objects.
        """
        from corefgraph.multisieve.purges import purges_by_name

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
        # Get the gold mentions spans to store wrong purges in metadata
        gold_mentions = [m[SPAN] for m in self.graph_builder.get_all_gold_mentions()]
        # Purge the system output to match annotation guidelines  and clean useful but bo valid mentions
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
        return False, "unpurged"

    def purge_entity(self, mentions):
        for purge in self.purges:
            if purge.purge_entity(mentions):
                return True, purge.short_name
        return False, "unpurged"

    def post_process(self, coreference_proposal, gold_mentions, indexed_clusters):
        self.logger.info("POST-Processing Coreference (%s clusters)", len(coreference_proposal))
        # Purge the coreference clusters add the acceptable ones to the graph
        purged_mentions = []
        for index, entity in enumerate(coreference_proposal):
            clean_mentions = []
            # Filter the mentions of the entity
            for unfiltered_mention in entity:
                # Purge the mention
                purged, purge = self.purge_mention(unfiltered_mention)
                if purged:
                    if self.soft_purges:
                        # If soft purges are activated, not ignore the mention create a new entity for it
                        if [unfiltered_mention] not in coreference_proposal:
                            coreference_proposal.append([unfiltered_mention])
                    else:
                        purged_mentions.append((unfiltered_mention, purge))
                else:
                    # If no purge breaks the cycle then the mention is valid
                    clean_mentions.append(unfiltered_mention)

            # Skip empty entities
            if len(clean_mentions) == 0:
                continue

            # Check the full entity Against the purges
            purged, purge = self.purge_entity(clean_mentions)
            if purged:
                purged_mentions.extend([(mention, purge) for mention in clean_mentions])
            else:
                # Add the entity to the response
                self.graph_builder.add_coref_entity(node_id="EN{0}".format(index), mentions=clean_mentions)
                # Increment the entity index
                indexed_clusters += 1
                # Store the meta
                if self.meta_info:
                    for mention in clean_mentions:
                        span_str = str(mention[SPAN])
                        if mention[SPAN] in gold_mentions:
                            # A wrong purge false positive
                            self.logger.debug("Wrong purged(Entity purge)")
                            self.not_purged[span_str] = mention
                        else:
                            # A correct purge True positive
                            self.lost_purged[span_str] = mention

        # Store meta for purged mentions
        if self.meta_info:
            for purged_mention, purge in purged_mentions:
                span_str = str(purged_mention[SPAN])
                if purged_mention[SPAN] in gold_mentions:
                    # A wrong purge false positive
                    self.logger.debug("Wrong purged(Entity purge)")
                    self.wrong_purged[purge][span_str] = purged_mention
                else:
                    # A correct purge True positive
                    self.ok_purged[purge][span_str] = purged_mention

        # Not a valid entity skip the adding stage
        return indexed_clusters

    def prepare_meta(self):
        # meta info structures
        self.ok_purged = defaultdict(dict)
        self.wrong_purged = defaultdict(dict)
        self.lost_purged = {}
        self.not_purged = {}

    def get_meta(self):
        """  Recover the statistics obtained while processing the graph.

        :return: A struck of dictionaries.
        """
        meta = {
            "sieves": self.multi_sieve.get_meta(),
            "purges":  {
                "OK": {
                    name: {span: mention[ID] for (span, mention) in purge.items()} for name, purge in self.ok_purged.items()},
                "WRONG": {
                    name: {span: mention[ID] for (span, mention) in purge.items()} for name, purge in self.wrong_purged.items()},
                "LOST": {
                    "all": {span: mention[ID] for (span, mention) in self.lost_purged.items()}},
                "NO": {
                    span: mention[ID] for (span, mention) in self.not_purged.items()}
            }
        }
        meta.update(self.extractor.get_meta())
        return meta
