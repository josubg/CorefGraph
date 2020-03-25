# coding=utf-8
from logging import getLogger

from corefgraph.resources.tagset import constituent_tags, ner_tags
from corefgraph.resources.dictionaries import temporals, verbs, stopwords, pronouns
from corefgraph.resources.tagset import pos_tags
from corefgraph.constants import TAG, FORM, NER, POS, ID, LEMMA, SPAN, CONSTITUENT, MULTIWORD


logger = getLogger(__name__)


def get_plausible_head(children):
    for element in children:
        if POS in element:
            if pos_tags.head_rules(element[POS]):
                return element
        if TAG in element:
            if constituent_tags.head_rules(element[TAG]):
                return element
    return children[-1]


# TODO Check
def get_head_word_form(graph_builder,  element):
    """ Get the head of a chunk

    :param graph_builder: The graph manager.
    :param element: A syntactic element.
    :return: String, the form of the word.
    """
    try:
        return element["head_word_form"]
    except KeyError:
        head = graph_builder.get_head_word(element)
        for token in head.get(MULTIWORD, []):
            head = token
            if graph_builder.is_head(token):
                break
        if ner_tags.mention_ner(element.get(NER)):
            # If element is a Named entity get the last word of the set
            # begin-word headword (both included) that isn't a common known
            # ne suffix
            words = []
            brk = False
            for word in graph_builder.get_words(element):
                for token in word.get(MULTIWORD, [word]):
                    words.append(token)
                    if token is head:
                        brk = True
                        break
                if word is head or brk:
                    break

            for word in reversed(words):
                word_form = word[FORM].replace(".", "")
                if not stopwords.common_NE_subfixes(word_form.lower()):
                    head = word
                    break

        element["head_word_form"] = head[FORM]
        return head[FORM]


# TODO Check
def is_role_appositive(graph_builder,  mention_a, mention_b):
    """Check if are in a role appositive construction.

    :param graph_builder: The graph manager.
    :param first_constituent:
    :param second_constituent:
    :return: True or False
    """
    if not graph_builder.same_sentence(
            mention_a, mention_b):
        return False
    constituent_a = mention_a.get(CONSTITUENT, mention_a)
    constituent_b = mention_b.get(CONSTITUENT, mention_b)
    if graph_builder.is_inside(
            constituent_a[SPAN], constituent_b[SPAN]):
        return _role_appositive(graph_builder, constituent_b, constituent_a)
    return False


def _role_appositive(graph_builder, first_constituent, second_constituent):

    # The Candidate is headed by a noun.
    candidate_head = graph_builder.get_head_word(second_constituent)
    if not candidate_head or not pos_tags.noun(candidate_head[POS]):
        return False
        # The Candidate appears as a modifier of a NP
    candidate_syntactic_father = graph_builder.get_syntactic_parent(
        second_constituent)
    if not constituent_tags.noun_phrase(candidate_syntactic_father[TAG]):
        return False
        # The NP whose head is the mention
    # if first_constituent[ID] == graph_builder.get_head(
    #         candidate_syntactic_father)[ID]:
    #     return True

    if first_constituent[ID] == candidate_syntactic_father[ID]:
        return True
    candidate_syntactic_father = graph_builder.get_syntactic_parent(
        candidate_syntactic_father)

    if not constituent_tags.noun_phrase(candidate_syntactic_father[TAG]):
        return False

    if first_constituent[ID] == candidate_syntactic_father[ID]:
        return True
    return False


# TODO Check
def is_relative_pronoun(graph_builder, first_constituent, second_constituent):
    """ Check if tho constituents are in relative pronoun construction.
    Also mark they.

    :param graph_builder: The graph manager.
    :param first_constituent:
    :param second_constituent:
    :return: Boolean
    """
    # NP < (NP=m1 $.. (SBAR < (WHNP < WP|WDT=m2)))
    if not graph_builder.same_sentence(
            first_constituent, second_constituent):
        return False
    if not pronouns.relative(second_constituent[FORM].lower()):
        return False
    if first_constituent[SPAN] > second_constituent[SPAN]:
        return False
    enclosing_np = graph_builder.get_syntactic_parent(
        first_constituent)

    upper = graph_builder.get_syntactic_parent(second_constituent)
    while upper and (upper[graph_builder.node_type] != graph_builder.root_type):
        if graph_builder.is_inside(
                upper[SPAN], enclosing_np[SPAN]):
            upper = graph_builder.get_syntactic_parent(upper)
        elif upper[ID] == enclosing_np[ID]:
            # TODO check path element
            return True
        else:
            return False

    return False


