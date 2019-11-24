# coding=utf-8
""" Utility functions used for loading resource files into language modules.

"""


import marshal
import logging

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

logger = logging.getLogger(__name__)


def load_file(file_name):
    """ Load a file into a line list and remove the next line ending character.

    :param file_name: The name of the file to load
    :return: A list of file lines
    """
    data_file = open(file_name, 'r')
    data = [line[:-1] for line in data_file]
    data_file.close()
    return data


def split_gendername_file(filename):
    """ Load a file of word marked by gender.

    The file is a two column per file text file: The first column is the word
    and the second is the gender separated by a tab.


    :param filename: The name(path) of the file to load.
    :return: return a female anf
    """
    combined = open(filename, 'r')
    male = []
    female = []
    for index, line in enumerate(combined):
        try:
            name, gender = line.replace('\n', '').split('\t')
            if gender == "MALE":
                male.append(name)
            elif gender == "FEMALE":
                female.append(name)
        except Exception as ex:
            logger.exception("ERROR in combine name file line: %s", index)
    combined.close()
    return female, male


def bergma_split(filename):
    """ Load the bergsma file into a dict of tuples. Try to keep a marshaled
    version of the file. If you changes the file remember to erase the
    marshalled version.
    """
    marshal_filename = filename + ".marshal"
    try:
        with open(marshal_filename, 'r') as data_file:
            data = marshal.load(data_file)
        return data
    except IOError as ex:
        logger.info("No marshal file")
        logger.debug("Reason: %s", ex)
        with open(filename, 'r') as data_file:
            data = dict()
            for index, line in enumerate(data_file):
                try:
                    form, stats = line.split("\t")
                    data[form] = tuple([int(x) for x in stats.split()])
                except Exception as ex:
                    pass
                    logger.debug("line(%s) sipped: %s", index, ex)
            try:
                with open(marshal_filename, 'w') as store_file:
                    marshal.dump(data, store_file, -1)
                logger.warning("Created marshal file")
                logger.debug("path: %s", marshal_filename)
            except IOError as ex:
                logger.warning("Marshal file not created %s", marshal_filename)
                pass
        return data
