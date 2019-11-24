from unittest import TestCase
from corefgraph import properties

properties.set_lang("es_semeval", "utf-8")

from corefgraph.multisieve.sieves import sieves_by_name
from corefgraph.graph.builder import BaseGraphBuilder


class TestSpanishPronounMatch(TestCase):
    def setUp(self):
        self.sieve = sieves_by_name["RPNM"]({})
        self.sieve.SENTENCE_DISTANCE_LIMIT = False
        self.sieve.UNRELIABLE = False
        self.sieve.INCOMPATIBLE_DISCOURSE = False
        self.sieve.RESTRICT_ADJACENT = False
        self.sieve.graph_builder = BaseGraphBuilder()

    def test_are_coreferent_force_parameters(self):
        mention = self.sieve.graph_builder.add_constituent(
            "C3", None, "NP", 2)
        self.sieve.graph_builder.link_syntax_terminal(
            mention,
            self.sieve.graph_builder.add_word("su", "W3", "suspense", "suspense", "DP3CS0",
                                              (3, 3), 3, 3, None))
        self.sieve.graph_builder.fill_constituent(mention)
        candidate = self.sieve.graph_builder.add_constituent(
            "C1", None, "NP", 2)
        self.sieve.graph_builder.link_syntax_terminal(
            candidate,
            self.sieve.graph_builder.add_word("su", "W1", "su", "su", "DP3CS0",
                                              (1, 1), 1, 1, None))
        self.sieve.graph_builder.fill_constituent(candidate)
        candidate2 = self.sieve.graph_builder.add_constituent(
            "C2", None, "NP", 2)
        self.sieve.graph_builder.link_syntax_terminal(
            candidate2,
            self.sieve.graph_builder.add_word("su", "W1", "su", "su", "DP3CS0",
                                              (1, 1), 1, 1, None))
        self.sieve.graph_builder.link_syntax_terminal(
            candidate2,
            self.sieve.graph_builder.add_word("barco", "W2", "barco", "barco", "NCMS000",
                                              (2, 2), 2, 2, None))
        self.sieve.graph_builder.fill_constituent(candidate2)
        self.assertTrue(
            self.sieve.are_coreferent(
                entity=[mention], mention=mention, candidate_entity=[candidate], candidate=candidate))

        self.sieve.RESTRICT_POSSESSIVES = False
        self.assertTrue(
            self.sieve.are_coreferent(
                entity=[mention], mention=mention, candidate_entity=[candidate], candidate=candidate))

        self.sieve.RESTRICT_POSSESSIVES = True
        self.assertFalse(
            self.sieve.are_coreferent(
                entity=[mention], mention=mention, candidate_entity=[candidate2], candidate=candidate2))

    def test_are_coreferent_base(self):
        mention = self.sieve.graph_builder.add_constituent(
            "C3", None, "NP", 2)

        self.sieve.graph_builder.link_syntax_terminal(
            mention,
            self.sieve.graph_builder.add_word("su", "W3", "suspense", "suspense", "DP3CS0",
                                              (3, 3), 3, 3, None))
        self.sieve.graph_builder.fill_constituent(mention)
        candidate = self.sieve.graph_builder.add_constituent(
            "C1", None, "NP", 1)
        self.sieve.graph_builder.link_syntax_terminal(
            candidate,
            self.sieve.graph_builder.add_word("su", "W1", "su", "su", "DP3CS0",
                                              (1, 1), 1, 1, None))
        self.sieve.graph_builder.fill_constituent(candidate)
        candidate2 = self.sieve.graph_builder.add_constituent(
            "C2", None, "NP", 2)
        self.sieve.graph_builder.link_syntax_terminal(
            candidate2,
            self.sieve.graph_builder.add_word("su", "W1", "su", "su", "DP3CS0",
                                              (1, 1), 1, 1, None))
        self.sieve.graph_builder.link_syntax_terminal(
            candidate2,
            self.sieve.graph_builder.add_word("barco", "W2", "barco", "barco", "NCMS000",
                                              (2, 2), 2, 2, None))
        self.sieve.graph_builder.fill_constituent(candidate2)

        self.assertTrue(
            self.sieve.are_coreferent(
                entity=[mention], mention=mention, candidate_entity=[candidate], candidate=candidate))

        self.assertFalse(
            self.sieve.are_coreferent(
                entity=[mention], mention=mention, candidate_entity=[candidate2], candidate=candidate2))

    def test_are_coreferent_form_trap(self):
        mention = self.sieve.graph_builder.add_constituent(
            "C3", None, "NP", 2)
        self.sieve.graph_builder.link_syntax_terminal(
            mention,
            self.sieve.graph_builder.add_word("su", "W3", "suspense", "suspense", "DP3CS0",
                                              (3, 3), 3, 3, None))
        self.sieve.graph_builder.fill_constituent(mention)
        candidate = self.sieve.graph_builder.add_constituent(
            "C1", None, "NP", 2)
        self.sieve.graph_builder.link_syntax_terminal(
            candidate,
            self.sieve.graph_builder.add_word("suspense", "W2", "suspense", "suspense", "NCMS000",
                                              (2, 2), 2, 2, None))
        self.sieve.graph_builder.fill_constituent(candidate)
        candidate2 = self.sieve.graph_builder.add_constituent(
            "C2", None, "NP", 2)
        self.sieve.graph_builder.link_syntax_terminal(
            candidate2,
            self.sieve.graph_builder.add_word("su", "W1", "su", "su", "DP3CS0",
                                              (1, 1), 1, 1, None))
        self.sieve.graph_builder.link_syntax_terminal(
            candidate2,
            self.sieve.graph_builder.add_word("barco", "W2", "barco", "barco", "NCMS000",
                                              (2, 2), 2, 2, None))
        self.sieve.graph_builder.fill_constituent(candidate2)

        self.assertTrue(
            self.sieve.are_coreferent(
                entity=[mention], mention=mention, candidate_entity=[candidate], candidate=candidate))

        self.assertFalse(
            self.sieve.are_coreferent(
                entity=[mention], mention=mention, candidate_entity=[candidate2], candidate=candidate2))
