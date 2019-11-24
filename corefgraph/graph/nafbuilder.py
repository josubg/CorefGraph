# coding=utf-8
""" The kaf version of the graph builder

"""

import logging
from collections import defaultdict, deque
from operator import itemgetter
from pynaf import NAFDocument, KAFDocument

from corefgraph.multisieve.features.constants import SPEAKER
from corefgraph.graph.builder import BaseGraphBuilder
from corefgraph.graph.wrapper import GraphWrapper
from corefgraph.resources import tree
from corefgraph.resources.dictionaries import stopwords
from corefgraph.resources.tagset import constituent_tags
from corefgraph.constants import POS, NER, TAG, SPAN, FORM, ID, SENTENCE, QUOTED, PREV_SPEAKER, \
    UTTERANCE, TREE, HEAD_OF_NER, GOLD, SINGLETON

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class NafAndTreeGraphBuilder(BaseGraphBuilder):
    """Extract the info from KAF documents and TreeBank."""

    naf_document_property = "kaf"
    naf_id_property = "kaf_id"
    naf_offset_property = "offset"
    naf_label = "label"
    naf_word_length = "length"
    naf_entity_type = "type"
    naf_entity_begin = "begin"
    naf_entity_end = "end"
    naf_mention_begin = "begin"
    naf_mention_end = "end"
    naf_tree_from = "from"
    naf_tree_to = "to"
    naf_head_mark = "head"

    encoding = "utf8"
    speaker_pattern = "PER{0}"
    term_pattern = "t{0}"
    constituent_pattern = "C{0}"
    id_pattern = "{0}#{1}"
    label_pattern = "{0} | {1}"

    root_tag = "ROOT"

    def __init__(self, reader_name, secure_tree=True,
                 logger=logging.getLogger(__name__)):
        super(NafAndTreeGraphBuilder, self).__init__()
        if reader_name == "NAF":
            self.document_reader = NAFDocument
        elif reader_name == "KAF":
            self.document_reader = KAFDocument
        else:
            raise Exception("Unknown Reader")
        self.secure_tree = secure_tree
        self.logger = logger
        self.syntax_count = 0
        self.leaf_count = 0
        self.naf = None
        self.sentence_order = 0
        self.utterance = -1
        self.speakers = []
        self.max_utterance = 1
        self.terms_pool = []
        self.term_by_id = dict()
        self.term_by_word_id = dict()
        self.entities_by_word = dict()
        self._sentences = None
        self.graph_utils = GraphWrapper

    def process_document(self, document):
        """ Get a document and prepare the graph and the graph builder to
        sentence by sentence processing of the document.

        :param document: A tuple that contains (the NAF,Sentences or none,
            speakers or none)
        """
        # Counter to order the sentences inside a text.
        self.sentence_order = 1
        if document[1]:
            self._sentences = document[1].strip().split("\n")
        # If speaker is None store None otherwise store split speaker file
        if document[2]:
            # Remove the blank lines and split
            self.speakers = []
            current_speaker = None
            self.max_utterance = 0
            for line in document[2].split("\n"):
                # sentences are separated by blank lines
                if line == "":
                    continue
                speaker = line.replace("_", "").lower().strip()
                self.speakers.append(speaker)
                if current_speaker != speaker:
                    self.max_utterance += 1
                    current_speaker = speaker

            # A doc is a conversation if exist two o more speakers in it
        else:
            self.speakers = []

            self.max_utterance = 1
        self.set_speakers(self.speakers)
        self.utterance = 0
        self._parse_naf(naf_string=document[0].strip())

    def get_original(self):
        """ Return the original NAF document """
        return self.naf

    def get_sentences(self):
        """ Get the sentences of the document.

        :return: A list of trees(kaf nodes or Penn Treebank strings)
        """
        if self._sentences:
            return self._sentences
        else:
            return self.naf.get_constituency_trees()

    def _parse_naf(self, naf_string):
        """ Parse all the kaf info tho the graph except of sentence parsing.

        :param naf_string: The string that contains the string of the NAF file content.
        """
        self.terms_pool = []
        # Store original kaf for further recreation
        self.naf = self.document_reader(input_stream=naf_string)
        self._set_terms(self.naf)
        self._set_entities(self.naf)
        self._set_mentions(self.naf)
        self._set_dependencies(self.naf)

    def _set_terms(self, naf):
        """ Extract the terms of the kaf and add to the graph

        :param naf: The kaf file manager
        """
        # Words
        kaf_words = dict([
                             (kaf_word.attrib[self.document_reader.WORD_ID_ATTRIBUTE], kaf_word)
                             for kaf_word in naf.get_words()])
        # Terms
        self.term_by_id = dict()
        self.term_by_word_id = dict()
        prev_speaker = None
        prev_form = None
        if self.max_utterance > 1:
            doc_type_value = self.doc_conversation
        else:
            doc_type_value = self.doc_article
        GraphWrapper.set_graph_property(
            self.graph, self.doc_type, doc_type_value)
        inside_utterance = deque()
        inside_plain_quotes = False
        for term in naf.get_terms():
            term_id = term.attrib[self.document_reader.TERM_ID_ATTRIBUTE]
            # Fetch the words of the term values
            term_words = sorted(
                (
                    kaf_words[word.attrib[ID]]
                    for word in naf.get_terms_words(term)),
                key=lambda x: x.attrib[self.naf_offset_property])
            # Build term attributes
            form = self._expand_kaf_word(term_words)
            span = (
                int(term_words[0].attrib[
                    self.document_reader.WORD_ID_ATTRIBUTE][1:]),
                int(term_words[-1].attrib[
                    self.document_reader.WORD_ID_ATTRIBUTE][1:]))
            begin = int(term_words[0].attrib[self.naf_offset_property])
            end = int(term_words[-1].attrib[self.naf_offset_property]) \
                + int(term_words[-1].attrib[self.naf_word_length]) - 1
            # We want pennTreeBank tagging no kaf tagging
            pos = term.attrib[self.document_reader.MORPHOFEAT_ATTRIBUTE]
            kaf_id = self.id_pattern.format(
                term_id, "|".join(
                    [word.attrib[self.document_reader.WORD_ID_ATTRIBUTE]
                     for word in term_words]))
            # Clear unicode problems
            if isinstance(form, unicode):
                form = form.encode(self.encoding)
            try:
                lemma = term.attrib[self.document_reader.LEMMA_ATTRIBUTE]
                if lemma == "-":
                    raise KeyError
            except KeyError:
                lemma = form
            if isinstance(lemma, unicode):
                lemma = lemma.encode(self.encoding)

            label = "\n".join((form, pos, lemma, term_id))
            # Create word node
            word_node = self.add_word(form=form, node_id=term_id, label=label, lemma=lemma, pos=pos, span=span,
                                      begin=begin, end=end)
            word_node[self.naf_id_property] = kaf_id
            word_node[PREV_SPEAKER] = prev_speaker
            if self.speakers:
                speaker = self.speakers.pop(0)
                if not speaker or speaker == "-":
                    form_speaker = self.speaker_pattern.format(self.utterance)
                else:
                    form_speaker = speaker
                if prev_speaker != speaker:
                    if prev_speaker is not None:
                        self.utterance += 1
                    prev_speaker = speaker
            else:
                form_speaker = self.speaker_pattern.format(self.utterance)

            # Manage Quotation
            if form != prev_form:
                if stopwords.speaking_begin(form) or (stopwords.speaking_ambiguous(form)and not inside_plain_quotes):
                    self.max_utterance += 1
                    inside_utterance.append(self.max_utterance)
                    # if form == '"':
                    if stopwords.speaking_ambiguous(form):
                        inside_plain_quotes = True
                elif stopwords.speaking_end(form) or (stopwords.speaking_ambiguous(form) and inside_plain_quotes):
                    if stopwords.speaking_ambiguous(form):
                        inside_plain_quotes = False
                    try:
                        inside_utterance.pop()
                    except IndexError:
                        self.logger.warning("Unbalanced quotes")

            if len(inside_utterance):
                word_node[UTTERANCE] = inside_utterance[-1]
                word_node[SPEAKER] = self.speaker_pattern.format(inside_utterance[-1])
                word_node[QUOTED] = True
            else:
                word_node[SPEAKER] = form_speaker
                word_node[UTTERANCE] = self.utterance
                word_node[QUOTED] = False
            prev_form = form
            word_node[self.doc_type] = doc_type_value
            # Store term
            # ONLY FOR STANFORD DEPENDENCIES IN KAF
            for word in term_words:
                self.term_by_word_id[
                    word.attrib[
                        self.document_reader.WORD_ID_ATTRIBUTE]] = word_node
            self.term_by_id[term_id] = word_node
            self.terms_pool.append(word_node)
        self.leaf_count = 0

    def _set_entities(self, naf):
        """ Extract the entities of the kaf and add to the graph

        :param naf: The kaf file manager
        """
        # A dict of entities that contains a list of references.
        # A reference is a list of terms.
        self.entities_by_word = defaultdict(list)
        for kaf_entity in naf.get_entities():
            entity_type = kaf_entity.attrib[self.naf_entity_type]
            entity_id = kaf_entity.attrib[
                self.document_reader.NAMED_ENTITY_ID_ATTRIBUTE]
            for reference in naf.get_entity_references(kaf_entity):
                # Fetch terms and convert ID into terms
                entity_terms = sorted(
                    [self.term_by_id[term.attrib[ID]]
                     for term in naf.get_reference_span(reference)],
                    key=itemgetter(SPAN))
                # Build form
                form = self._expand_node(entity_terms)
                # Build the entity
                label = self.label_pattern.format(form, entity_type)
                entity = self.add_named_entity(
                    entity_type=entity_type, entity_id=entity_id, label=label)
                # Set the other attributes
                entity[NER] = entity_type
                entity[FORM] = form
                entity[SPAN] = (
                    entity_terms[0][SPAN][0],
                    entity_terms[-1][SPAN][-1]
                    )
                # Link words_ids to mention as word
                for term in entity_terms:
                    self.link_word(entity, term)
                    #term[HEAD_OF_NER] = entity_type
                # Index the entity by its first word
                first_word_id = entity_terms[0][ID]
                self.entities_by_word[first_word_id].append(entity)

    def _set_mentions(self, naf):
        """ Extract the entities of the kaf and add to the graph

        :param naf: The kaf file manager
        """
        # A dict of entities that contains a list of references.
        # A reference is a list of terms.
        self.mentions_by_word = defaultdict(list)
        for kaf_entity in naf.get_coreference():
            entity_id = kaf_entity.attrib[
                self.document_reader.COREFERENCE_ID_ATTRIBUTE]
            counter = 0
            singleton = len(naf.get_coreference_mentions(kaf_entity)) == 1
            for reference in naf.get_coreference_mentions(kaf_entity):
                counter += 1
                # Fetch terms
                entity_terms = sorted(
                    [self.term_by_id[term.attrib[ID]]
                     for term in set(naf.get_reference_span(reference))],
                    key=itemgetter(SPAN))
                # Build form
                form = self._expand_node(entity_terms)
                # Build the entity
                label = self.label_pattern.format(form, "Gold")
                mention = self.add_gold_mention(
                    mention_id=self.id_pattern.format(entity_id, counter),
                    entity_id=entity_id,
                    label=label)
                # Set the other attributes
                mention[GOLD] = True
                mention[SINGLETON] = singleton
                mention[FORM] = form
                mention[SPAN] = (
                    entity_terms[0][SPAN][0],
                    entity_terms[-1][SPAN][-1])
                # Link words_ids to mention as word
                for term in entity_terms:
                    self.link_word(mention, term)
                # Index the entity by its first word
                first_word_id = entity_terms[0][ID]
                self.mentions_by_word[first_word_id].append(mention)

    def _set_dependencies(self, naf):
        """ Extract the dependencies of the kaf and add to the graph

        :param naf: The kaf file manager
        """
        for dependency in naf.get_dependencies():
            dependency_from_id = dependency.attrib[
                self.document_reader.DEPENDENCY_FROM_ATTRIBUTE]
            dependency_to_id = dependency.attrib[
                self.document_reader.DEPENDENCY_TO_ATTRIBUTE]
            dependency_type = dependency.attrib[
                self.document_reader.DEPENDENCY_FUNCTION_ATTRIBUTE]
            # IFS For STANFORD DEPENDENCIES IN KAF
            if dependency_from_id[0] == "w":
                dependency_from = self.term_by_word_id[dependency_from_id]
            else:
                dependency_from = self.term_by_id[dependency_from_id]
            if dependency_to_id == "TOP":
                continue
            if dependency_to_id[0] == "w":
                dependency_to = self.term_by_word_id[dependency_to_id]
            else:
                dependency_to = self.term_by_id[dependency_to_id]
            self.link_dependency(
                dependency_from, dependency_to, dependency_type)

    def process_sentence(self, sentence, root_index, sentence_namespace):
        """Add to the graph the morphological, syntactical and dependency info
        contained in the sentence.

        :param sentence: the sentence to parse
        :param sentence_namespace: prefix added to all nodes ID strings.
        :param root_index: The index of the root node
        """
        sentence_id = sentence_namespace
        sentence_label = sentence_namespace

        # Sentence Root
        sentence_root_node = self.add_sentence(
            root_index=root_index, sentence_form="",
            sentence_label=sentence_label, sentence_id=sentence_id)

        sentence_root_node[SENTENCE] = self.sentence_order
        sentence_root_node[TAG] = self.root_tag

        self._parse_syntax(
            sentence=sentence, syntactic_root=sentence_root_node)
        # copy the properties to the root
        self.sentence_order += 1
        # Return the generated context graph
        return sentence_root_node

    def _iterate_syntax(self, syntactic_tree, parent, syntactic_root):
        """ Walk recursively over the syntax tree and add their info to the
        graph.

        :param syntactic_tree: The subtree to process
        :param parent: The parent node of the subtree
        :param syntactic_root: The syntactic root node of all the tree

        :return: The element created from the top of the subtree
        """
        # Aux functions
        def syntax_leaf_process(parent_node, leaf):
            """ Process a final node of the tree.

            :param parent_node: The upside node of the element
            :param leaf: The node to process

            :return: The word that correspond to the leaf.
            """
            # the tree node is a leaf
            # Get the text of the tree to obtain more attributes
            self.leaf_count += 1
            text_leaf = leaf.node
            # treebank_word = leaf[0]
            is_head = "=H" in text_leaf or "-H" in text_leaf
            leaf_pos = text_leaf.split()[0].replace("=H", "").replace("-H", "")
            try:
                word_node = self.terms_pool.pop(0)
                self.last_word = word_node
            except IndexError:
                self.logger.warning("Unaligned Tree LEAF")
                word_node = self.last_word
            if word_node[POS] != leaf_pos:
                self.logger.debug("Warning Unmatched POS(%s): %s %s", leaf, word_node[POS], leaf_pos)
            # Get the word node pointed by the leaf

            # Word is mark as head
            if is_head:
                self.set_head(parent_node, word_node)
            # Word is mark as Named Entity
            if "|" in text_leaf:
                self.set_ner(
                    node=word_node, ner_type=text_leaf.split("|")[-1])
            # Link the word to the constituent(Parent of this leaf)
            self.link_syntax_terminal(parent=parent_node, terminal=word_node)
            # link the word to the sentence
            self.link_root(sentence=syntactic_root, element=word_node)
            self.link_word(sentence=syntactic_root, word=word_node)
            # Enlist entities that appears in the phrase
            for mention in self.entities_by_word.get(word_node[ID], []):
                self.add_mention_of_named_entity(
                    sentence=syntactic_root, mention=mention)
            # Enlist gold mention that appears in the phrase
            for mention in self.mentions_by_word.get(word_node[ID], []):
                self.add_mention_of_gold_mention(
                    sentence=syntactic_root, mention=mention)
            return word_node

        def syntax_branch_process(parent_node, branch):
            """ Process a intermediate node of the tree.

            :param parent_node: The upside node of the element
            :param branch: The node to process

            :return: The constituent created from the top of the branch
            """
            # Create a node for this element
            label = branch.node
            # constituent is mark as head
            head = "=H" in label or "-H" in label
            tag = label.replace("=H", "").replace("-H", "")
            # Constituent is mark as ner
            if "|" in label:
                ner = label.split("|")[-1]
            else:
                ner = None

            tag = tag.split("|")[0]
            order = self.syntax_count

            new_constituent = self.add_constituent(
                node_id=self.constituent_pattern.format(order), sentence=syntactic_root, tag=tag,
                order=order, label=label)
            self.set_ner(new_constituent, ner)
            self.syntax_count += 1
            # Process the children
            children = [
                self._iterate_syntax(
                    syntactic_tree=child, parent=new_constituent,
                    syntactic_root=syntactic_root)
                for child in branch]
            children.sort(key=itemgetter(SPAN))

            # Link the child with their parent (The actual processed node)
            self.link_syntax_non_terminal(
                parent=parent_node, child=new_constituent)
            if head:
                self.set_head(parent_node, new_constituent)

            self.fill_constituent(new_constituent)
            new_constituent[TREE] = branch
            return new_constituent

        # ======MAIN FUNCTION==================
        # Determine if the syntactic tree Node is as branch or a leaf
        if len(syntactic_tree) > 1 or \
                not (isinstance(syntactic_tree[0], str) or isinstance(syntactic_tree[0], unicode)):
            constituent_or_word = syntax_branch_process(
                parent_node=parent, branch=syntactic_tree)
            self.syntax_count += 1
        else:
            constituent_or_word = syntax_leaf_process(
                parent_node=parent, leaf=syntactic_tree)
        return constituent_or_word

    def _parse_syntax_naf(self, sentence, syntactic_root):
        """ Add the syntax info from a NAF tree node

        :param sentence: The NAF tree element
        :param syntactic_root: The sentence node
        :return: the syntax root node or the first constituent
        """
        # Process Non Terminals
        constituents_by_id, root = self.process_no_terminals(sentence, syntactic_root)
        # Process Terminals
        terminals_words = self._naf_process_terminals(sentence)
        # Process the edges
        edges_by_departure_node = self.process_edges(sentence)
        # Ensure the link between the tree with the root
        if root is None:
            for constituent in constituents_by_id.viewkeys():
                if constituent not in edges_by_departure_node:
                    constituents_by_id[constituent] = syntactic_root
                    self.logger.warning(
                        "No ROOT found: No departure constituent used %s", constituent)
                    break
            else:
                lowest_id = sorted(constituents_by_id.viewkeys())[0]
                constituents_by_id[lowest_id] = syntactic_root
                self.logger.warning("No ROOT found: lowest id constituent used %s", lowest_id)

        # Process bottom-up the syntax tree. Edge by edge.
        node_process_list = terminals_words.keys()
        while len(node_process_list):
            edge = edges_by_departure_node[node_process_list.pop(0)]
            # The edges have a down-top direction
            target_id = edge.attrib[self.naf_tree_to]
            source_id = edge.attrib[self.naf_tree_from]
            # Add the target to processing queue.
            # Root doesn't have to be processed.
            target = constituents_by_id[target_id]
            if target != syntactic_root:
                node_process_list.append(target_id)
            # select link type in base of the source node type
            # Relations from No terminal edge (Constituent)
            if source_id.startswith("n"):
                source = constituents_by_id[source_id]
                self.link_root(sentence=syntactic_root, element=source)
                self.link_syntax_non_terminal(parent=target, child=source)
                # Set the head of the constituent
                if edge.attrib.get(self.naf_head_mark, False):
                    try:
                        self.set_head(parent=target, head=source)
                    except Exception as ex:
                        self.logger.warning(
                            "Error setting a head: Source %s ID#%s Target "
                            "%s ID#%s Error: %s",
                            target_id, target, source_id, source, ex)
            else:
                # Relations for terminal edges (Words)
                source = terminals_words[source_id]
                # Artificial constituent that is in fact a POS tag
                nexus_constituent = constituents_by_id[target_id]
                self.remove(nexus_constituent)
                constituents_by_id[target_id] = source[-1]
                # Sanity warning
                if nexus_constituent[TAG] != source[-1][POS]:
                    self.logger.debug(
                        "Warning Unmatched POS(%s): %s %s ",
                        source[-1]["form"], nexus_constituent[TAG], source[-1][POS])
                if len(source) > 1:
                    self.logger.debug("Warning Multi-word: Setting last as head: %s", source_id)
                for word in source:
                    # Lint to sentence ROOT
                    self.link_root(sentence=syntactic_root, element=word)
                    self.link_word(sentence=syntactic_root, word=word)
                    # Enlist entities that appears in the phrase
                    for mention in self.entities_by_word.get(word[ID], []):
                        self.add_mention_of_named_entity(
                            sentence=syntactic_root, mention=mention)
                    for mention in self.mentions_by_word.get(word[ID], []):
                        self.add_mention_of_gold_mention(
                            sentence=syntactic_root, mention=mention)
                # Set the head the last, Usually the only one
                self.set_head(target, source[-1])

        # Build constituent child based values
        # for constituent in constituents_by_id.viewvalues():
        #     if constituent.get(TAG) != self.word_node_tag:
        #         self.fill_constituent(constituent)

    def _naf_process_terminals(self, sentence):
        terminals = self.naf.get_constituent_tree_terminals(sentence)
        terminals_words = dict()
        # Build Terminals constituents
        for terminal in terminals:
            terminal_id = terminal.attrib[ID]
            terminals_words[terminal_id] = [
                self.term_by_id[target_term.attrib[ID]]
                for target_term
                in self.naf.get_constituent_terminal_words(terminal)]
        return terminals_words

    def process_edges(self, sentence):
        edges_by_departure_node = {}
        edges_list = self.naf.get_constituent_tree_edges(sentence)
        for edge in edges_list:
            edges_by_departure_node[edge.attrib[self.naf_tree_from]] = edge
        return edges_by_departure_node

    def process_no_terminals(self, sentence, syntactic_root):
        """Process the kaf nodes that represents the syntactic constituents.

        :param sentence: The root node of the kaf syntactic re
        :param syntactic_root: The node of the graph where attach syntactic tree.

        :return a dict (id, constituents) and the root of the sentence(syntactic_root if everything goes correctly)

        """
        constituents_by_id = dict()
        root = None
        # Build no terminal constituents
        for non_terminal \
                in self.naf.get_constituent_tree_non_terminals(sentence):
            constituent_id = non_terminal.attrib[ID]
            tag = non_terminal.attrib[self.naf_label]
            if constituent_tags.root(tag):
                constituents_by_id[constituent_id] = syntactic_root
                root = syntactic_root
            else:
                order = self.syntax_count
                self.syntax_count += 1
                constituent = self.add_constituent(
                    node_id=constituent_id, sentence=syntactic_root, tag=tag,
                    order=order, label=tag)
                constituent[NER] = None
                constituents_by_id[constituent_id] = constituent
        return constituents_by_id, root

    def _parse_syntax(self, sentence, syntactic_root):
        """ Parse the syntax of the sentence.

        :param sentence:  The sentence syntactic structure maybe a PeenTreeBank string or NAF structure.
        :param syntactic_root: The root where attach the syntactic structure.

        :return: The upper node of the syntax tree.
        """
        # Convert the syntactic tree
        if type(sentence) is str:
            # Is a plain Penn-tree
            sentence = self.clean_penn_tree(sentence)
            syntactic_tree = tree.Tree(sentence)
            # Skip root node (TOP, ROOT...)
            if constituent_tags.root(syntactic_tree.node):
                syntactic_tree = syntactic_tree[0]
            # Call to the recursive function
            self._iterate_syntax(
                syntactic_tree=syntactic_tree, parent=syntactic_root,
                syntactic_root=syntactic_root)
        else:
            # Is a Naf tree
            self._parse_syntax_naf(
                sentence=sentence, syntactic_root=syntactic_root)
        self.fill_constituent(syntactic_root)

    # AUX FUNCTIONS
    @staticmethod
    def _expand_kaf_word(words):
        """ Rebuild the text form from a list of kaf words.

        :param words: a list of KAF words

        :return: the form of all words separated by comas.
        """
        text = " ".join([word.text for word in words])
        return text.strip()

    @staticmethod
    def clean_penn_tree(penn_tree):
        """ Clean from the tree all knows problems.

        :param penn_tree: the plain text tree

        :return: cleaned tree
        """
        penn_tree = penn_tree.strip()
        return penn_tree

    def skip_root(self, sentence_root):
        """Get the first chunk of the sentence (usually S) Skip al ROOT nodes,
        created by the parser o the graph builder.

        Skip all the dummy roots crated by the parsers/graph builder.

        :param sentence_root: The syntactic tree root node.
        """
        chunk = sentence_root
        while chunk and (chunk[TAG] == self.root_pos):
            children = self.get_syntactic_children_sorted(chunk)[0]
            if type(children) is list:
                if len(children):
                    return chunk
                else:
                    chunk = children[0]
            else:
                chunk = children
        return chunk
