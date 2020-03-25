# coding=utf-8
""" This is where the base of the sieves lives

"""

from collections import Counter
from logging import getLogger

from corefgraph.constants import SPAN, ID, FORM, UTTERANCE, POS, NER, SPEAKER, CONSTITUENT, TAG, GOLD
from corefgraph.resources.dictionaries import pronouns, stopwords
from corefgraph.resources.rules import rules
from corefgraph.resources.tagset import ner_tags, constituent_tags
from corefgraph.resources.tagset import pos_tags
from corefgraph.multisieve.features.constants import UNKNOWN, PERSON, FIRST_PERSON, SECOND_PERSON, GENERIC, \
    STARTED_BY_INDEFINITE_PRONOUN, APPOSITIVE, PREDICATIVE_NOMINATIVE, MENTION, PROPER_MENTION, NOMINAL_MENTION, \
    PRONOUN_MENTION, STARTED_BY_INDEFINITE_ARTICLE, NUMBER, ANIMACY, GENDER, ENUMERATION_MENTION

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class Sieve(object):
    """ The base of all the sieves of the system. It contains all the check,
    resolve and merge basic mechanics and also the methods to extract
    information from entities and candidates.

    """
    short_name = "base"
    auto_load = True

    # Filter options
    DISCOURSE_SALIENCE = True
    ONLY_FIRST_MENTION = True
    USE_INCOMPATIBLES = True
    NO_PRONOUN_MENTION = True
    NO_ENUMERATION_MENTION = False
    NO_APPOSITIVE_MENTION = False
    NO_PRONOUN_CANDIDATE = False
    NO_ENUMERATION_CANDIDATE = False
    NO_APPOSITIVE_CANDIDATE = False
    NO_STOP_WORDS = False
    INCOMPATIBLE_DISCOURSE = False
    SENTENCE_DISTANCE_LIMIT = False
    I_WITHIN_I = False
    NO_SUBJECT_OBJECT = False
    IS_INSIDE = True
    gold_check = True

    UNKNOWN_VALUES = {UNKNOWN, None, }
    INCOMPATIBLES = "incompatible"

    UNRELIABLE = 3

    def __init__(self, meta_info):
        self.meta = Counter()
        self.logger = getLogger(__name__ + "." + self.short_name)
        self.meta_info = meta_info

        self.correct_link = []
        self.wrong_link = []
        self.lost_link = []
        self.no_link = []

        self.graph_builder = None

    def get_meta(self):
        return {
            "OK": self.correct_link,
            "WRONG": self.wrong_link,
            "LOST": self.lost_link,
            "NO": self.no_link,
        }

    def resolve(self, graph_builder, mentions_order, candidates_order):
        """Runs each sentence compare each mention and its candidates.

        :param graph_builder: The manager to ask or manipulate the graph.
        :param candidates_order: A list sentences that are a list of mentions in BFS.
        :param mentions_order: A list sentences that are a list of mentions in textual order.
        """
        STOP = 'nter439'
        self.graph_builder = graph_builder
        output_clusters = dict()
        self.logger.info(
            "SIEVE: =========== %s Start ===========", self.short_name)
        # for each sentence for each mention in tree traversal order
        for index_sentence, sentence in enumerate(mentions_order):
            for index_mention, mention in enumerate(sentence):
                self.logger.debug("RESOLVE: ---------- New mention ----------")
                self.log_mention(mention)
                # Skip the mention?
                mention_entity_idx, mention_entity = mention.get("entity")
                if not self.validate(mention=mention, entity=mention_entity):
                    self.logger.debug("RESOLVE: Invalid mention")
                else:
                    candidates = self.get_candidates(
                        mentions_order, candidates_order, mention, index_sentence)
                    for candidate in candidates:
                        self.logger.debug("RESOLVE: +++++ New Candidate +++++")
                        self.log_candidate(candidate)
                        candidate_entity_idx, candidate_entity = \
                            candidate.get("entity")

                        if self.are_coreferent(
                                entity=mention_entity, mention=mention,
                                candidate_entity=candidate_entity, candidate=candidate):
                            if self.meta_info:
                                if self.check_gold(mention, candidate):
                                    self.logger.info(
                                        "CORRECT LINK (%s):%s ", self.short_name,
                                        self.context(
                                            mention_entity, mention,
                                            candidate_entity, candidate))
                                    self.correct_link.append(
                                        (mention[ID], candidate[ID]))
                                else:
                                    self.logger.debug(
                                        "WRONG LINK (%s):%s ", self.short_name,
                                        self.context(
                                            mention_entity, mention,
                                            candidate_entity, candidate))
                                    self.wrong_link.append(
                                        (mention[ID], candidate[ID]))
                            try:
                                del output_clusters[mention_entity_idx]
                            except KeyError:
                                pass
                            # If passed the sieve link candidate and stop search
                            # for that entity
                            try:
                                del output_clusters[candidate_entity_idx]
                            except KeyError:
                                pass
                            self.logger.debug("RESOLVE: End candidate (LINKED).")
                            mention_entity_idx, mention_entity = self._merge(
                                mention_entity, candidate_entity)
                            break
                        else:
                            if self.meta_info:
                                if self.check_gold(mention, candidate):
                                    if not self.check_in_entity(candidate, mention_entity):
                                        self.logger.debug(
                                            "LOST LINK(%s):%s ", self.short_name,
                                            self.context(
                                                mention_entity, mention,
                                                candidate_entity, candidate))
                                        self.lost_link.append(
                                            (mention[ID], candidate[ID]))
                                else:
                                    self.no_link.append((mention[ID], candidate[ID],))
                        self.logger.debug("RESOLVE: End candidate(Not linked).")
                self.logger.debug("RESOLVE: End mention.")
                output_clusters[mention_entity_idx] = mention_entity
        return output_clusters

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """ Determine if the candidate is a valid entity coreferent.

        :param candidate: The candidate to be part of the entity.
        :param mention: The selected mention to represent the entity.
        :param candidate_entity: The entity of the candidate mention.
        :param entity: The entity that is going to be evaluated.
        """
        self.meta["asked"] += 1
        if mention.get("invalid") or candidate.get("invalid"):
            return False
        if self.USE_INCOMPATIBLES:
            for c_mention in candidate_entity:
                if c_mention[ID] in mention.get(self.INCOMPATIBLES, ()):
                    self.meta["filter_incompatible"] += 1
                    self.logger.debug(
                        "LINK FILTERED incompatible mentions inside entities.")
                    return False

        if self.SENTENCE_DISTANCE_LIMIT:
            sentence_distance = self.graph_builder.sentence_distance(
                mention, candidate)
            if sentence_distance > self.SENTENCE_DISTANCE_LIMIT \
                    and not (mention.get(PERSON) in (FIRST_PERSON, SECOND_PERSON)):
                self.meta["filter_to_far"] += 1
                self.logger.debug(
                    "LINK FILTERED Candidate to far and not I or You.")
                return False
        if self.UNRELIABLE and (stopwords.unreliable(mention[FORM].lower())) and \
                (self.graph_builder.sentence_distance(
                    element_a=mention, element_b=candidate) > self.UNRELIABLE):
            self.meta["filter_to_far_this"] += 1
            self.logger.debug("LINK FILTERED too far this. Candidate")
            return False

        if self.check_in_entity(mention=candidate, entity=entity):
            self.meta["filter_already_linked"] += 1
            self.logger.debug("LINK FILTERED already linked. Candidate")
            return False
        if candidate.get(GENERIC, False) and candidate.get(PERSON) == SECOND_PERSON:
            self.meta["filter_generic_candidate"] += 1
            self.logger.debug("LINK FILTERED Generic Candidate")
            return False

        if self.IS_INSIDE and (self.graph_builder.is_inside(mention[SPAN],  candidate[SPAN]) or
                               self.graph_builder.is_inside(candidate[SPAN], mention[SPAN])):
            self.meta["filtered_inside"] += 1
            self.logger.debug("LINK FILTERED Inside. Candidate")
            return False
        if self.INCOMPATIBLE_DISCOURSE and \
                self.incompatible_discourse(
                    entity_a=candidate_entity, entity_b=entity):
            self.meta["filtered_discourse"] += 1
            self.logger.debug("LINK FILTERED incompatible discourse")
            return False
        representative_mention = self.entity_representative_mention(entity)
        if self.NO_SUBJECT_OBJECT and \
                self.subject_object(candidate_entity, entity):
            self.meta["filtered_subject_object"] += 1
            self.logger.debug("LINK FILTERED Subject-object")
            self.invalid(
                entity_a=entity, mention_a=mention,
                entity_b=candidate_entity, mention_b=candidate)
            return False
        if self.I_WITHIN_I and \
                self.i_within_i(
                    mention_a=representative_mention, mention_b=candidate):
            self.meta["filtered_i_within_i"] += 1
            self.logger.debug(
                "LINK FILTERED I within I construction: %s", candidate[FORM])
            self.invalid(
                entity_a=entity, mention_a=mention,
                entity_b=candidate_entity, mention_b=candidate)
            return False

        if self.NO_PRONOUN_CANDIDATE and self.is_pronoun(candidate):
            self.logger.debug("FILTERED LINK mention pronoun")
            self.meta["Filtered_mention_pronoun"] += 1
            return False
        self.meta["First pass"] += 1

        if self.NO_ENUMERATION_CANDIDATE and candidate[MENTION] == ENUMERATION_MENTION:
            self.logger.debug("FILTERED LINK candidate enumeration")
            self.meta["Filtered_enumeration"] += 1
            return False
        if self.NO_APPOSITIVE_CANDIDATE and candidate.get(APPOSITIVE, False):
            self.logger.debug("FILTERED LINK candidate appositive")
            self.meta["mention_filtered_enumeration"] += 1
            return False
        return True

    def validate(self, mention, entity):
        """ Determine if the mention is valid for this sieve.

        :param mention: The mention to check.
        :param entity: The entity of the mention.
        """
        if self.DISCOURSE_SALIENCE and \
                not self.discourse_salience(mention=mention):
            return False
        # Filter all no first mentions
        if self.ONLY_FIRST_MENTION and \
                not self.first_mention(mention=mention, entity=entity):
            self.meta["mention_filtered_no_first"] += 1
            self.logger.debug(
                "MENTION FILTERED: Not first one: %s", mention[FORM])
            return False
        # Filter Narrative you
        if self.narrative_you(mention=mention):
            self.meta["mention_filtered_narrative_you"] += 1
            self.logger.debug(
                "MENTION FILTERED: is a narrative you: %s", mention[FORM])
            return False
        # filter generics
        if mention.get(GENERIC, False):
            self.meta["mention_filtered_generic"] += 1
            self.logger.debug(
                "MENTION FILTERED: is generic: %s", mention[FORM])
            return False
        # Filter stopWords
        if self.NO_STOP_WORDS and stopwords.stop_words(mention[FORM].lower()):
            self.meta["mention_filtered_stop_word"] += 1
            self.logger.debug(
                "MENTION FILTERED: is a stop word: %s", mention[FORM])
            return False
        # Filter all pronouns
        if self.NO_PRONOUN_MENTION and self.is_pronoun(mention):
            self.meta["mention_filtered_pronoun"] += 1
            self.logger.debug(
                "MENTION FILTERED: Is a pronoun: %s", mention[FORM])
            return False
        if self.NO_ENUMERATION_MENTION and mention[MENTION] == ENUMERATION_MENTION:
            self.logger.debug("MENTION FILTERED enumeration form")
            self.meta["mention_filtered_enumeration"] += 1
            return False
        if self.NO_APPOSITIVE_MENTION and mention.get(APPOSITIVE, False):
            self.logger.debug("MENTION FILTERED APPOSITIVE form")
            self.meta["mention_filtered_enumeration"] += 1
            return False
        return True

    def discourse_salience(self, mention):
        """ Determine if a mention is relevant by its discourse salience.

        :param mention:  The mention to check discourse salience
        :return: True if is relevant mention
        """

        # If starts with, or is, a undefined pronouns, Filter it.
        if mention[STARTED_BY_INDEFINITE_PRONOUN]:
            self.logger.debug(
                "MENTION FILTERED: is undefined: %s", mention[FORM])
            self.meta["mention_filtered_is_undefined"] += 1
            return False
        # If start with indefinite article and isn't part of an appositive or
        # predicative-nominative constructions filter it.
        if not mention.get(APPOSITIVE, False) and not mention.get(PREDICATIVE_NOMINATIVE, False) and \
                self.is_undefined(mention=mention):
            self.meta["mention_filtered_starts_undefined"] += 1
            self.logger.debug(
                "MENTION FILTERED: starts with undefined: %s", mention[FORM])
            return False
        return True

    def first_mention(self, mention, entity):
        """ Check if the mention is the first no pronoun mention with discourse
        salience of the cluster.

        :param mention: The mention to check.
        :param entity:  The entity of the mention.
        :return: True or False
        """
        for m in entity:
            if self.is_pronoun(m):
                continue
            if not self.discourse_salience(m):
                continue
            if m[ID] == mention[ID]:
                return True
            return False
        return entity[0][ID] == mention[ID]

    def get_candidates(self, text_order, candidate_order, mention, index_sent):
        """ Gets the candidates ordered for the sieve check. This function is
        made for the need of reorder candidates in the sieve X. Also, another
        sieves may benefit form this in the future.

        :param text_order: The list of sentences that contain the list of mentions that form the text.
        :param candidate_order: The list of sentences that contain the list of mentions that form the text in bts order.
        :param mention: The mention whose candidates whe need.
        :param index_sent: The index of the current sentence.

        @rtype : list
        :return: A list of ordered candidates.
        """
        index_mention = [c[ID] for c in candidate_order[index_sent]].index(mention["id"])
        return candidate_order[index_sent][:index_mention] + [m for s in reversed(text_order[:index_sent]) for m in s]

    def invalid(self, entity_a, mention_a, entity_b, mention_b):
        """ Set the two mentions invalid for each other.

        :param entity_a: Entity of the mention.
        :param mention_a: One of the mentions.
        :param entity_b: Entity of the other mention.
        :param mention_b: The other mention.
        :return:
        """
        if self.gold_check:
            if self.check_gold(mention_a, mention_b):
                self.logger.debug(
                    "WRONG BLACKLISTED: %s",
                    self.context(entity_a, mention_a, entity_b, mention_b))
            else:
                self.logger.debug(
                    "CORRECT BLACKLISTED: %s",
                    self.context(entity_a, mention_a, entity_b, mention_b))
        else:
            self.logger.debug("BLACKLISTED")
        try:
            mention_a[self.INCOMPATIBLES].add(mention_b[ID])
        except KeyError:
            mention_a[self.INCOMPATIBLES] = {mention_b[ID]}
        try:
            mention_b[self.INCOMPATIBLES].add(mention_a[ID])
        except KeyError:
            mention_b[self.INCOMPATIBLES] = {mention_a[ID]}

    def _merge(self, entity_a, entity_b):
        """ Merge two entities into new one.

        :param entity_a: a entity to merge
        :param entity_b: a entity to merge
        """
        # Add the new mentions to first cluster
        entity = list(sorted(
            entity_a + entity_b, key=lambda x: x[SPAN],))
        incompatibles = set()
        for mention in entity:
            incompatibles.update(mention.get(self.INCOMPATIBLES, set()))
        idx = entity[0][SPAN]
        for mention in entity:
            mention["entity"] = (idx, entity)
            mention[self.INCOMPATIBLES] = incompatibles
        return idx, entity

    @staticmethod
    def entity_representative_mention(entity):
        """ Get the most representative mention of the entity.

        :param entity: The entity of which representative mention is fetched.
        """
        for mention in entity:
            if mention.get(MENTION) == PROPER_MENTION:
                return mention
        for mention in entity:
            if mention.get(MENTION) == NOMINAL_MENTION:
                return mention
        for mention in entity:
            if mention.get(MENTION) == PRONOUN_MENTION:
                return mention
        return entity[0]

    def entity_property(self, entity, property_name):
        """ Get a combined property of the values of all mentions of the entity

        :param property_name: The name of the property to fetch.
        :param entity: The entity of which property is fetched.
        """
        combined_property = set(
            (mention.get(property_name, UNKNOWN) for mention in entity))
        if len(combined_property) > 1:
            combined_property = combined_property.difference(
                self.UNKNOWN_VALUES)
        if len(combined_property) == 0:
            combined_property.add(UNKNOWN)
        return combined_property

    @staticmethod
    def entity_ne(entity):
        """ Get a combined NE of the values of all mentions of the entity.
        Other and no NER tags are cleared. If no NE tag is found None is
        returned.

        :param entity: The entity of which NE is fetched.
        """
        combined_property = set(
            (mention.get(NER, None) for mention in entity))
        combined_property = filter(
            lambda x: ner_tags.mention_ner(x), combined_property)
        if len(combined_property) == 0:
            return set()
        return set(combined_property)

    def narrative_you(self, mention):
        """The mention is second person(YOU) or the narrator(PER0) in an article.

        :param mention: The mention to check.
        """
        return \
            mention[self.graph_builder.doc_type] == \
            self.graph_builder.doc_article and\
            mention.get(SPEAKER, False) == "PER0" and \
            mention.get(PERSON) == SECOND_PERSON

    @staticmethod
    def is_pronoun(mention):
        """ The mentions is a pronoun mention?

        :param mention: The mention to check.
        """
        return (mention.get(MENTION) == PRONOUN_MENTION) or \
            pronouns.all(mention[FORM])

    @staticmethod
    def is_undefined(mention):
        """ The mentions is an undefined mention?

        :param mention: The mention to check.
        """
        return mention[STARTED_BY_INDEFINITE_PRONOUN] or \
            mention[STARTED_BY_INDEFINITE_ARTICLE]

    @staticmethod
    def is_location(mention):
        """ The mentions is a location?

        :param mention: The mention to check.
        """
        return ner_tags.location(mention.get(NER))

    def agree_attributes(self, entity, candidate_entity):
        """ All attributes are compatible. Its mean the attributes of each are
        a subset one of the another.

        :param entity: Entity of the mention
        :param candidate_entity: Entity of the candidate
        :return: True or False
        """
        candidate_gender = self.entity_property(candidate_entity, GENDER)
        entity_gender = self.entity_property(entity, GENDER)
        if not (self.UNKNOWN_VALUES.intersection(entity_gender) or
                self.UNKNOWN_VALUES.intersection(candidate_gender)):
            if candidate_gender.difference(entity_gender) \
                    and entity_gender.difference(candidate_gender):
                self.logger.debug(
                    "Gender disagree %s %s",
                    entity_gender, candidate_gender)
                return False

        candidate_number = self.entity_property(candidate_entity, NUMBER)
        entity_number = self.entity_property(entity, NUMBER)
        if not(self.UNKNOWN_VALUES.intersection(entity_number) or
                self.UNKNOWN_VALUES.intersection(candidate_number)):
            if candidate_number.difference(entity_number) \
                    and entity_number.difference(candidate_number):
                self.logger.debug(
                    "Number disagree %s %s",
                    entity_number, candidate_number)
                return False

        candidate_animacy = self.entity_property(candidate_entity, ANIMACY)
        entity_animacy = self.entity_property(entity, ANIMACY)
        if not(self.UNKNOWN_VALUES.intersection(entity_animacy) or
                self.UNKNOWN_VALUES.intersection(candidate_animacy)):
            if candidate_animacy.difference(entity_animacy) \
                    and entity_animacy.difference(candidate_animacy):
                self.logger.debug(
                    "Animacy disagree %s %s",
                    entity_animacy, candidate_animacy)
                return False

        candidate_ner = self.entity_ne(candidate_entity)
        entity_ner = self.entity_ne(entity)
        if not(entity_ner is None or candidate_ner is None):
            if candidate_ner.difference(entity_ner) and \
                    entity_ner.difference(candidate_ner):
                self.logger.debug(
                    "NER disagree %s %s",
                    entity_ner, candidate_ner)
                return False
        return True

    def subject_object(self, entity_a, entity_b):
        """ Check if entities are linked by any subject-object relation.

        :param entity_a: An entity to check
        :param entity_b: An entity to check
        :return: True or False
        """
        if entity_a[0]["doc_type"] != "article":
            return False
        for mention_a in entity_a:
            for mention_b in entity_b:
                if self.graph_builder.sentence_distance(
                        mention_a,  mention_b) > 0:
                    continue
                if mention_a.get("subject", False) and \
                        mention_b.get("object", False) and \
                        mention_a["subject"] == mention_b["object"]:
                    return True
                if mention_b.get("subject", False) and \
                        mention_a.get("object", False) and \
                        mention_b["subject"] == mention_a["object"]:
                    return True
                pass
        return False

    def i_within_i(self, mention_a, mention_b):
        """ Check if the  mention and candidate are in a i-within-i
        construction.

        :param mention_a: a mention
        :param mention_b: another mention
        """
        if not self.graph_builder.same_sentence(mention_a, mention_b):
            return False
        # Aren't appositive
        if mention_a.get(APPOSITIVE, False) and mention_b.get(APPOSITIVE, False):
            return False
        # Aren't Relative pronouns
        if rules.is_relative_pronoun(self.graph_builder, mention_b, mention_a) or \
                rules.is_relative_pronoun(self.graph_builder, mention_a, mention_b):
            return False
        # One is included in the other
        if self.graph_builder.is_inside(mention_a[SPAN], mention_b[SPAN]) \
                or self.graph_builder.is_inside(
                    mention_b[SPAN], mention_a[SPAN]):
            return True
        return False

    def relaxed_form_word(self, mention):
        """ Return the words of the mention without the words after the head
         word.

        :param mention: The mention where the words are extracted.
        :return: a list of words.
        """
        mention_words = self.graph_builder.get_words(mention)
        mention_head = self.graph_builder.get_head_word(mention)
        head = False
        for index, word in enumerate(mention_words):
            word_pos = word[POS]
            if word[ID] == mention_head[ID]:
                head = True
            if head and pos_tags.relative_pronoun(word_pos):
                return [word for word in mention_words[:index]]
            # TODO CHANGE TO CLAUSE CONNECTORS
            if head and word[FORM] == ",":
                return [word for word in mention_words[:index]]
        return [word for word in mention_words]

    def relaxed_form(self, mention):
        """ Return the form of the mention without the words after the head
         word. The form is lowered and all words are space separated.

        :param mention: The mention where the words are extracted.
        :return: a string of word forms separated by spaces.
        """
        return " ".join(word[FORM] for word in self.relaxed_form_word(mention=mention)).lower()

    def same_speaker(self, mention_a, mention_b):
        """ Check if mention refer to the same speaker.

        :param mention_a: a mention
        :param mention_b: another mention
        :return type: Bool
        """
        speaker_a = mention_a.get(SPEAKER, False)
        speaker_b = mention_b.get(SPEAKER, False)
        if not(speaker_a and speaker_b):
            return False
        if speaker_a == speaker_b:
            return True
        # Two speakers are the same string
        if type(speaker_a) == str and\
                type(speaker_b) == str and \
                speaker_a == speaker_b:
            return True
        # Speaker A is B head word
        if self._check_speaker(speaker_a, mention_b):
            return True
        # Speaker B is A head word
        if self._check_speaker(speaker_b, mention_a):
            return True
        return False

    def _check_speaker(self, speaker, mention):
        """ Is the mention a form of the speaker.
        :param speaker:
        :param mention:
        :return:
        """

        # the speaker may be a string or another mention
        if not (type(speaker) is str):
            speaker = speaker[FORM]

        mention_head_form = self.graph_builder.get_head_word(mention)[FORM]
        if mention_head_form == speaker:
            return True
        for speaker_token in speaker.split():
            if speaker_token == mention_head_form:
                return True
        return False

    def are_speaker_speech(self, speaker, speech):
        """ Tho mention are in a speaker speech relation?

        :param speaker: The mention that is a speaker
        :param speech: The mention that is inside a speech.
        :return: True or False
        """
        speech_speaker = speech.get(SPEAKER, False)
        # TODO check this Only heads??
        if type(speech_speaker) is dict:
            speaker_words_ids = [
                word[ID]
                for word in self.graph_builder.get_words(speaker)]
            return speech_speaker[ID] in speaker_words_ids
        else:
            speaker_head_word = rules.get_head_word_form(self.graph_builder, speaker)\
                .lower()
            for word in speech_speaker.split(" "):
                if word.lower() == speaker_head_word:
                    return True
        return False

    def incompatible_discourse(self, entity_a, entity_b):
        """ Check if two entities have any incompatible mentions between them.

        :param entity_a: A entity
        :param entity_b: Another entity
        :return: Return True if the entities are incompatible.
        """
        for mention_a in entity_a:
            doc_type = entity_b[0][self.graph_builder.doc_type]
            mention_a_person = mention_a.get(PERSON)
            for mention_b in entity_b:
                mention_b_person = mention_b.get(PERSON)
                if (self.are_speaker_speech(
                        speaker=mention_a, speech=mention_b) or
                        self.are_speaker_speech(
                            speaker=mention_b, speech=mention_a)
                    ) and not (
                        mention_a_person == FIRST_PERSON and
                        mention_b_person == FIRST_PERSON):
                    return True
                if doc_type == self.graph_builder.doc_article:
                    continue
                distance = abs(mention_a[UTTERANCE] - mention_b[UTTERANCE])
                if distance == 1 and \
                        not self.same_speaker(mention_a, mention_b):
                    if mention_a_person != mention_b_person:
                        if mention_b_person == FIRST_PERSON:
                            return True
                        if mention_b_person == SECOND_PERSON:
                            return True
        return False

    @staticmethod
    def check_gold(mention, candidate):
        """ Check if the link is in the gold Standard.

        :param mention: The mention which link want to check.
        :param candidate: The candidate of the link.
        :return: True or False depends of the veracity
        """

        # mention_id = mention.get(SPAN, "")
        # candidate_id = candidate.get(ID, "")
        mention_id = mention.get(GOLD, {ID: mention[ID]}).get(ID)
        candidate_id = candidate.get(GOLD, {ID: candidate[ID]}).get(ID)
        if "#" not in mention_id or "#" not in candidate_id:
            return False
        mention_entity_id = mention_id.split("#")[0]
        candidate_entity_id = candidate_id.split("#")[0]
        return mention_entity_id == candidate_entity_id

    def log_mention(self, mention):
        """ The function that log the mention and all useful info for this sieve
        coreference resolution

        :param mention: The mention to show
        """
        self.logger.debug("MENTION -%s- %s", mention[FORM], mention[SPAN])

    def log_candidate(self, candidate):
        """ The function that show the candidate of a link and all the relevant
        info for the linking process.

        :param candidate:
        """
        self.logger.debug(
            "CANDIDATE -%s- %s",
            candidate[FORM], candidate[SPAN])

    def context(self, mention_entity, mention, candidate_entity, candidate):
        """ Return a Human readable and sieve specific info string of the
        mention, the candidate and the link for logging proposes.

        :param mention_entity: The entity of the linked mention.
        :param mention: The mention.
        :param candidate_entity: The candidate entity
        :param candidate: The candidate of the link
        :return A ready to read string.
        """
        return "{0} -{1}- | {2} -{3}-".format(
            mention[FORM], self.graph_builder.get_root(mention)[FORM],
            candidate[FORM], self.graph_builder.get_root(candidate)[FORM])

    @staticmethod
    def check_in_entity(mention, entity):
        """ Check if the mention is part of the entity.

        :param entity: entity where check.
        :param mention: The mention to find.
        :return True or False.
        """
        return mention[ID] in [m[ID] for m in entity]


