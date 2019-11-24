# coding=utf-8
from logging import getLogger

from corefgraph.resources.tagset import constituent_tags, pos_tags, ner_tags
from corefgraph.constants import TAG, FORM, POS, ID, CONSTITUENT, SPAN, NER
from corefgraph.resources.dictionaries import temporals, pronouns, verbs, stopwords

logger = getLogger(__name__)


def get_plausible_head(words):
    for word in reversed(words):
        if pos_tags.head_rules(word[POS]):
            return word


def get_head_word_form(graph_builder, element):
    """ Get the head of a chunk

    :param element: A syntactic element
    :return: String, the form of the word.
    """
    try:
        return element["head_word_form"]
    except KeyError:
        head = graph_builder.get_head_word(element)
        if ner_tags.mention_ner(element.get(NER)):
            # If element is a Named entity get the last word of the set
            # begin-word headword (both included) that isn't a common known
            # ne suffix
            words = graph_builder.get_words(element)
            words = words[:words.index(head) + 1]
            for word in reversed(words):
                word_form = word[FORM].replace(".", "")
                if not stopwords.common_NE_subfixes(word_form.lower()):
                    head = word
                    break
        element["head_word_form"] = head[FORM]
        return head[FORM]


def is_role_appositive(graph_builder,  first_constituent, second_constituent):
    """Check if are in a role appositive construction.

    :param first_constituent:
    :param second_constituent:
    :return: True or False
    """
    if not graph_builder.same_sentence(
            second_constituent, first_constituent):
        return False
    if not (graph_builder.is_inside(
            first_constituent[SPAN], second_constituent[SPAN]) or
                graph_builder.is_inside(
                    second_constituent[SPAN], first_constituent[SPAN])):
        return False
    # If candidate or mention are NE use their constituent
    if first_constituent[graph_builder.node_type] == graph_builder.named_entity_node_type:
        first_constituent = first_constituent[CONSTITUENT]
    if second_constituent[graph_builder.node_type] == graph_builder.named_entity_node_type:
        second_constituent = second_constituent[CONSTITUENT]

    # The Candidate is headed by a noun.
    candidate_head = graph_builder.get_head_word(first_constituent)
    if not candidate_head or not pos_tags.noun(candidate_head[POS]):
        return False
        # The Candidate appears as a modifier of a NP
    candidate_syntactic_father = graph_builder.get_syntactic_parent(
        first_constituent)
    if not constituent_tags.noun_phrase(candidate_syntactic_father[TAG]):
        return False
        # The NP whose head is the mention
    return second_constituent[ID] == graph_builder.get_head(
        candidate_syntactic_father)[ID]


def is_relative_pronoun(graph_builder, first_constituent, second_constituent):
    """ Check if tho constituents are in relative pronoun construction.
    Also mark they.

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


def is_enumeration(graph_builder,  constituent):
    """ Check if the constituent is a enumeration.
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


def is_predicative_nominative(graph_builder, constituent):
    """ Check if the constituent is a predicate in a predicative nominative
    mention.

    Stanford check for the relation:
    # "S < (NP=m1 $.. (VP < ((/VB/ <
                    /^(am|are|is|was|were|'m|'re|'s|be)$/) $.. NP=m2)))";
    # "S < (NP=m1 $.. (VP < (VP < ((/VB/ <
                    /^(be|been|being)$/) $.. NP=m2))))";

    :param constituent: The mention to check
    """
    constituent = constituent.get(CONSTITUENT, constituent)
    # The constituent is in a VP that start with a copulative verb
    parent = graph_builder.get_syntactic_parent(constituent)
    if constituent_tags.verb_phrase(parent.get(TAG)):
        # Check if previous sibling is a copulative verb
        for child in graph_builder.get_syntactic_children_sorted(parent):
            if child[SPAN] < constituent[SPAN]:
                if pos_tags.verb(child.get(POS)):
                    if verbs.copulative(child[FORM]):
                        return True
    return False


