# coding=utf-8
""" Naf format output
"""

from corefgraph.output.basewriter import BaseDocument

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class GephiDocument(BaseDocument):
    """ Store the document in a KAF format(2.1).
    """
    short_name = "GEPHI"
    time_format = "%Y-%m-%dT%H:%M:%SZ"

    def store(self, graph_builder, encoding, language, version, linguistic_parsers,
              start_time, end_time, hostname, **kwargs):
        """ Store the graph in a string and return it.

        :param hostname: The name of the processing machine
        :param end_time: Real processing start
        :param start_time: Real processing end
        :param graph: the graph to be stored.
        :param language: The language code inserted into the kaf file
        :param version: The version of corefgraph set on kaf
        :param encoding: Encoding set on kaf document
        :param linguistic_parsers: The linguistic parser added to kaf header.
        :param kwargs: Unused
        """
        graph_builder.get_gephi(self.file)
