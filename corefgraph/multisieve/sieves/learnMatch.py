# coding=utf-8
""" The sieves that check form similarity features.

"""

from logging import getLogger

from corefgraph.constants import POS, FORM, ID
from corefgraph.multisieve.features.constants import APPOSITIVE, ENUMERATION
from corefgraph.multisieve.sieves.base import Sieve
from corefgraph.resources.tagset import pos_tags

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class LearnMatch(Sieve):
    """ Two mentions are coreferent if their surfaces are equals."""
    short_name = "SML"
    auto_load = False
    # Filter options
    ONLY_FIRST_MENTION = False
    NO_PRONOUN_MENTION = False
    NO_STOP_WORDS = False
    DISCOURSE_SALIENCE = False
    BROWN_CLUSTER = "/home/josubg/remote/eval/berkeley-entity-brown/data/ixa-brown-en.txt"
    COINCIDENCE_DISAGREE = "CD"
    COINCIDENCE_AGREE = "CA"
    COINCIDENCE_FAIL = "CF"
    COINCIDENCE_MIXED = "CM"

    def __init__(self, meta_info):
        super(LearnMatch, self).__init__(meta_info)
        self.load_brown(self.BROWN_CLUSTER)

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """ Candidate an primary mention have the same form

        :param graph_builder: The manager to ask or manipulate the graph.
        :param mention: The selected mention to represent the entity.
        :param entity: The entity that mention is part.
        :param candidate: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.
        """

        # Relaxed form match
        relax_match = self.relax_match(candidate, mention)

        mention_enumeration = mention.get(ENUMERATION, False)
        candidate_enumeration = candidate.get(ENUMERATION, False)

        mention_appositive = mention.get(APPOSITIVE, False)
        candidate_appositive = candidate.get(APPOSITIVE, False)

        mention_words = set([
            (word[FORM].lower(), word[POS])
            for word in self.graph_builder.get_words(mention)])
        candidate_words = set([
            (word[FORM].lower(), word[POS])
            for word in self.graph_builder.get_words(candidate)])

        mention_names = 0.0
        mention_adjectives = 0.0
        mention_rest = 0.0
        for word, pos in mention_words:
            if pos_tags.noun(pos):
                mention_names += 1
            elif pos_tags.adjectives(pos):
                mention_adjectives += 1
            else:
                mention_rest += 1

        candidate_names = 0.0
        candidate_adjectives = 0.0
        candidate_rest = 0.0
        for word, pos in candidate_words:
            if pos_tags.noun(pos):
                candidate_names += 1
            elif pos_tags.adjectives(pos):
                candidate_adjectives += 1
            else:
                candidate_rest += 1

        total_names = 0.0
        total_adjectives = 0.0
        total_rest = 0.0
        for word, pos in mention_words.union(candidate_words):
            if pos_tags.noun(pos):
                total_names += 1
            elif pos_tags.adjectives(pos):
                total_adjectives += 1
            else:
                total_rest += 1

        equal_names = 0.0
        equal_adjectives = 0.0
        equal_rest = 0.0
        for word, pos in mention_words.intersection(candidate_words):
            if pos_tags.noun(pos):
                equal_names += 1
            elif pos_tags.adjectives(pos):
                equal_adjectives += 1
            else:
                equal_rest += 1
        equal_names = total_names and (equal_names / total_names)
        equal_adjectives = total_adjectives and (equal_adjectives / total_adjectives)
        equal_rest = total_rest and (equal_rest / total_rest)

        extra_mention_names = 0.0
        extra_mention_adjectives = 0.0
        extra_mention_rest = 0.0
        for word, pos in mention_words.difference(candidate_words):
            if pos_tags.noun(pos):
                extra_mention_names += 1
            elif pos_tags.adjectives(pos):
                extra_mention_adjectives += 1
            else:
                extra_mention_rest += 1
        extra_mention_names = mention_names and (extra_mention_names / mention_names)
        extra_mention_adjectives = mention_adjectives and (extra_mention_adjectives / mention_adjectives)
        extra_mention_rest = mention_rest and (extra_mention_rest / mention_rest)

        extra_candidate_names = 0.0
        extra_candidate_adjectives = 0.0
        extra_candidate_rest = 0.0
        for word, pos in candidate_words.difference(mention_words):
            if pos_tags.noun(pos):
                extra_candidate_names += 1
            elif pos_tags.adjectives(pos):
                extra_candidate_adjectives += 1
            else:
                extra_candidate_rest += 1
        extra_candidate_names = candidate_names and (extra_candidate_names / candidate_names)
        extra_candidate_adjectives = candidate_adjectives and (extra_candidate_adjectives / candidate_adjectives)
        extra_candidate_rest = candidate_rest and (extra_candidate_rest / candidate_rest)

        mention_entity_id = mention.get("Gold_mention_id", "#X").split("#")[0]
        candidate_entity_id = candidate.get("Gold_mention_id", "#X").split("#")[0]
        sentence_distance = self.graph_builder.sentence_distance(mention, candidate)
        brown_difference = self.brown_distance(
            mention_words=[word[FORM] for word in self.graph_builder.get_words(mention)],
            candidate_words=[word[FORM] for word in self.graph_builder.get_words(candidate)])

        linked = mention_entity_id == candidate_entity_id != "X"
        row = [relax_match, mention_enumeration, candidate_enumeration, mention_appositive, candidate_appositive,
               equal_names, equal_adjectives, equal_rest, extra_mention_names, extra_mention_adjectives,
               extra_mention_rest, extra_candidate_names, extra_candidate_adjectives, extra_candidate_rest,
               mention[FORM], candidate[FORM], sentence_distance]

        for key in self.classes:
            row.append(brown_difference.get(key,0))
        row.append(linked)

        try:
            mention["surface_learn"][candidate[ID]] = row
        except KeyError:
            mention["surface_learn"] = {candidate[ID]: row}
        return False

    def brown_distance(self, mention_words, candidate_words):
        brown_vector = {}
        mention_brown_clusters = [self.brown_class(word) for word in mention_words]
        for word in candidate_words:
            brown = self.brown_class(word)
            result = ""
            if brown in mention_brown_clusters:
                if word in mention_words:
                    result = self.COINCIDENCE_AGREE
                else:
                    result = self.COINCIDENCE_DISAGREE
            else:
                result = self.COINCIDENCE_FAIL
            if result == brown_vector.get(brown, result):
                brown_vector[brown] = result
            else:
                brown_vector[brown] += result
        return brown_vector

    def brown_class(self, word):
        return self.brown.get(word, "0")

    def load_brown(self, path):
        self.brown = dict()
        for line in open(path):
            tokens = line.split("\t")
            self.brown[tokens[0]] = format(int("1" + tokens[1], 2),"x")
        self.classes = set(self.brown.values())

    def relax_match(self, candidate, mention):
        candidate_relaxed_form = self.relaxed_form(candidate)
        mention_relaxed_form = self.relaxed_form(mention)

        if candidate_relaxed_form == "":
            self.logger.debug("FILTERED LINK Empty relaxed form")
            self.meta["Filtered_relaxed_form_empty"] += 1
            return False
        if mention_relaxed_form == "":
            self.logger.debug("FILTERED LINK Empty relaxed form")
            self.meta["Filtered_relaxed_form_empty"] += 1
            return False
        if (mention_relaxed_form == candidate_relaxed_form) or \
                (mention_relaxed_form + " 's" == candidate_relaxed_form) or \
                (mention_relaxed_form == candidate_relaxed_form + " 's"):
            self.logger.debug("Linked")
            self.meta["linked"] += 1
            return True
        return False