def is_attributive(graph_builder, constituent):
    """ Check if the constituent is a known attributive construction

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


def is_appositive_construction_child(graph_builder, constituent):
    """ Check if the mention is in a appositive construction.

    "NP=m1 < (NP=m2 $.. (/,/ $.. NP=m3))";
    "NP=m1 < (NP=m2 $.. (/,/ $.. (SBAR < (WHNP < WP|WDT=m3))))";
    "/^NP(?:-TMP|-ADV)?$/=m1 < (NP=m2 $- /^,$/ $-- NP=m3 !$ CC|CONJP)";
    "/^NP(?:-TMP|-ADV)?$/=m1 <
                  (PRN=m2 < (NP < /^NNS?|CD$/ $-- /^-LRB-$/ $+ /^-RRB-$/))";

    :param graph_builder: The graphBuilder
    :param constituent: The mention to check
    """
    constituent = constituent.get("constituent", constituent)

    # mention is inside a NP
    # TODO Improve the precision
    parent = graph_builder.get_syntactic_parent(constituent)
    if not constituent_tags.noun_phrase(parent[TAG]):
        return False
    siblings = graph_builder.get_syntactic_sibling(constituent)
    # Check if
    while siblings:
        actual = siblings.pop(0)
        if actual == constituent:
            break
    else:
        return False

    while siblings:
        actual = siblings.pop(0)
        if actual[FORM] == ",":
            break
    else:
        return False

    while siblings:
        actual = siblings.pop(0)
        if constituent_tags.noun_phrase(actual.get(TAG)):
            return parent
        if pronouns.relative(graph_builder.get_words(actual)[0].get("form")):
            return parent

    return False


def is_bare_np(graph_builder, constituent):
    head_word = graph_builder.get_head_word(constituent)
    head_form = head_word[FORM].lower()
    head_word_pos = head_word[POS]
    words = graph_builder.get_words(constituent)
    if pos_tags.singular_common_noun(head_word_pos) and \
            not temporals.temporals(head_form) and (
            len(words) == 1 or pos_tags.adjective(words[0][POS])):
        logger.debug(
            "Mention is bare NP: %s(%s)", constituent[FORM], constituent[ID])
        return True
    return False


def is_bare_plural(graph_builder, constituent):
    """ Check if the constituent is Bare plural.
    :param constituent: The constituent to check
    :return: Boolean
    """
    span = constituent[SPAN]
    return (span[0] - span[1] == 0) and \
        pos_tags.bare_plurals(
            graph_builder.get_constituent_words(constituent)[0][POS])


def is_pleonastic(graph_builder, constituent):
    """ Determine if the mention is pleonastic.
    :param graph_builder: The graph builder
    :param constituent: The constituent to check if is pleonastic

        "@NP < (PRP=m1 < it|IT|It) $..
                (@VP < (/^V.*/ < /^(?i:is|was|be|becomes|become|became)$/ $.. (@VP < (VBN $.. @S|SBAR))))"
        "@NP <
                (PRP=m1 < it|IT|It) $.. (@VP < (/^V.*/ < /^(?i:is|was|be|becomes|become|became)$/
                $.. (@VP < (VBN $.. @S|SBAR))))"

        // in practice, go with this one (best results)

        "NP < (PRP=m1) $.. (VP < ((/^V.*/ < /^(?:is|was|become|became)/)         $.. (ADJP $.. (/S|SBAR/))))"
        "NP < (PRP=m1) $.. (VP < ((/^V.*/ < /^(?:is|was|become|became)/)         $.. (ADJP < (/S|SBAR/))))"
        "NP < (PRP=m1) $.. (VP < ((/^V.*/ < /^(?:is|was|become|became)/)         $.. (NP < /S|SBAR/)))"
        "NP < (PRP=m1) $.. (VP < ((/^V.*/ < /^(?:is|was|become|became)/)         $.. (NP $.. ADVP $.. /S|SBAR/)))"

        "NP < (PRP=m1) $.. (VP < ((/^V.*/ < /^(?:seems|appears|means|follows)/)  $.. /S|SBAR/))"

        "NP < (PRP=m1) $.. (VP < ((/^V.*/ < /^(?:turns|turned)/)                 $.. PRT $.. /S|SBAR/))"

        "NP < (PRP=m1) $.. (VP < (MD $.. (VP < ((/^V.*/ < /^(?:be|become)/) $.. (VP < (VBN $.. /S|SBAR/))))))"
        "NP < (PRP=m1) $.. (VP < (MD $.. (VP < ((/^V.*/ < /^(?:be|become)/) $.. (ADJP $.. (/S|SBAR/))))))"
        "NP < (PRP=m1) $.. (VP < (MD $.. (VP < ((/^V.*/ < /^(?:be|become)/) $.. (ADJP < (/S|SBAR/))))))"
        "NP < (PRP=m1) $.. (VP < (MD $.. (VP < ((/^V.*/ < /^(?:be|become)/) $.. (NP < /S|SBAR/)))))"
        "NP < (PRP=m1) $.. (VP < (MD $.. (VP < ((/^V.*/ < /^(?:be|become)/) $.. (NP $.. ADVP $.. /S|SBAR/)))))"


    """
    # NP < (PRP=m1) $..
    # Is a "it" pronoun
    if constituent_tags.noun_phrase(constituent.get(TAG)):
        pleonastic_np = constituent
    else:
        father = graph_builder.get_syntactic_parent(constituent)
        # Is a child of a NP
        if constituent_tags.noun_phrase(father[TAG]):
            pleonastic_np = father
        else:
            return False

    if pleonastic_np is None:
        return False
    # $.. (VP

    # Have a (next) sibling that is a VP
    np_siblings = graph_builder.get_syntactic_sibling(pleonastic_np)
    # try:
    #     np_index = next(index for (index, d) in enumerate(np_siblings) if d[ID] == pleonastic_np[ID])
    # except:
    #     logger.error("ERROR: %s in %s ", mention, np_siblings)
    #     raise Exception()
    verb_phrase, verb_phrase_index = graph_builder.check_sibling_property(
        0, np_siblings,
        TAG, constituent_tags.verb_phrase)

    if not verb_phrase:
        return False
    # Base Case (/^V.*/ < /^(?i:is|was|be|becomes|become|became)$/ $.. (@VP < (VBN $.. @S|SBAR)))
    vp_constituents = graph_builder.get_syntactic_children_sorted(verb_phrase)
    valid_verb, valid_verb_index = graph_builder.check_sibling_property(
        0, vp_constituents, FORM, verbs.pleonastic_verbs_full)
    if valid_verb:
        inner_verb_phrase, inner_verb_phrase_index = graph_builder.check_sibling_property(
            valid_verb_index, vp_constituents,
            TAG, constituent_tags.verb_phrase)
        if inner_verb_phrase:
            inner_vp_constituents = graph_builder.get_syntactic_children_sorted(inner_verb_phrase)
            verb_form, verb_form_index = graph_builder.check_sibling_property(
                0, inner_vp_constituents, POS,
                pos_tags.verbs_past_particicle)
            if verb_form:
                # children = graph_builder.get_syntactic_children(verb_phrase)
                # verb_form, verb_form_index = check_sibling_property(
                #    0, children, POS, constituent_tags.past_participle_verb)
                # if verb_form:
                sbar, sbar_index = \
                    graph_builder.check_sibling_property(
                        verb_form_index, inner_vp_constituents, TAG, constituent_tags.simple_or_sub_phrase)
                return sbar is not None

    # First Case
    # ((/^V.*/ < /^(?:is|was|become|became)/)
    vp_constituents = graph_builder.get_syntactic_children_sorted(verb_phrase)
    valid_verb, valid_verb_index = graph_builder.check_sibling_property(
        0, vp_constituents, FORM, verbs.pleonastic_verbs)
    if valid_verb:
        # $.. (ADJP $.. (/S|SBAR/))))"
        # $.. (ADJP < (/S|SBAR/))))"
        adjectival_phrase, adjectival_phrase_index = graph_builder.check_sibling_property(
            valid_verb_index, vp_constituents,
            TAG, constituent_tags.adjectival_phrase)
        if adjectival_phrase:
            sbar, sbar_index = graph_builder.check_sibling_property(
                adjectival_phrase_index, vp_constituents, TAG, constituent_tags.simple_or_sub_phrase)
            if sbar is not None:
                return True
            children = graph_builder.get_syntactic_children_sorted(
                adjectival_phrase)
            sbar, sbar_index = graph_builder.check_sibling_property(
                0, children, TAG, constituent_tags.simple_or_sub_phrase)
            if sbar is not None:
                return True

        # $.. (NP < /S|SBAR/)))"
        # $.. (NP $.. ADVP $.. /S|SBAR/)))"
        noun_phrase, noun_phrase_index = graph_builder.check_sibling_property(
            valid_verb_index, vp_constituents, TAG,
            constituent_tags.noun_phrase)
        if noun_phrase:
            adverbial_phrase, adverbial_phrase_index = \
                graph_builder.check_sibling_property(
                    noun_phrase_index, vp_constituents,
                    TAG, constituent_tags.adverbial_phrase)
            # if adverbial_phrase:
            if True:
                sbar, sbar_index = graph_builder.check_sibling_property(
                    adverbial_phrase_index, vp_constituents, TAG, constituent_tags.simple_or_sub_phrase)
                if sbar is not None:
                    return True
            children = graph_builder.get_syntactic_children_sorted(noun_phrase)
            sbar, sbar_index = \
                graph_builder.check_sibling_property(
                    0, children, TAG, constituent_tags.simple_or_sub_phrase)
            if sbar is not None:
                return True
        return False
    # Second Case
    # ((/^V.*/ < /^(?:seems|appears|means|follows)/)

    valid_verb, _valid_verb_index = \
        graph_builder.check_sibling_property(
            0, vp_constituents, FORM,
            verbs.alternative_a_pleonastic_verbs)
    if valid_verb:
        #  $.. /S|SBAR/)
        sbar, sbar_index = graph_builder.check_sibling_property(
            valid_verb_index, vp_constituents,
            TAG, constituent_tags.simple_or_sub_phrase)
        return sbar is not None
    # third Case
    # (VP < ((/^V.*/ < /^(?:turns|turned)/)
    valid_verb, valid_verb_index = \
        graph_builder.check_sibling_property(
            0, vp_constituents, FORM,
            verbs.alternative_b_pleonastic_verbs)
    if valid_verb:
        # $.. PRT $.. /S|SBAR/))
        particle, particle_index = graph_builder.check_sibling_property(
            valid_verb_index, vp_constituents,
            TAG, constituent_tags.particle_constituent)

        sbar, sbar_index = graph_builder.check_sibling_property(
            particle_index, vp_constituents, TAG,
            constituent_tags.simple_or_sub_phrase)
        return sbar is not None

    # Four Case
    # (MD $.. (VP < ((/^V.*/ < /^(?:be|become)/)
    valid_modal, valid_modal_index = graph_builder.check_sibling_property(
        0, vp_constituents, POS, pos_tags.modal)
    if valid_modal:
        verb_phrase, verb_phrase_index = graph_builder.check_sibling_property(
            valid_modal_index, vp_constituents,
            TAG, constituent_tags.verb_phrase)
        if verb_phrase:
            inner_vp_constituents = graph_builder.get_syntactic_children_sorted(
                verb_phrase)
            valid_verb, valid_verb_index = graph_builder.check_sibling_property(
                0, inner_vp_constituents, FORM, verbs.alternative_c_pleonastic_verbs)
            # confirmed case
            if valid_verb:
                # brach a
                # $.. (@VP < (VBN $.. @S|SBAR))
                # check verb phrase, then check verb POS and then check S or SB
                verb_phrase, verb_phrase_index = graph_builder.check_sibling_property(
                    valid_verb_index, inner_vp_constituents,
                    TAG, constituent_tags.verb_phrase)
                if verb_phrase:
                    inner_vp_constituents = graph_builder.get_syntactic_children_sorted(
                        verb_phrase)
                    # Fin del añadido ,un tab añadido
                    verb_form, verb_form_index = graph_builder.check_sibling_property(
                        valid_verb_index, inner_vp_constituents, POS,
                        pos_tags.verbs_past_particicle)
                    if verb_form:
                        # children = graph_builder.get_syntactic_children(verb_phrase)
                        # verb_form, verb_form_index = check_sibling_property(
                        #    0, children, POS, constituent_tags.past_participle_verb)
                        # if verb_form:
                        sbar, sbar_index = \
                            graph_builder.check_sibling_property(
                                verb_form_index, inner_vp_constituents, TAG, constituent_tags.simple_or_sub_phrase)
                        return sbar is not None
                # Branch B or C
                # $.. (ADJP $.. (/S|SBAR/))))
                # $.. (ADJP < (/S|SBAR/))))
                adjectival_phrase, adjectival_phrase_index = graph_builder.check_sibling_property(
                    0, inner_vp_constituents,
                    TAG, constituent_tags.adjectival_phrase)
                if adjectival_phrase:
                    sbar, sbar_index = graph_builder.check_sibling_property(
                        adjectival_phrase_index, inner_vp_constituents, TAG, constituent_tags.simple_or_sub_phrase)
                    if sbar is not None:
                        return True
                    children = graph_builder.get_syntactic_children_sorted(
                        adjectival_phrase)
                    sbar, sbar_index = graph_builder.check_sibling_property(
                        0, children, TAG, constituent_tags.simple_or_sub_phrase)
                    if sbar is not None:
                        return True
                    return False
                # $.. (NP $.. ADVP $.. /S|SBAR/)))
                # $.. (NP < /S|SBAR/)))
                noun_phrase, noun_phrase_index = graph_builder.check_sibling_property(
                    valid_verb_index, inner_vp_constituents, TAG,
                    constituent_tags.noun_phrase)
                if noun_phrase:
                    # adverbial_phrase, adverbial_phrase_index = \
                    #     graph_builder.check_sibling_property(
                    #         noun_phrase_index, inner_vp_constituents,
                    #         TAG, constituent_tags.adverbial_phrase)
                    # if adverbial_phrase:
                    if True:
                        sbar, sbar_index = graph_builder.check_sibling_property(
                            0, inner_vp_constituents, TAG, constituent_tags.simple_or_sub_phrase)
                        if sbar is not None:
                            return True
                    children = graph_builder.get_syntactic_children_sorted(noun_phrase)
                    sbar, sbar_index = \
                        graph_builder.check_sibling_property(
                            0, children, TAG, constituent_tags.simple_or_sub_phrase)
                    if sbar is not None:
                        return True
    return False


def clean_string(form):
    form = form.lower().strip()
    if form.endswith(" 's"):
        return form[:len(form) - 3].strip()
    if form.endswith("'s"):
        return form[:len(form) - 2].strip()
    return form.strip()
