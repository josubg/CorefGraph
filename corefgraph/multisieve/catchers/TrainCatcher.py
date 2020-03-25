# coding=utf-8
"""Import(this module) and inherit(BaseCatcher) to create a new catcher.
The system will call the constructor(once) and the catch_mention function for
each plausible mention obtained in the system. The filter calling order is not 
reliable for ALL option.
"""


from corefgraph.resources.tagset import constituent_tags
from corefgraph.resources.tagset import dependency_tags
from corefgraph.resources.tagset import pos_tags
from corefgraph.resources.dictionaries import pronouns
from corefgraph.constants import POS, NER, TAG, SPAN, ID
from corefgraph.multisieve.catchers import BaseCatcher


__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class TrainCatcher(BaseCatcher):
    """ Base class for catchers. To create a new catcher import and inherit from
     this class.
    """

    short_name = "trainCatcher"

    def _catch_mention(self, mention_candidate):
        """ Overload this in each catcher.

        :param mention_candidate: The mention to test

        :return: True or False.
        """
        mention_id = mention_candidate[ID]
        # manage the Named Entities(They may not be in the tree)
        if mention_id in self.extractor.named_entities_by_constituent:
            mention_span = mention_candidate.get(SPAN)
            skip_mention = False
            for named_entity_mention in \
                    self.extractor.named_entities_by_constituent.pop(
                    mention_id):
                skip_mention = mention_span == named_entity_mention.get(SPAN)
                self.feature_mention(mention=named_entity_mention)
                self.extractor.add_mention(mention=named_entity_mention)
            if skip_mention:
                return False

        self.feature_mention(mention_candidate)
        return True

    def feature_mention(self, mention):
        NO = "NO"
        mention_id = mention[ID]
        head = self.graph_builder.get_head(mention)
        sentence = self.graph_builder.get_root(mention)
        sentence_words = self.graph_builder.get_sentence_words(sentence=sentence)
        sentence_span = sentence[SPAN]
        span = mention[SPAN]

        previous_word_index = span[0] - sentence_span[0] - 1
        next_word_index = span[1] - sentence_span[0] + 1
        previous_word_pos = NO
        if previous_word_index > 0:
            previous_word_pos = sentence_words[previous_word_index].get(POS)
        next_word_pos = NO
        if next_word_index > len(sentence_words):
            next_word_pos = sentence_words[next_word_index].get(POS)

        words = self.graph_builder.get_words(mention)
        words_pos = [word.get(POS) for word in words]

        parent = self.graph_builder.get_syntactic_parent(mention)
        parent_head = self.graph_builder.get_head(parent)

        # Generate label and features
        label = mention_id in self.extractor.gold_mentions_by_constituent
        # Mention type
        feature_id = mention[ID]

        feature_pos = mention.get(POS, NO)
        feature_tag = mention.get(TAG, NO)

        feature_pronoun = bool(pos_tags.mention_pronoun(feature_pos) or
                               pronouns.all(mention["form"]))
        feature_np = bool(constituent_tags.mention_constituents(feature_tag))

        feature_entity = mention.get(NER, NO)

        # head
        feature_head_pos = head.get(POS)
        feature_same_head = parent_head[ID] == head[ID]
        feature_head_proper_noun = bool(pos_tags.proper_noun(head.get(POS)))

        # dependency
        feature_dependency_subject = False
        feature_dependency_object = False
        feature_dependency_other = True
        feature_dependency_all = ""
        dependants = self.graph_builder.get_governor_words(head)
        for dependant in dependants:
            dependency = dependant[1]["value"]
            linked_word = dependant[0]
            feature_dependency_all += dependency
            if pos_tags.verb(linked_word[POS]):
                if dependency_tags.subject(dependency):
                    feature_dependency_subject = True
                    feature_dependency_other = False

                if dependency_tags.object(dependency):
                    feature_dependency_object = True
                    feature_dependency_other = False
        # words
        feature_first_word_pos = words_pos[0]
        feature_last_word_pos = words_pos[-1]
        feature_word_count = len(sentence_words)

        # punctuation
        feature_mention_punctuation = [pos for pos in words_pos if pos_tags.conjunctions(pos) or pos == ","]
        feature_mention_comma = "," in words_pos
        feature_mention_conjunction = [pos for pos in words_pos if pos_tags.conjunctions(pos)]

        # Surrounding
        feature_previous_word_pos = previous_word_pos
        feature_next_word_pos = next_word_pos

        # Store in the mention
        mention["mention_gold"] = label
        mention["features"] = (
            feature_id,
            feature_pos,
            feature_tag,
            feature_pronoun,
            feature_np,
            feature_entity,
            feature_same_head,
            feature_head_pos,
            feature_head_proper_noun,
            feature_mention_punctuation,
            feature_mention_comma,
            feature_mention_conjunction,
            feature_previous_word_pos,
            feature_next_word_pos,
            feature_dependency_subject,
            feature_dependency_object,
            feature_dependency_other,
            feature_first_word_pos,
            feature_last_word_pos,
            feature_word_count
            )
