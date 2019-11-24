# coding=utf-8
""" The base document to provide a standard Api for document formatters.
"""

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '11/29/12'

from logging import getLogger


class BaseDocument:
    """ The base for create a document writer.
    """
    def __init__(self, filename="", stream=None, document_id=None):
        self.logger = getLogger(__name__)
        self.document_id = document_id
        if stream:
            self.file = stream
        else:
            self.file = open(filename, "w")

    def store(self, *args, **kwargs):
        """Implement here the storing code in sub classes.
        :param args: The arguments needed for store the graph.
        :param kwargs: The arguments needed for store the graph with name.
        """
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
