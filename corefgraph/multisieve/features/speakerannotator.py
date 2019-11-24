# coding=utf-8
""" Contains the necessary elements to extract the speaker of text fragments.

"""
from corefgraph.constants import QUOTED, UTTERANCE, LEMMA, FORM
from corefgraph.multisieve.features.constants import SPEAKER, IS_SPEAKER
from corefgraph.resources.dictionaries import verbs
from corefgraph.resources.tagset import dependency_tags
from .baseannotator import FeatureAnnotator

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class SpeakerAnnotator(FeatureAnnotator):
    """ Find speech type and speaker for mentions.
    """
    name = "speaker"
    features = [SPEAKER, IS_SPEAKER]

    # The subject dependency valid types for a subject of a reporting verb,
    invalid_speakers = ("-", "")

    def __init__(self, graphbuilder):
        super(SpeakerAnnotator, self).__init__(graphbuilder)

    def _find_speaker(self, syntactic_element, head_word):
        """ Find a plausible speaker for a mention inside a direct speech(Text
        inside quotations).

        Find closest reporting verb and select their subject as speaker.
        """
        constituent_utterance = syntactic_element[UTTERANCE]
        current_sentence = self.graph_builder.get_root(syntactic_element)

        # Set the sentences where find the speaker
        previous_sentence = self.graph_builder.get_prev_sentence(
            current_sentence)
        next_sentence = self.graph_builder.get_next_sentence(
            sentence=current_sentence)
        sentences = (current_sentence,  next_sentence, previous_sentence)
        # Search over the sentences
        for root in sentences:
            # If the current sentence is the first or
            # the last one of the roots is None.
            if root:
                sentence_terms = self.graph_builder.get_sentence_words(
                    sentence=root)
                for term in sentence_terms:
                    # Search for a reporting verb that is outside
                    # of the constituent utterance
                    if verbs.reporting(term[LEMMA]) and \
                            term[UTTERANCE] != constituent_utterance:
                        # Search the subject of the reporting verb.
                        for word, dependency \
                                in self.graph_builder.get_dependant_words(term):
                            if dependency_tags.subject(dependency["value"]):
                                return word
                        # Only rely on first reporting verb
                        return head_word[SPEAKER]
        return head_word[SPEAKER]

    def is_speaker(self, mention):
        head_word = self.graph_builder.get_head_word(mention)[FORM].lower()
        for speaker in self.graph_builder.get_speakers():
            if head_word == speaker:
                return speaker
        return False

    def extract_and_mark(self, mention):
        """ Determines the speaker of a element of a sentence.

        :param mention: a word, constituent or named entity.
        """
        head_word = self.graph_builder.get_head_word(mention)
        if mention[QUOTED]:
            mention[SPEAKER] = self._find_speaker(mention, head_word)
        else:
            mention[SPEAKER] = head_word[SPEAKER]
        if type(mention[SPEAKER]) is dict:
            mention[SPEAKER][IS_SPEAKER] = True
        if not mention.get(IS_SPEAKER, False):
            mention[IS_SPEAKER] = self.is_speaker(mention)
