# coding=utf-8
""" This modules load language specific gazetteers files into lists. As fallback create empty list for missing files or
in case of unexpected errors.
"""

import os
from logging import getLogger
from corefgraph.properties import lang, module_path

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '5/30/14'

logger = getLogger(__name__)

demonyms = []
locations = []
locations_and_demonyms = []
demonyms_locations_coincidences = set()
demonym_by_location = {}
locations_by_demonyms = {}


def load_demonym_file(file_name):
    """ Load the demonym and place in memory."""
    global demonyms_locations_coincidences

    demonym_file = open(file_name)
    for line in demonym_file:
        # line = line.lower()
        if line[0] != "#":
            line_tokens = []
            for token in line.split("\t"):
                if token == "":
                    continue
                if token == "\n":
                    continue
                line_tokens.append(token.strip())

            line_location = line_tokens[0]
            line_demonyms = line_tokens[1:]

            locations_and_demonyms.extend(line_tokens)
            locations.append(line_location)
            demonyms.extend(line_demonyms)
            demonym_by_location[line_location] = set(line_demonyms)
            for demonym in line_demonyms:
                try:
                    locations_by_demonyms[demonym].append(line_location)
                except KeyError:
                    locations_by_demonyms[demonym] = [line_location]
    locations_and_demonyms.extend(locations_and_demonyms)
    demonyms_locations_coincidences = set(demonyms).intersection(locations)


_name = "resources/languages/{0}/demonym/data.txt".format(lang)

try:
    load_demonym_file(os.path.join(module_path, _name))
except IOError as ex:
    logger.warning("Demonym file %s error", _name)