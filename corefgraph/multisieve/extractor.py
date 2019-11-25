# coding=utf-8
""" Module that contains all necessary stuff to detect the mentions present in a
 sentence and supply a ordered list of candidates for each mention.

"""


from logging import getLogger
from collections import defaultdict

from corefgraph.resources.tagset import constituent_tags, ner_tags
from corefgraph.constants import SPAN, NER, FORM, ID, POS, TAG, QUOTED, UTTERANCE, CONSTITUENT, CONSTITUENT_ALIGN, \
    HEAD_OF_NER, GOLD
from filters import filters_by_name
from catchers import catchers_by_name
from corefgraph.resources.rules import rules
from corefgraph.multisieve.extractors import extractors_by_name

__author__ = 'Josu Bermúdez <josu.bermudez@deusto.es>'


class SentenceCandidateExtractor:
    """ Extract all the mentions of a text. The text if analysed sentence by
    sentence."""

    logger = getLogger(__name__)

    def __init__(
            self, graph_builder,
            mention_catchers,
            mention_filters,
            mention_extractor, candidate_extractor,
            soft_filter,gold_boundaries, meta_info):

        # meta info
        self._mentions = dict()

        self._lost_filtered = dict()
        self._ok_filtered = dict()
        self._wrong_filtered = dict()
        self._no_filtered = dict()

        self._lost_caught = dict()
        self._ok_caught = dict()
        self._wrong_caught = dict()
        self._no_caught = list()

        self.candidates = []

        self.meta_info = meta_info

        # Graph management
        self.graph_builder = graph_builder

        # extractors
        self.candidate_extractor = self._load_extractor(graph_builder, candidate_extractor)
        self.mention_extractor = self._load_extractor(graph_builder, mention_extractor)

        # Catchers
        self._mention_catchers_names = mention_catchers
        self.catchers = self._load_catchers(
            graph_builder, mention_catchers)

        # Filters
        self._mention_filters_names = mention_filters
        self.filters = self._load_filters(
            graph_builder, mention_filters)
        self.soft_filter = soft_filter
        self.gold_boundaries =gold_boundaries

        # List used to keep mention during the tree traversal
        self._sentence_mentions_bft_order = []
        self._sentence_mentions_dft_order = []

        # The spans are used to avoid duplicate mentions and mention inside NE
        self._sentence_candidates_span = []
        self._sentence_candidates_ids = []

        # Gold mention storage structures
        self.gold_entities = {}
        #self.gold_mentions_by_span = {}
        self.gold_entities_spans = []
        self.sentence_gold_mentions_by_constituent = defaultdict(list)

        # Named entities storage structures
        self.named_entities = []
        self.named_entities_span = []
        self.sentence_named_entities_by_constituent = defaultdict(list)

    # Meta info
    def get_meta(self):
        """ Recollect the meta info and store it  in json compatible values.

        :return A json compatible structure of info.
        """
        return {
            "mentions": self._mentions,
            "catchers": {
                "names": self._mention_catchers_names,
                "OK": self._ok_caught,
                "WRONG": self._wrong_caught,
                "LOST": self._lost_caught,
                # "NO": self._no_caught,
                },
            "filters": {
                "names": self._mention_filters_names,
                "OK": self._ok_filtered,
                "WRONG": self._wrong_filtered,
                "LOST": self._lost_filtered,
                "NO": self._no_filtered,
                "SOFT_FILTER": self.soft_filter,
            },
        }

    # Dynamic load
    def _load_extractor(self, graph_builder, extractor_name):
        """ Load the extractor used during mention retrieving.

        :param graph_builder: The graph Builder
        :param extractor_name: The extractor name to load.

        :return: the list of filter instances.
        """

        self.logger.info("Extractors: %s", extractor_name)
        # Find each filter class by its short name and create one instance
        return extractors_by_name[extractor_name](graph_builder)

    def _load_filters(self, graph_builder, mention_filters):
        """ Load the filters used during mention retrieving.

        :param graph_builder: The graph Builder
        :param mention_filters: The list of filters to load(their short name).

        :return: the list of filter instances.
        """

        self.logger.info("Filters: %s", mention_filters)
        # Find each filter class by its short name and create one instance
        return [filters_by_name[filter_name](
                graph_builder, self)
                for filter_name in mention_filters]

    def _load_catchers(self, graph_builder, mention_catchers):
        """ Load the catchers used during mention retrieving.

        :param graph_builder: The graph Builder
        :param mention_catchers: The list of filters to load(their short name).

        :return: the list of catchers instances.
        """
        self.logger.info("Catchers: %s", mention_catchers)
        # Find each catcher class by its short name and create one instance
        return [catchers_by_name[catcher_name](
                graph_builder, self)
                for catcher_name in mention_catchers]

    # Mention extracting
    def _check_node(self, mention_candidate, prev_mentions):
        return mention_candidate[ID] in self._sentence_candidates_ids

    def _catch(self, mention_candidate):
        span_str = str(mention_candidate[SPAN])
        for catcher in self.catchers:
            if catcher.catch(mention_candidate):
                # Candidate is accepted
                if self.meta_info:
                    # Remove the candidate form the lost candidate list (a upper representation of the span
                    if span_str in self._lost_caught:
                        del self._lost_caught[span_str]

                    self._mention_meta(mention_candidate)
                    #  check if is gold one
                    if mention_candidate[SPAN] in self.gold_entities_spans:
                        # Candidate is a gold one. Good catching(True positive)
                        self._ok_caught[span_str] = [mention_candidate[ID], catcher.short_name]
                    else:
                        # Candidate is not a gold one. Bad catching(False positive)
                        self._wrong_caught[span_str] = [mention_candidate[ID], catcher.short_name]

                # Is a valid candidate
                # The node is a valid candidate
                self.logger.debug(
                    "Mention accepted: -%s- -%s- %s",
                    mention_candidate[FORM], mention_candidate[ID],
                    mention_candidate.get(POS, None) or mention_candidate.get(TAG))
                # Check if filter the candidate
                return True
        if self.meta_info:
            # Check if is gold one
            if mention_candidate[SPAN] in self.gold_entities_spans:
                # It is a gold one Bad catching (a bottom representation of the span may be checked later, but
                # the lost is annotated)
                self._lost_caught[span_str] = [mention_candidate[ID], "NONE"]
                self._mention_meta(mention_candidate)
            # Correct false cases aren't annotated because it will be overwhelming
        return False

    def _validate_node(self, mention_candidate, prev_mentions):
        """Determine if a node is a valid candidate with every loaded catcher.

        :param mention_candidate: The candidate Node(constituent, word o NE) to be
            validates as mention.

        :return True if the span is a valid candidate or False otherwise.
        """
        # If the span is already in the accepted candidates Skip catching the span.
        if mention_candidate[SPAN] in self._sentence_candidates_span:
            return False

        # Check candidate with each catcher
        if self._catch(mention_candidate):
            if self._filter_candidate(mention_candidate=mention_candidate, prev_mentions=prev_mentions):
                # Candidate is not accepted Filtered
                return False
            else:
                # Candidate is a valid mention
                self.add_mention(mention=mention_candidate)
                return True
        # Candidate is not accepted Not catch
        return False

    def _filter_candidate(self, mention_candidate, prev_mentions):
        """ Check if the mention candidate have to be filtered with all loaded filters.

        :param mention_candidate: A candidate mention(constituent, word o NE).

        :return True if it have to be filtered, false otherwise.
        """
        span_str = str(mention_candidate[SPAN])
        # Pass candidate for each filter
        for mention_filter in self.filters:
            # Check candidate
            if mention_filter.filter(mention_candidate, prev_mentions):
                # The candidate is going to be filtered
                if self.meta_info:
                    # Check if is a gold one.
                    if mention_candidate[SPAN] in self.gold_entities_spans:
                        # candidate is filters and it is in gold response (Bad filtering: False positive)
                        self._wrong_filtered[span_str] = [mention_candidate[ID], mention_filter.short_name]
                    else:
                        # candidate is filters and it is not gold response (God filtering: True positive)
                        self._ok_filtered[span_str] = [mention_candidate[ID], mention_filter.short_name]
                # If soft filter is activated the mention is only marked as invalid
                if self.soft_filter:
                    # Not filter but mark as invalid.
                    mention_candidate["invalid"] = True
                    return False
                # candidate is filtered
                return True
        # Candidate is not going to be filtered
        if self.meta_info:
            # Check if is gold one
            if mention_candidate[SPAN] not in self.gold_entities_spans:
                # Candidate is not filtered and is not in Gold response (Bad filtering: False Negative)
                self._lost_filtered[span_str] = [mention_candidate[ID], "NONE"]
            else:
                # Candidate is not filtered and is not in Gold response (Good Filtering: True positive)
                self._no_filtered[span_str] = [mention_candidate[ID], "NONE"]
        # if mention_candidate[SPAN] in self.gold_entities_spans:
        #     mention_candidate["GOLD"] = self.gold_mentions_by_span[mention_candidate[SPAN]]
        # # candidate is not filtered
        return False

    def add_mention(self, mention):
        """ Add mention to the sentence mention cluster. Also assign the ner type  of the mention.

        :param mention: A valid and checked mention mention
        """
        self._sentence_candidates_ids.append(mention[ID])
        self._sentence_candidates_span.append(mention[SPAN])

    # Allocation of tree externals
    def _get_span_constituent(self, sentence, span):
        """ Try to fit a span (a group of sequential words) into a existing
        constituent.

        :param sentence: The sentence where the word must be allocated.
        :param span: The list of word that must be allocated.
        """
        nodes = self.graph_builder.get_syntactic_children_sorted(sentence)
        while nodes:
            node = nodes.pop()
            node_span = node[SPAN]
            # No root
            if not constituent_tags.root(node.get(TAG)) and\
                    node_span == span:
                return node
            children = self.graph_builder.get_syntactic_children_sorted(node)
            if not (node_span[0] > span[0] or node_span[-1] < span[-1]):
                nodes.extend(children)
        return None

    def _get_plausible_head_word(self, words):
        """ Get a Head word for the NE that preserves the head coherence.

        Find the words of the NE that are heads. If more than one are head use
        the head assign rules( NP cases) with
        the head word to select the head. If no head is contained in the bag of
        word use every word instead of head words.

        #  head word assignment preferences for NP cases:
        # "NN", "NNP", "NNPS", "NNS", "NX", "JJR", "POS"

        :param words: A list of words
        :return A word
        """
        head = rules.get_plausible_head(words)
        if head:
            self.logger.debug("PLAUSIBLE HEAD: Matched head word")
            return head
        self.logger.debug("PLAUSIBLE HEAD: last word")
        head_word = words[-1]
        return head_word

    def _get_plausible_constituent(self, head, span):
        """ Get the highest NP that has the same head.

        Get the constituent that complains these restriction:
            + Have the same terminal head.
            + Is NP.
            + Is the highest NP of the first chain of NPs.

        If no valid NP is found uses the constituent of the head.

        Source:
        StanfordCoreNLP::MentionExtractor.Java::Class:MentionExtractor:Arrage

        :param head: the terminal head that must be the head of the constituent.
        :param span: The span of the external(to the tree) element.

        :return A node(constituent) where fit the external to the tree.
        """

        constituent = self.graph_builder.get_syntactic_parent(head)
        constituent_head = self.graph_builder.get_head_word(constituent)[ID]
        valid_constituent = head
        # Climb until head chain is broken
        while (constituent_head == head[ID] and
                constituent_tags.noun_phrase(constituent[TAG]) and
                constituent[SPAN][0] >= span[0] and
                constituent[SPAN][1] <= span[1]):
            valid_constituent = constituent
            constituent = self.graph_builder.get_syntactic_parent(constituent)
            constituent_head = self.graph_builder.get_head_word(constituent)[ID]
        return valid_constituent

    def _allocate_into_tree(self, external, root):
        """ Try to set a terminal head and a constituent of a named entity.

         The constituent and the head is used to order the mention in the sieve
         searching.

        :param root: The sentence where the word must be allocated.
        :param external: The named entity that must be allocated.
        """
        self.logger.debug("ALLOCATING: %s", external[FORM])
        # Find a plausible terminal head
        entity_span = external[SPAN]
        # Try to find a constituent that fit the mention span
        valid_constituent = self._get_span_constituent(root, entity_span)
        if valid_constituent:
            head_word = self.graph_builder.get_head_word(valid_constituent)
            constituent = valid_constituent
            external[CONSTITUENT_ALIGN] = "fitted"
            self.logger.debug("ALLOCATING: Valid constituent:-%s- (%s)",
                              head_word[FORM], constituent[FORM])
        else:
            # Use the head finder to get a plausible constituent
            head_word = self._get_plausible_head_word(
                self.graph_builder.get_words(external))
            # With the artificial Terminal head find a plausible NP constituent
            constituent = self._get_plausible_constituent(head_word, entity_span)
            external[CONSTITUENT] = constituent
            external[CONSTITUENT_ALIGN] = "plausible"
            self.logger.debug("ALLOCATING: Plausible constituent:-%s- (%s)",
                              head_word[FORM], constituent[FORM])
        self.graph_builder.link_root(
            external, self.graph_builder.get_root(constituent))
        self.graph_builder.set_head(external, head_word)
        external[CONSTITUENT] = constituent
        external[UTTERANCE] = constituent[UTTERANCE]
        external[QUOTED] = constituent[QUOTED]
        external[self.graph_builder.doc_type] = \
            head_word[self.graph_builder.doc_type]
        return constituent

    # Process of tree externals
    def _process_named_entities(self, sentence):
        """Add the named entities to the candidates.

        For every entity in the sentence:
            + Add their span for quick check
            + Add their reference to a list
            + Add their reference by constituent


        :param sentence: The base node for the sentence named entities.
            usually the root node.
        """
        for entity in self.graph_builder.get_sentence_named_entities(sentence):
            self.named_entities.append(entity)
            # Allocate in the tree
            constituent = self._allocate_into_tree(
                entity, sentence)
            self.graph_builder.get_head_word(entity)[HEAD_OF_NER] = entity[NER]
            if ner_tags.mention_ner(entity[NER]):
                entity_span = entity[SPAN]
                # Add the mention to registers
                self.named_entities_span.append(entity_span)
                self.sentence_named_entities_by_constituent[constituent[ID]] \
                    .append(entity)

    def _process_gold_mentions(self, sentence):
        """Add the named entities to the candidates.

        For every mention in the sentence:
            + Store as a mention
            + Add their span for the no inside NE restriction
         :param sentence: The base node for the sentence named entities. usually
             the root node.
        """
        for gold_mention in self.graph_builder.get_sentence_gold_mentions(sentence):
            # Try to match a NE
            self.gold_entities_spans.append(gold_mention[SPAN])
            if not self.gold_boundaries:
                continue
            gold_mention_span = gold_mention[SPAN]
            self.logger.debug(
                "Gold mention allocation: Start (%s)", gold_mention[FORM])
            if gold_mention_span in self.named_entities_span:
                # Fitting NE
                for name_entity in self.named_entities:
                    if gold_mention_span == name_entity[SPAN]:
                        self.logger.debug("Gold mention allocation: NE paired")
                        # Lock the mention in the tree
                        self.graph_builder.link_root(
                            gold_mention, self.graph_builder.get_root(name_entity))
                        self.graph_builder.set_head(
                            gold_mention,
                            self.graph_builder.get_head_word(name_entity))
                        constituent = name_entity[CONSTITUENT]
                        gold_mention[CONSTITUENT] = constituent
                        # Inherit attributes from NE
                        gold_mention[UTTERANCE] = name_entity[UTTERANCE]
                        gold_mention[QUOTED] = name_entity[QUOTED]
                        gold_mention[NER] = name_entity[NER]
                        gold_mention[self.graph_builder.doc_type] = \
                            name_entity[self.graph_builder.doc_type]
                        self.logger.debug("Gold mention allocation: NE paired %s", constituent[FORM])
                        gold_mention[CONSTITUENT_ALIGN] = "NE_" + name_entity[CONSTITUENT_ALIGN]
                        break
                else:
                    # Apparently something failed, this doesn't happens if NE
                    # load is correct
                    constituent = self._allocate_into_tree(
                        gold_mention, sentence)
                    # if gold_mention[CONSTITUENT_ALIGN] == "fitted":
                    #     constituent["GOLD"] = gold_mention[ID]
                    gold_mention["NE_align"] = "FAIL"
                    self.logger.warning(
                        "Gold Mention allocation: NE pairing failed %s", constituent[FORM])
            else:
                # Allocate in the tree
                constituent = self._allocate_into_tree(
                    gold_mention, sentence)
                gold_mention["NE_align"] = False
                self.logger.debug(
                    "Gold Mention allocation: constituent pairing %s", constituent[FORM])

            # Add the mention to registers
            self.sentence_gold_mentions_by_constituent[constituent[ID]].append(gold_mention)
            constituent["Gold_mention_id"] = gold_mention[ID]
            constituent["Gold_mention_align"] = gold_mention[CONSTITUENT_ALIGN] == "fitted"
            # The id of a gold mention is entity_index#mention_index
            entity = gold_mention[ID].split("#")[0]
            #self.gold_mentions_by_span[gold_mention_span] = gold_mention
            # try:
            #     self.gold_entities[entity].append(gold_mention)
            # except KeyError:
            #     self.logger.debug("New Entity: ")
            #     self.gold_entities[entity] = [gold_mention]

    # Sentence extraction entry point
    def process_sentence(self, sentence):
        """ Extract al the mentions of the Order all graph syntactic trees in
        filtered breath-first-transverse.

        :param sentence: The sentence whose mentions are wanted.
        """
        # Initialize sentence structures

        self.sentence_named_entities_by_constituent = defaultdict(list)
        self.sentence_gold_mentions_by_constituent = defaultdict(list)
        # The spans are used to avoid duplicate mentions and mention inside NE
        self._sentence_candidates_span = []
        self._sentence_candidates_ids = []
        self.named_entities_span = []
        # Prepare the Named entities before the tree traversal
        self._process_named_entities(sentence)
        self._process_gold_mentions(sentence)
        # Skip useless Root nodes
        syntax_root = self.graph_builder.skip_root(sentence)
        # Thought the rabbit hole
        self.sentence_mentions_order = []
        self.sentence_candidates_order = []

        self.mention_extractor.extract(
            order=self.sentence_mentions_order,
            root=syntax_root, validation=self._validate_node,
            named_entities_by_constituent=self.sentence_named_entities_by_constituent,
            gold_mentions_by_constituent=self.sentence_gold_mentions_by_constituent,
        )

        self.candidate_extractor.extract(
            order=self.sentence_candidates_order,
            root=syntax_root, validation=self._check_node,
            named_entities_by_constituent=self.sentence_named_entities_by_constituent,
            gold_mentions_by_constituent=self.sentence_gold_mentions_by_constituent,
        )

        self._lost_caught.update({
             str(span): ("NO", "OUT")
             for span in self.gold_entities_spans
             if (str(span) not in self._ok_caught) and (str(span) not in self._wrong_filtered)})

        return (
            self.sentence_candidates_order,
            self.sentence_mentions_order,
        )

    def _mention_meta(self, mention):
        root = self.graph_builder.get_root(mention)
        offset = root[SPAN][0]
        sentence_form = root[FORM].split(" ")
        sentence_span = (mention[SPAN][0] - offset, mention[SPAN][1] - offset)
        self._mentions[mention[ID]] = {
            ID: mention[ID],
            FORM: mention[FORM],
            SPAN: (mention[SPAN][0], mention[SPAN][1]),
            TAG: mention.get(TAG, "none"),
            POS: mention.get(POS, "none"),
            NER: mention.get(NER, 'none'),
            "sentence": " ".join(
                sentence_form[:sentence_span[0]] +
                ["["] + sentence_form[sentence_span[0]:sentence_span[1]+1] + ["]"] +
                sentence_form[sentence_span[1]+1:]),
            "sentence_span": sentence_span,
            "tree": self.graph_builder.print_tree(root),
            "headword": self.graph_builder.get_head_word(mention)[FORM],
            }
