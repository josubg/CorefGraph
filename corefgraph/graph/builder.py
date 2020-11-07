# coding=utf-8
""" Base of graph creators to convert external linguistic knowledge into a graph
 usable by the system.
"""
from logging import getLogger
from corefgraph.resources.rules import rules
from corefgraph.graph.wrapper import GraphWrapper
from corefgraph.constants import SPAN, ID, NER, CONSTITUENT,\
    SENTENCE, LABEL, TAG, LEMMA, FORM, UTTERANCE, QUOTED, BEGIN, END, POS, DEEP


class BaseGraphBuilder(object):
    """ THe Basic operations of text graph.
    """

    doc_type = "doc_type"
    doc_article = "article"
    doc_conversation = "conversation"

    node_type = "type"

    root_type = "ROOT"
    root_pos = "ROOT"
    root_label = "ROOT"
    root_edge_type = "ROOT"

    sentence_order_edge_type = "order"
    sentence_order_edge_label = "order"

    word_node_type = "word"
    word_edge_type = "word"
    word_node_tag = "WORD"

    entity_node_type = "entity"
    entity_edge_type = "refers"
    entity_edge_label = "refers"

    gold_mention_node_type = "gold_mention"
    gold_mention_edge_type = "gold_mention"
    gold_mention_edge_label = "gold_mention"

    named_entity_node_type = "named_entity"
    named_entity_edge_type = "named_refers"
    named_entity_edge_label = "named_refers"

    syntactic_node_type = "constituent"
    syntactic_edge_type = "syntactic"
    syntactic_edge_label = "syntactic"
    syntactic_edge_value_branch = "contains"
    syntactic_edge_value_terminal = "terminal"

    head_edge_type = "is_head"
    head_word_edge_type = "is_head_word"

    dependency_node_type = "dependency"
    dependency_edge_type = "dependency"

    # Dependency edge Value is determined by parser

    label_pattern = "{0} | {1}"

    HEAD = "head"
    HEADWORD = "head_word"

    def __init__(self):
        self.graph = None
        self.previous_sentence = None
        self.logger = getLogger(__name__)
        self.graph = GraphWrapper.blank_graph()
        self.graph.graph['graph_builder'] = self

    def get_doc_type(self):
        """ Return the doctype of the document."""
        return GraphWrapper.get_graph_property(self.graph, self.doc_type)

    def get_speakers(self):
        """ Return the speakers of the document."""
        return GraphWrapper.get_graph_property(self.graph, "speakers")

    def set_speakers(self, speakers):
        """ Set the speakers of the document."""
        GraphWrapper.set_graph_property(self.graph, "speakers", speakers)

    def get_original(self):
        """ Return de original representation of the document.
        """
        raise NotImplemented()

    @staticmethod
    def set_ner(node, ner_type):
        """ Set the NER type to a constituent.

        :param node: The constituent.
        :param ner_type: The ner type.
        """
        node[NER] = ner_type

    # Sentence Related
    def add_sentence(
            self, root_index, form, label, node_id):
        """ Create a new sentence in the graph. Also link it to the previous
        sentence.

        :param root_index: The index of the sentence.
        :param form:
        :param label:
        :param node_id:
        :return: The sentence node
        """
        sentence_root_node = GraphWrapper.new_node(
            # graph=self.graph,
            graph=self.graph,
            node_type=self.root_type,
            node_id=node_id,
            form="{0}#{1}".format(self.root_label, form),
            label="{0}#{1}".format(self.root_label, label),
            ord=root_index,
            tag=self.root_pos,
            pos=self.root_pos,)
        if self.previous_sentence:
            self.link_sentences(self.previous_sentence, sentence_root_node)
        self.previous_sentence = sentence_root_node
        return sentence_root_node

    def link_sentences(self, sentence, next_sentence):
        """ link two consecutive sentences.

        :param sentence: first sentence of the union.
        :param next_sentence: Second sentence of the union.
        """
        GraphWrapper.link(
            self.graph, sentence, next_sentence,
            self.sentence_order_edge_type,
            1,
            self.sentence_order_edge_label)

    def get_next_sentence(self, sentence):
        """ Get the textual order next sentence.

        :param sentence: The root of the base sentence.
        :return: The next sentence.
        """
        for sentence_node, next_sentence, relation_type \
                in self.graph.out_edges(sentence[ID], keys=True):
            if relation_type == self.sentence_order_edge_type:
                return self.graph.node[next_sentence]
        return None

    def get_prev_sentence(self, sentence):
        """ Get the textual order previous sentence.

        :param sentence: The root of the base sentence.
        :return: The previous sentence.
        """
        for prev_sentence, sentence_node, relation_type \
                in self.graph.in_edges(sentence[ID], keys=True):
            if relation_type == self.sentence_order_edge_type:
                return self.graph.node[prev_sentence]
        return None

    def get_all_sentences(self):
        """ Get all the sentences of the graph.

        :return: A list of sentences.
        """
        return GraphWrapper.get_all_node_by_type(
            graph=self.graph, node_type=self.root_type)

    def same_sentence(self, element_a, element_b):
        """ Check if the nodes are in the same sentence.

        :param element_a: Word, constituent or Named entity.
        :param element_b: Word, constituent or Named entity.
        """
        root_a = self.get_root(element_a)
        root_b = self.get_root(element_b)

        return root_a == root_b

    def sentence_distance(self, element_a, element_b):
        """ Get the distance between the sentences of 2 nodes( 0 for same
        sentence nodes).

        The distance is always a positive number.

        :param element_a: Word, constituent or Named entity.
        :param element_b: Word, constituent or Named entity.
        """
        root_a = self.get_root(element_a)
        root_b = self.get_root(element_b)
        return abs(root_a[SENTENCE] - root_b[SENTENCE])

    def get_sentence_words(self, sentence):
        """Get the (Sorted)words contained in a sentence.

         This method not traverse the syntactic tree, used the root direct
         links. NOT USE WITH CONSTITUENT.

        :param sentence: the root node of the sentence.
        :return: The words of the sentence.
        """
        return sorted(GraphWrapper.get_out_neighbours_by_relation_type(
            graph=self.graph, node=sentence, relation_type=self.word_edge_type),
            key=lambda y: y[SPAN])

    # Coreference
    def add_coref_entity(self, node_id, mentions, label=None):
        """ Creates a entity with the identification provided and link to all
        the mentions passed.

        :param label: Optional label for the mention.
        :param mentions: List of mentions that forms the entity.
        :param node_id: identifier assigned to the mention.
        """
        graph = self.graph
        # Create the node that links all mentions as an entity.
        new_node = GraphWrapper.new_node(graph=graph,
                                         node_type=self.entity_node_type,
                                         node_id=node_id,
                                         label=label
                                         )
        # Mention lis is a list of mention node identifiers
        for mention in mentions:
            GraphWrapper.link(
                self.graph, node_id, mention,
                self.entity_edge_type,
                label=self.entity_edge_label)
        return new_node

    def get_all_coref_entities(self):
        """ Get all entities of the graph

        :return: A list of entities
        """
        return GraphWrapper.get_all_node_by_type(
            graph=self.graph, node_type=self.entity_node_type)

    def add_gold_mention(self, node_id, gold_entity, label):
        """Creates a gold mention into the graph.
        :param entity_id:  The ID of the entity.
        :param node_id: The ID of the gold mention in the graph
        :param label: A label for representation uses.
        """

        new_entity = GraphWrapper.new_node(
            graph=self.graph,
            node_type=self.gold_mention_node_type,
            node_id=node_id,
            label=label,
            gold_entity=gold_entity
        )
        return new_entity

    def get_gold_mention_by_span(self, span):
        return [gm for gm in GraphWrapper.get_all_node_by_type(
            graph=self.graph, node_type=self.gold_mention_node_type) if gm[SPAN] == span]

    def get_all_gold_mentions(self):
        """ Get all named entities of the graph

        :return: A list of named entities
        """
        return GraphWrapper.get_all_node_by_type(
            graph=self.graph, node_type=self.gold_mention_node_type)

    def get_all_named_entities(self):
        """ Get all named entities of the graph

        :return: A list of named entities
        """
        return GraphWrapper.get_all_node_by_type(
            graph=self.graph, node_type=self.named_entity_node_type)

    def get_all_words(self):
        """ Get all named entities of the graph

        :return: A list of named entities
        """
        return GraphWrapper.get_all_node_by_type(
            graph=self.graph, node_type=self.word_node_type)

    def get_all_constituents(self):
        """ Get all named entities of the graph

        :return: A list of named entities
        """
        return GraphWrapper.get_all_node_by_type(
            graph=self.graph, node_type=self.syntactic_node_type)

    def add_mention_of_gold_mention(self, sentence, mention):
        """ Add gold mention to a sentence.

        :param sentence: The sentence where the Gold mention is.
        :param mention: The gold mention
        """
        GraphWrapper.link(graph=self.graph, origin=sentence, target=mention,
                          link_type=self.gold_mention_edge_type,
                          label=self.gold_mention_edge_label)

    def get_sentence_gold_mentions(self, root):
        """Get the gold mentions contained in a sentence.

        This method not traverse the syntactic tree, used the root direct links.
        NOT USE WITH CONSTITUENT.

        :param root: the root of the sentence
        """
        return sorted(GraphWrapper.get_out_neighbours_by_relation_type(
            graph=self.graph, node=root,
            relation_type=self.gold_mention_edge_type),
            key=lambda y: y[SPAN])

    def get_all_entity_mentions(self, entity):
        """ Get mentions of a entity
        :param entity: The source entity
        :return: A list of mentions(elements)
        """
        return GraphWrapper.get_out_neighbours_by_relation_type(
            graph=self.graph, node=entity, relation_type=self.entity_edge_type)

    # Named entities
    def add_named_entity(self, entity_type, entity_id, label):
        """Creates a named entity into the graph.
        :param label: A label for representation uses.
        :param entity_id: The ID of the entity in the graph
        :param entity_type: The type of the NER
        """
        new_entity = GraphWrapper.new_node(
            graph=self.graph,
            node_type=self.named_entity_node_type,
            node_id=entity_id,
            label=label,
            ner=entity_type,
            tag=entity_type)
        return new_entity

    def get_all_named_entity(self):
        """Returns all named entities of  the graph.
        """
        new_entity = GraphWrapper.get_all_node_by_type(
            graph=self.graph,
            node_type=self.named_entity_node_type)
        return new_entity

    def add_mention_of_named_entity(self, sentence, mention):
        """ Add a mention of an Named Entity.
        :param sentence: The sentence where the mention is.
        :param mention: The mention of the Name entity.
        """
        GraphWrapper.link(graph=self.graph, origin=sentence, target=mention,
                          link_type=self.named_entity_edge_type,
                          label=self.named_entity_edge_label)

    def get_sentence_named_entities(self, root):
        """Get the (Sorted)named entities contained in a sentence.

        This method not traverse the syntactic tree, used the root direct links.
        NOT USE WITH CONSTITUENT.

        :param root: the root of the sentence
        """
        return sorted(GraphWrapper.get_out_neighbours_by_relation_type(
            graph=self.graph, node=root,
            relation_type=self.named_entity_edge_type),
            key=lambda y: y[SPAN])

    # Constituents
    def add_constituent(self, node_id, sentence, tag, order, label=None):
        """ Add a new constituent to the graph.
        :param node_id: The unique id in the graph
        :param sentence: The sentence Root
        :param tag: The tag of the constituent
        :param order: The order of the constituent
        :param label: A label for representation proposes

        :return: The constituent node
        """
        new_node = GraphWrapper.new_node(graph=self.graph,
                                         node_type=self.syntactic_node_type,
                                         node_id=node_id,
                                         tag=tag,
                                         label=label or tag,
                                         ord=order
                                         )
        if sentence:
            self.link_root(sentence, new_node)
        return new_node

    # Words
    def add_word(self, form, node_id, label, lemma, pos,
                 span, begin, end, sentence=None):
        """ Add a word into the graph. Also link it into its sentence

        :param form: The form of the word as it appears in the text.
        :param node_id: The unique id of the node
        :param label: The label of the word, for representative usage
        :param lemma: The lemma of the word
        :param pos: The Part of Speech of the word
        :param begin: Index of the fist character of the mention in the text.
        :param end: Index of the last character of the mention in the text.
        :param span: Index of the first and last token of the mention in the text
        :param sentence: The sentence where word appears.

        :return: The word node
        """
        word_node = GraphWrapper.new_node(
            graph=self.graph,
            node_type=self.word_node_type,
            node_id=node_id,
            form=form,
            label=label,
            pos=pos,
            lemma=lemma,
            span=span,
            tag=self.word_node_tag,
            begin=begin,
            end=end
        )
        if sentence:
            self.link_word(sentence=sentence, word=word_node)
            self.link_root(sentence=sentence, element=word_node)
        return word_node

    def link_word(self, sentence, word):
        """ Link a word with the sentence where it appears. Also make a root
        link.
        :param sentence: The sentence root node
        :param word: The word node
        """
        GraphWrapper.link(graph=self.graph, origin=sentence, target=word,
                          link_type=self.word_edge_type)

    def get_words(self, element):
        """ Get the words(sorted in textual order) of the constituent.

        If constituent is a word, returns the words in a list.

        :param element: Word, constituent or Named entity

        :return the words of the element in a list
        """
        if element[self.node_type] == self.word_node_type:
            return [element]
        words = GraphWrapper.get_out_neighbours_by_relation_type(
            self.graph, element, relation_type=self.word_edge_type)
        return sorted(words, key=lambda y: y[SPAN])

    def remove(self, element):
        """ Remove the element from the graph
        :param element: The element to remove
        """
        GraphWrapper.remove(graph=self.graph, element=element)

    def unlink(self, origin, target):
        """ Break all link between a nodes. Only in one direction.
        :param origin: The origin node of the links
        :param target: The target node of the links
        """
        GraphWrapper.unlink(graph=self.graph, origin=origin, target=target)

    # Dependency
    def link_dependency(self, dependency_from, dependency_to, dependency_type):
        """ Add a dependency relation to the graph. Remember that dependency
        relations are down-top.

        :param dependency_from: The origin of the link
        :param dependency_to: The target of the link
        :param dependency_type: The value of the link
        """
        GraphWrapper.link(
            graph=self.graph, origin=dependency_from, target=dependency_to,
            link_type=self.dependency_edge_type, value=dependency_type,
            weight=1, label=self.dependency_edge_type + "_" + dependency_type)

    def get_dependant_words(self, word):
        """ Get all words that depend on the word and the dependency type.
        :param word: The word where the dependency starts
        """
        children = GraphWrapper.get_out_neighbours_by_relation_type(
            node=word, relation_type=self.dependency_edge_type,
            graph=self.graph, keys=True)
        return children

    def get_governor_words(self, word):
        """ Get all words that rules a dependency link with the word and the
        dependency type.

        :param word: The word where the dependency ends
        """
        children = GraphWrapper.get_in_neighbours_by_relation_type(
            node=word, relation_type=self.dependency_edge_type,
            graph=self.graph, keys=True)
        return children

    # Syntax
    def link_root(self, sentence, element):
        """ Link a word with the sentence where it appears
        :param sentence: The sentence root node
        :param element: The element
        """
        GraphWrapper.link(
            graph=self.graph, origin=sentence, target=element,
            link_type=self.root_edge_type)

    def get_root(self, element):
        """Get the sentence of the element

        :param element: The constituent or word whose parent is wanted.
        """
        element = element.get(CONSTITUENT, element)
        return GraphWrapper.get_in_neighbour_by_relation_type(
            self.graph, element, self.root_edge_type)

    def get_all_elements_from_root(self, sentence):
        children = GraphWrapper.get_out_neighbours_by_relation_type(
            node=sentence, relation_type=self.root_edge_type,
            graph=self.graph)
        children.sort(key=lambda x: x[SPAN])
        return children

    def link_syntax_non_terminal(self, parent, child):
        """ Link a non-terminal(constituent) to the constituent. Also link the
        constituent child word with the parent.

        :param parent: The parent constituent
        :param child: The child constituent
        """
        for word in self.get_words(child):
            self.link_word(parent, word)

        label = self.syntactic_edge_label\
            + "_" \
            + self.syntactic_edge_value_branch

        GraphWrapper.link(
            graph=self.graph, origin=parent, target=child,
            link_type=self.syntactic_edge_type,
            value=self.syntactic_edge_value_branch,
            label=label)

    def link_syntax_terminal(self, parent, terminal):
        """  Link a word to a constituent. Also add the word to
        :param parent:
        :param terminal:
        :return:
        """
        self.link_word(parent, terminal)
        label = self.syntactic_edge_type \
            + "_" \
            + self.syntactic_edge_value_terminal
        GraphWrapper.link(
            graph=self.graph, origin=parent, target=terminal,
            link_type=self.syntactic_edge_type,
            value=self.syntactic_edge_value_terminal,
            weight=1,
            label=label)

    def set_head_word(self, element, head_word):
        """Set the head word of the element.

        :param element: Word, constituent or Named entity
        :param head_word: The word that is the head word
        """
        if head_word[self.node_type] != self.word_node_type:
            raise Exception("No word as head word")
        GraphWrapper.link(
            self.graph, element, head_word, self.head_word_edge_type)
        element[self.HEADWORD] = head_word

    def get_head_word(self, element):
        """ Get the head word. The word that is in the end of heads chain.
        :param element: Word, constituent or Named entity
        :return: The head word
        """
        if element[self.node_type] == self.word_node_type:
            return element
        try:
            return element[self.HEADWORD]
        except KeyError:
            if element.get(self.HEAD, False):
                return self.get_head_word(element[self.HEAD])
            else:
                self.logger.warning("No HEAD word:%s", element)
                return self.get_head_word(rules.get_plausible_head(self.get_syntactic_children_sorted(element)))

    def set_head(self, parent, head):
        """ Set a child as parent head and inverse inherit some values.
        :param parent: The parent constituent
        :param head: The child constituent or word
        """
        # Inverse inherit
        head[self.head_edge_type] = True
        # link
        parent[self.HEAD] = head
        GraphWrapper.link(self.graph, parent, head, self.head_edge_type)

    def get_head(self, element):
        """Get the head of the element. If a word id passed by error the word
        itself is returned.

        :param element: Word, constituent or Named entity
        """
        if element[self.node_type] == self.word_node_type:
            return element
        head = GraphWrapper.get_out_neighbour_by_relation_type(
            graph=self.graph, node=element, relation_type=self.head_edge_type)
        if head is None:
            return self.get_syntactic_children_sorted(element=element)[-1]
        return head

    def is_head(self, element):
        """ Determines if the constituent is head of its parent.
        :param element: The constituent to check
        :return: True of False
        """
        return self.head_edge_type in element and element[self.head_edge_type]

    # Syntactical navigation

    @staticmethod
    def is_inside(element_a_span, element_b_span):
        """Is a inside b?
        :param element_a_span: Word, constituent or Named entity span
        :param element_b_span: Word, constituent or Named entity span
        """
        return (element_a_span[0] >= element_b_span[0]) \
            and (element_a_span[1] <= element_b_span[1])

    def get_syntactic_children_sorted(self, element):
        """Get all the syntactical children of a element.

        :param element: The Word, constituent or Named entity whose children are
         wanted.
        """
        element = element.get(CONSTITUENT, element)
        children = GraphWrapper.get_out_neighbours_by_relation_type(
            graph=self.graph, node=element,
            relation_type=self.syntactic_edge_type)
        children.sort(key=lambda x: x[SPAN])
        return children

    def get_syntactic_children(self, element):
        """Get all the syntactical children of a element.

        :param element: The Word, constituent or Named entity whose children are
         wanted.
        """
        element = element.get(CONSTITUENT, element)
        children = GraphWrapper.get_out_neighbours_by_relation_type(
            graph=self.graph, node=element,
            relation_type=self.syntactic_edge_type)
        return children

    def get_syntactic_parent(self, element):
        """Return the syntactic parent of the node(constituent or word).

        :param element: The Word, constituent or Named entity whose parent is
            wanted.

        :return: The parent of the element.
        """
        element = element.get(CONSTITUENT, element)
        return GraphWrapper.get_in_neighbour_by_relation_type(
            self.graph, element, self.syntactic_edge_type)

    def get_syntactic_sibling(self, element):
        """ Get the ordered sibling of a syntactic node.

        :param element: Word, constituent or Named entity

        :return The siblings of the element, itself included.
        """
        element = element.get(CONSTITUENT, element)
        syntactic_father = self.get_syntactic_parent(element)
        siblings = self.get_syntactic_children_sorted(syntactic_father)
        siblings.sort(key=lambda x: x[SPAN])
        return siblings

    def show_graph(self):
        """ Show a windows with the graph
        """
        GraphWrapper.show_graph(graph=self.graph)

    def show_sentence(self, root, node_type=None):
        """ Show a windows with the sentence nodes.

        :param node_type: The type of the nodes to show.
        :param root: The root node of the sentence to show.
        """
        GraphWrapper.show_sentence(graph=self.graph, root=root, node_type=node_type)

    @classmethod
    def get_compose_id(cls, sentence_namespace, word_id, separator="_"):
        """ Generate a string id.

        :param sentence_namespace: The base name for the sentence.
        :param word_id: The id of the word
        :param separator: A separator between sentence and word

        :return The id.
        """
        return "{1}{0}{2}".format(separator, sentence_namespace, word_id)

    @staticmethod
    def check_sibling_property(base_index, siblings, _property, check_function):
        """ Return the forward siblings and return the first that fulfill
        the property.

        :param base_index: The index of the original sibling
        :param siblings: The ordered list of siblings
        :param _property: The name of the property to check
        :param check_function: The function used to check the property

        :return: the sibling that fulfill the property and its index.
        """
        constituent = None
        index = 0
        for index, sibling in enumerate(siblings[base_index:]):
            if _property in sibling and check_function(sibling[_property]):
                constituent = sibling
                break
        return constituent, index

    def fill_constituent(self, constituent, deep=0):
        """ Fill the constituent attributes with de data from its children

        :param constituent: The constituent to fill
        :param deep: The deep of the constituent, default 0

        :return: Nothing
        """
        words = self.get_words(constituent)
        content_text = self._expand_node(words)
        constituent[LABEL] = self.label_pattern.format(
            content_text, constituent[TAG])
        constituent[LEMMA] = self._expand_node_lemma(words)
        constituent[FORM] = content_text
        constituent[BEGIN] = words[0][BEGIN]
        constituent[END] = words[-1][END]
        constituent[SPAN] = (
            words[0][SPAN][0],
            words[-1][SPAN][-1]
        )
        constituent[DEEP] = deep
        for child in self.get_syntactic_children(constituent):
            if child[self.node_type] == self.word_node_type:
                child[DEEP] = deep + 1
                continue
            self.fill_constituent(child, deep + 1)
        head_word = self.get_head_word(constituent)
        self.set_head_word(constituent, head_word)
        constituent[self.doc_type] = head_word.get(self.doc_type, None)
        constituent[UTTERANCE] = head_word.get(UTTERANCE, None)
        constituent[QUOTED] = head_word.get(QUOTED, None)

    @staticmethod
    def _expand_node(terms):
        """ Rebuild the from of a element
        :param terms: The ordered term list of this element
        :return: The form of the element
        """
        text = " ".join([term[FORM] for term in terms])
        return text.strip()

    @staticmethod
    def _expand_node_lemma(terms):
        """ Rebuild the lemma of a element
        :param terms: The ordered term list of this element
        :return: The form of the element
        """
        text = " ".join([term[LEMMA] for term in terms])
        return text.strip()

    def print_tree(self, node):

        if node[self.node_type] == self.word_node_type:
            return " {0}".format(node[FORM])
        else:
            children = " ".join(self.print_tree(x) for x in self.get_syntactic_children_sorted(node))
            return "({0}{1})".format(node.get(POS, node.get(TAG)), children)