class PronounSieve(Sieve):
    def pronoun_order(self, sentence_candidates, mention):
        """ Reorder the candidates that are in the same sentence of the mention
        for pronoun sieve coreference resolution.

        :param sentence_candidates: The candidates for coreference that appears in the same sentence
            of the main mention.
        :param mention: The main mention whose coreference is been checking.
        :return: The sentence candidates ordered for coreference pronoun resolution.
        """
        reordered = []
        reordered_ids = []
        current = mention.get(CONSTITUENT, mention)
        root_id = self.graph_builder.get_root(current)[ID]
        while current[ID] != root_id:
            current = self.graph_builder.get_syntactic_parent(current)
            if constituent_tags.clause(current.get(TAG)):
                for mention_a in sentence_candidates:
                    if mention_a[ID] not in reordered_ids and \
                            self.graph_builder.is_inside(mention_a[SPAN], current[SPAN], ) and \
                            mention_a[SPAN][0] < mention[SPAN][1]:
                        reordered_ids.append(mention_a[ID])
                        reordered.append(mention_a)
        return reordered

    def get_candidates(self, text_order, candidate_order, mention, index_sent):
        """ Gets the candidates ordered in a for the sieve check.

        :param text_order: The list of sentences that contain the list of mentions that form the text.
        :param candidate_order: The list of sentences that contain the list of mentions that form the text in bts order.
        :param mention: The mention whose candidates whe need.
        :param index_sent: The index of the current sentence.

        @rtype : list
        :return: A list of ordered candidates.
        """

        mention_index = [c[ID] for c in candidate_order[index_sent]].index(mention["id"])
        if len(candidate_order[index_sent][mention_index]["entity"][1]) == 1 and self.is_pronoun(mention):
            self.logger.debug("ORDERING: pronoun order")
            sentence_candidates = self.pronoun_order(candidate_order[index_sent][:mention_index], mention)
            other_candidates = [m for s in reversed(text_order[:index_sent]) for m in s]
            if pronouns.relative(mention[FORM].lower()):
                self.logger.debug("ORDERING: Relative pronoun order")
                sentence_candidates.reverse()
            return sentence_candidates + other_candidates
        else:
            return super(PronounSieve, self).get_candidates(text_order, candidate_order, mention, index_sent)
    pass
