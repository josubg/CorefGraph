# coding=utf-8
""" General properties

Tagset values for each language as specified in resources/tagset. Currently, we use POS, Syntactic Constituents
and NER types tagsets. The nomenclature for the files in resources/target is used to instantiate the variables
below. For example, pos_tag_set will expect a file end in '_pos', such as 'tagset_pos'. The same applies to
'_constituent' and '_ner'.

"""

import logging
import logging.config
import os
import sys

try:
    from yaml import full_load
    config_filename = os.path.abspath(os.path.join(__path__[0], 'logging.yaml'))
    try:
        logging.config.dictConfig(full_load(open(config_filename)))
    except Exception as ex:
        sys.stderr.write("NO LOGGING: {0} \nError loading configuration: {1}".format(config_filename, ex))
except ImportError as ex:
    sys.stdout.write("No logging: Error importing yalm: " + str(ex))

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '10/30/13'


default_lang = "default"
default_ner_tag_set = "default"
default_dep_tag_set = "default"
default_pos_tag_set = "default"
default_constituent_tag_set = "default"

lang = None
encoding = None

pos_tag_set = None
constituent_tag_set = None
ner_tag_set = None
dep_tag_set = None

module_path = os.path.split(__path__[0])[0]


def set_lang(lang_code, encoding_code):
    """ set the module properties from  a specific language properties


    :param lang_code: A string that determines de language used in the system. lowercase and
    """
    logger = logging.getLogger(__name__)
    try:
        lang_properties = __import__("properties_{0}".format(lang_code), globals=globals(), locals=locals())
    except ImportError as io:
        logger.error("No module for language %s", lang_code)
        exit(-1)
    global encoding

    global lang
    global pos_tag_set
    global constituent_tag_set
    global ner_tag_set
    global dep_tag_set

    encoding = encoding_code
    if lang and lang == lang_code:
        return
    lang = lang_properties.lang
    try:
        pos_tag_set = lang_properties.pos_tag_set
    except Exception as Ex:
        logger.warning("Warning using default Part Of Speech tagset.", )
        logger.exception("Exception")
        pos_tag_set = default_pos_tag_set
    try:
        constituent_tag_set = lang_properties.constituent_tag_set
    except Exception as Ex:
        logger.warning("Warning using default constituent tagset.", )
        logger.exception("Exception")
        constituent_tag_set = default_constituent_tag_set
    try:
        ner_tag_set = lang_properties.ner_tag_set
    except Exception as Ex:
        logger.warning("Warning using default Named Entity tagset.", )
        logger.exception("Exception")
        ner_tag_set = default_ner_tag_set
    try:
        dep_tag_set = lang_properties.dep_tag_set
    except Exception as Ex:
        logger.warning("Warning using default dependency tagset.", )
        logger.exception("Exception")
        dep_tag_set = default_dep_tag_set

    logger.info("Language: %s.", lang)
    logger.info("Part of speech: %s.", pos_tag_set)
    logger.info("Constituent TagSet: %s.", constituent_tag_set)
    logger.info("Dependency: %s.", dep_tag_set)
    logger.info("Named entities: %s.", ner_tag_set)
