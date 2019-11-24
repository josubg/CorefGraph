
from corefgraph.constants import ID, SPAN, TAG
from corefgraph.resources.tagset import constituent_tags


class Plain:

    def __init__(self, graph_builder):
        self.graph_builder = graph_builder

    def extract(self, order, root, validation, named_entities_by_constituent, gold_mentions_by_constituent):
        """Extract the validated candidates from the sentence but use restarts search for each root children.

           :param order: A list where put the extracted constituents/Named Entities
           :param root: The chunk where each element must be traversed.
           :param validation: The function that validates de constituent.
           :param named_entities_by_constituent: The named entities ordered by constituent.
           :param gold_mentions_by_constituent: The gold mentions ordered by constituent.
           """
        ordered_children = sorted(self.graph_builder.get_syntactic_children_sorted(root),
                                  key=lambda child: child[SPAN])
        # # Visit each constituent in a BFT algorithm
        self._extract_mentions(
            order, ordered_children, validation, named_entities_by_constituent, gold_mentions_by_constituent)


class Preference:

    def __init__(self, graph_builder):
        self.graph_builder = graph_builder

    def extract(self, order, root, validation, named_entities_by_constituent, gold_mentions_by_constituent):
        """Extract the validated candidates from the sentence but use restarts search for each root children.

           :param order: A list where put the extracted constituents/Named Entities
           :param root: The chunk where each element must be traversed.
           :param validation: The function that validates de constituent.
           :param named_entities_by_constituent: The named entities ordered by constituent.
           :param gold_mentions_by_constituent: The gold mentions ordered by constituent.
           """
        children = self.graph_builder.get_syntactic_children_sorted(root)

        ordered_children = [c for c in children if constituent_tags.noun_phrase(c.get("tag",""))]

        # # Visit each constituent in a BFT algorithm
        self._extract_mentions(
            order, ordered_children, validation, named_entities_by_constituent, gold_mentions_by_constituent)

        ordered_children = [c for c in children if not constituent_tags.noun_phrase(c.get("tag",""))]

        self._extract_mentions(
            order, ordered_children, validation, named_entities_by_constituent)


class PerChild:

    def __init__(self, graph_builder):
        self.graph_builder = graph_builder

    def extract(self, order, root, validation, named_entities_by_constituent, gold_mentions_by_constituent):
        """Extract the validated candidates from the sentence.

           :param order: A list where put the extracted constituents/Named Entities
           :param root: The chunk where each element must be traversed.
           :param validation: The function that validates de constituent.
           :param named_entities_by_constituent: The named entities ordered by constituent.
           :param gold_mentions_by_constituent: The gold mentions ordered by constituent.
           """
        ordered_children = sorted(self.graph_builder.get_syntactic_children_sorted(root),
                                  key=lambda child: child[SPAN])
        # Visit each constituent in a BFT algorithm
        for constituent in ordered_children:
            self._extract_mentions(
                order, [constituent], validation, named_entities_by_constituent, gold_mentions_by_constituent)


class Breadth:

    def __init__(self, graph_builder):
        self.graph_builder = graph_builder

    SUBORDINATE_RESTART = False

    def _extract_mentions(self, order, nodes, validation, named_entities_by_constituent, gold_mentions_by_constituent):
        """The constituent syntax graph is traversed in breadth-first order. Each element(constituent or word) is
        evaluated and (if is found valid) added with is coreference candidates to the candidature tuple.

        :param order: A list where put the extracted constituents/Named Entities
        :param nodes: A list of nodes to starts with.
        :param validation: The function that validates de constituent.
        :param named_entities_by_constituent: The named entities ordered by constituent.
        :param gold_mentions_by_constituent: The gold mentions ordered by constituent.
        """
        # Process all the nodes
        while nodes:
            # Extract the first candidate
            node = nodes.pop(0)
            # Constituents Gold mentions
            for gold in gold_mentions_by_constituent.get(node[ID], []):
                # check if is an accepted mention
                if validation(gold, order):
                    # Add it to the order
                    order.append(gold)
            # Search in the constituent named entities
            for ner in named_entities_by_constituent.get(node[ID], []):
                # check the entity
                if validation(ner, order):
                    order.append(ner)
            # Check the Constituents or word
            if validation(node, order):
                order.append(node)
            # Order the children of the nodes
            if self.SUBORDINATE_RESTART and constituent_tags.clause(node.get(TAG)):
                self.extract(order, node, validation, named_entities_by_constituent, gold_mentions_by_constituent)
            else:
                # Order the children of the nodes
                ordered_children = sorted(
                    self.graph_builder.get_syntactic_children_sorted(node),
                    key=lambda child: child[SPAN])
                # Add the children to the search
                nodes.extend(ordered_children)


class Deep:

    SUBORDINATE_RESTART = False

    def _extract_mentions(self, order, nodes, validation, named_entities_by_constituent, gold_mentions_by_constituent):
        """The constituent syntax graph is traversed in deep-first order but restart search in subordinates.
        Each element(constituent or word) is evaluated and (if is found valid) added with is coreference candidates to
        the candidature tuple.

        :param order: A list where put the extracted constituents/Named Entities
        :param nodes: A list of nodes to starts with.
        :param validation: The function that validates de constituent.
        :param named_entities_by_constituent: The named entities ordered by constituent.
        :param gold_mentions_by_constituent: The gold mentions ordered by constituent.
        """
        # The ordered nodes of the constituent tha can be candidates

        # Process all the nodes
        while nodes:
            # Extract the first candidate
            node = nodes.pop(0)
            # Constituents Gold mentions
            for gold in gold_mentions_by_constituent.get(node[ID], []):
                # check if is an accepted mention
                if validation(gold, order):
                    # Add it to the order
                    order.append(gold)
            # constituent entities
            # Fetch constituents NES
            for ner in named_entities_by_constituent.get(node[ID], []):
                # check if is an accepted mention
                if validation(ner, order):
                    # Add it to the order
                    order.append(ner)
            # Constituents and words
            # check if is an accepted mention
            if validation(node, order):
                # add it to the order
                order.append(node)
            # Are clause  traversed in same way as roots?
            if self.SUBORDINATE_RESTART and constituent_tags.clause(node.get(TAG)):
                # start a new search for the clause
                self.extract(order, node, validation, named_entities_by_constituent, gold_mentions_by_constituent)
            else:
                # Order the children of the nodes
                ordered_children = self.graph_builder.get_syntactic_children_sorted(node)
                # Add the children to the search
                nodes = ordered_children + nodes


class BreathFistSimple(Plain, Breadth):
    name = "breadth_first"


class BreathFistPreference(Preference, Breadth):
    name = "breadth_first_preference"


class BreadthFirstSubordinate(Plain, Breadth):
    SUBORDINATE_RESTART = True
    name = "breadth_first_subordinate"


class BreathFistPerChild(PerChild, Breadth):
    name = "breadth_first_per_child"


class BreadthFirstPerChildSubordinate(PerChild, Breadth):
    SUBORDINATE_RESTART = True
    name = "breadth_first_per_child_subordinate"


class DeepFirstSimple(Plain, Deep):
    name = "deep_first"