# TODO Check
def is_enumeration(graph_builder,  constituent):
    """ Check if the constituent is a enumeration.

    :param graph_builder: The graph manager.
    :param constituent: The constituent to check
    :return: True or False
    """
    coordination = False
    np_pre_coordination = False
    for child in graph_builder.get_syntactic_children_sorted(constituent):
        child_tag = child.get(TAG)
        if constituent_tags.noun_phrase(child_tag):
            if coordination:
                return True
            else:
                np_pre_coordination = True
        else:
            child_pos = child.get(POS)
            if pos_tags.conjunction(child_pos) and np_pre_coordination:
                coordination = True
    return False


def is_enumeration(graph_builder, mention):
        """ Check if the mention is an enumeration

        :param mention:  The mention that can be a enumeration.

        :return: True or false
        """
        mention_words = graph_builder.get_words(mention)
        last_comma = 0
        last_conjuction = 0
        for index, word in enumerate(mention_words):
            if word[FORM] == ",":
                last_comma = index
            if pos_tags.conjunction(word.get(POS)):
                last_conjuction = index
        if last_conjuction and last_conjuction > last_comma:
            return True
        return False


# TODO Check
def is_predicative_nominative(graph_builder, constituent):
    """ Check if the constituent is a predicate in a predicative nominative
    mention.

    Stanford check for the relation:
    # "S < (NP=m1 $.. (VP < ((/VB/ <
                    /^(am|are|is|was|were|'m|'re|'s|be)$/) $.. NP=m2)))";
    # "S < (NP=m1 $.. (VP < (VP < ((/VB/ <
                    /^(be|been|being)$/) $.. NP=m2))))";

    :param graph_builder: The graph manager.
    :param constituent: The mention to check
    """
    constituent = constituent.get(CONSTITUENT, constituent)
    # The constituent is in a VP that start with a copulative verb
    parent = graph_builder.get_syntactic_parent(constituent)
    # Check if previous sibling is a copulative verb
    for child in graph_builder.get_syntactic_sibling(constituent):
        if child[SPAN][0] < constituent[SPAN][0]:
            if verbs.copulative(child[FORM]):
                return True
    return False


# TODO Check
def is_attributive(graph_builder, constituent):
    """ Check if the constituent is a known attributive construction

    :param graph_builder: The graph manager.
    :param constituent: The mention to check
    """
    # The constituent is in a VP that start with a copulative verb
    constituent = constituent.get(CONSTITUENT, constituent)
    root = graph_builder.get_root(constituent)
    sentence_words = graph_builder.get_words(root)
    first_word = constituent[SPAN][0] - root[SPAN][0]
    if first_word == 0:
        return False
    return sentence_words[first_word - 1][FORM] in ("of",)


# TODO Check
def is_appositive_construction_child(graph_builder, mention):
    """ Check if the mention is in a appositive construction.

    "NP=m1 < (NP=m2 $.. (/,/ $.. NP=m3))";
    "NP=m1 < (NP=m2 $.. (/,/ $.. (SBAR < (WHNP < WP|WDT=m3))))";
    "/^NP(?:-TMP|-ADV)?$/=m1 < (NP=m2 $- /^,$/ $-- NP=m3 !$ CC|CONJP)";
    "/^NP(?:-TMP|-ADV)?$/=m1 <
                  (PRN=m2 < (NP < /^NNS?|CD$/ $-- /^-LRB-$/ $+ /^-RRB-$/))";

    :param graph_builder: The graphBuilder
    :param mention: The mention to check
    """
    constituent = mention.get("constituent", mention)

    # mention is inside a NP
    # TODO Improve the precision
  
    # parent is NP
    plausible_parent = constituent
    constituent_parent = graph_builder.get_syntactic_parent(
        plausible_parent)

    if constituent_parent is None:
        return False
    # if graph_builder.get_head_word(constituent_parent) != constituent_headword:
    #     return False
    if not constituent_tags.noun_phrase(
            constituent_parent.get(TAG)):
        return False

    if ner_tags.mention_ner(constituent_parent.get(NER)):
        return False
    # Search if the next brother is usable
    siblings = graph_builder.get_syntactic_sibling(
        constituent)
    position = siblings.index(constituent)

    # Search for a coma or a conjunction between mention and the end
    if position > 0:
        form = mention[FORM]
        if form[0]in (',', '(', '[', '"', "'") and form[-1] in (',', ')', ']', '"', "'"):
            logger.info(
                    "Mention is apposition(First Element): %s",
                    constituent[FORM])
            return constituent_parent
    elif len(siblings) > position + 1:
        brother = siblings[position+1]
        if constituent_tags.noun_phrase(brother.get(TAG)):
            # Check if next to conjunction (or comma) exist a
            # enumerable sibling
            if graph_builder.get_words(brother)[0][FORM] == ",":
                logger.info(
                    "Mention is apposition(First Element): %s",
                    constituent[FORM])
                return constituent_parent
    # Check comma or conjunction before mention and previous sibling is usable

    return False


def is_bare_np(graph_builder, constituent):
    head_word = graph_builder.get_head_word(constituent)
    head_form = head_word[FORM].lower()
    head_word_pos = head_word[POS]
    words = graph_builder.get_words(constituent)
    sentence_words = graph_builder.get_words(graph_builder.get_root(constituent))
    first_word_index = sentence_words.index(words[0])
    last_word_index = sentence_words.index(words[-1])
    if pronouns.all(head_form) or pos_tags.pronoun(head_word_pos):
        return False

    if pos_tags.singular_common_noun(head_word_pos) and \
            not temporals.temporals(head_form) and (
            len(words) == 1 or pos_tags.  adjective(words[0][POS])):
        siblings = graph_builder.get_syntactic_sibling(
            constituent)

        #position = siblings.index(constituent)

        # if words[-1] != head_word:
        #    return False
        if first_word_index > 0:
            prev_word = sentence_words[first_word_index - 1]
            if prev_word[FORM].lower()[-1] in ('al', 'del', "y", "e", "ni"):
                return False
            if prev_word[FORM].lower()[-1] == ",":
                parent = graph_builder.get_syntactic_parent(constituent)[FORM]
                if "y" in parent:
                    return False
                if "e" in parent:
                    return False
                if "ni" in parent:
                    return False
            return False
        if last_word_index + 1 < len(sentence_words):
            #if graph_builder.get_words(siblings[position+1])[0][FORM].lower() in ("y", "e", "ni"):
            next_word = sentence_words[last_word_index + 1]
            if next_word[FORM].lower()[0] in ("y", "e", "ni"):
                return False
            if next_word[FORM].lower()[0] == ",":
                parent = graph_builder.get_syntactic_parent(constituent)[FORM]
                if "y" in parent:
                    return False
                if "e" in parent:
                    return False
                if "ni" in parent:
                    return False
                return False
        logger.debug(
            "Mention is bare NP: %s(%s)", constituent[FORM], constituent[ID])
        return True
    return False


# TODO check
def is_bare_plural(graph_builder, constituent):
    """ Check if the constituent is Bare plural.

    :param graph_builder: The graph manager.
    :param constituent: The constituent to check
    :return: Boolean
    """
    span = constituent[SPAN]
    return (span[0] - span[1] == 0) and \
        pos_tags.bare_plurals(
            graph_builder.get_constituent_words(constituent)[0][POS])


# TODO CHECK
def is_pleonastic(graph_builder, constituent):
    """ Determine if the mention is pleonastic.

    :param graph_builder: The graph manager.
    :param graph_builder: The graph builder
    :param constituent: The constituent to check if is pleonastic

    """
    # NP < (PRP=m1) $..
    # Is a "it" pronoun

    # if constituent_tags.noun_phrase(constituent.get(TAG)):
    #     pleonastic_np = constituent
    # else:
    #     father = graph_builder.get_syntactic_parent(constituent)
    #     # Is a child of a NP
    #     if constituent_tags.noun_phrase(father[TAG]):
    #         pleonastic_np = father
    #     else:
    #         return False
    #
    # if pleonastic_np is None:
    #     return False
    if not pronouns.pleonastic(constituent[FORM]):
        return False

    sentence_words = graph_builder.get_words(graph_builder.get_root(constituent))
    words = graph_builder.get_words(constituent)

    first_word_index = sentence_words.index(words[0])
    last_word_index = sentence_words.index(words[-1])

    if last_word_index + 1 < len(sentence_words):
        next_word = sentence_words[last_word_index+1]

        if pos_tags.interrogative_pronoun(next_word.get(POS, None)):
            return True
        if verbs.pleonastic_verbs(next_word[LEMMA]):
            return True

    if last_word_index + 2 < len(sentence_words):
        next_word = sentence_words[last_word_index+1]
        if constituent_tags.adverbial_phrase(next_word[LEMMA] in ("no", "haber")):
            if verbs.pleonastic_verbs(sentence_words[last_word_index + 2].get(LEMMA, None)):
                return True

    if first_word_index > 0 and last_word_index + 1 < len(sentence_words):
        prev_word = sentence_words[first_word_index - 1]
        next_word = sentence_words[last_word_index +1]

        if prev_word["form"].lower() == 'y' and next_word['form'] == 'que':
            return True

    return False


def clean_string(form):
    return form.lower().replace("_", " ").strip()
