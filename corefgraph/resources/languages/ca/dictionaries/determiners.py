# coding=utf-8
""" This module contains de functions that can determine if a word is one of the relevant determiners used in
corefgraph.

These relevant determiners are:

indefinite_articles: Used to determine if the mention is indefinite.
quantifiers: Used to filter mention that starts with quantifiers.
partitives: Used to filter mentions that are inside a partitive expression.
partitive_particle: Used among partitives.

"""

__author__ = 'Rodrigo Agerri <rodrigo.agerri@ehu.es>'

from corefgraph.resources.lambdas import list_checker, equality_checker, matcher, fail

# Used to determine if the mention is an indefinite mention Un hombre
indefinite_articles = list_checker((
    'alguna', 'algun', 'algunes', 'algú', 'alguns', 'ambdues', 'ambdòs', 'bastant', 'bastants', 'cada', 'qualssevol',
    'qualsevol', 'quant', 'quants', 'massa', 'molta', 'moltes', 'molt', 'molts', 'cap', 'gens', 'ninguns', 'ningú',
    'altra', 'altres', 'altre', 'poca', 'poques', 'poc', 'pocs', 'sengles', 'tantes', 'tanta', 'tants', 'tant', 'totes',
    'tota', 'tots', 'tot', 'unes', 'una', 'uns', 'un', 'diverses', 'diversos'))

# Used to determine a quantified mention:  Bastante Queso
# cuantificadores; they overlap with indefinite_articles in Spanish
quantifiers = list_checker((
    'no', 'res', 'suficientment', 'suficient', 'harto', 'alguna', 'algun', 'algunes', 'alguns', 'ambdues', 'ambdòs',
    'prou', 'cada', 'qualssevol', 'qualsevol', 'quantes', 'quants', 'altres', 'massa', 'molta', 'moltes', 'molt',
    'molts', 'cap', 'gens', 'ninguns', 'altra', 'altres', 'altre', 'altres', 'poca', 'poques', 'poc', 'pocs', 'sengles',
    'tantes', 'tanta', 'tants', 'tant', 'totes', 'tota', 'tots', 'tot', 'unes', 'una', 'uns', 'un', 'diverses',
    'diversos', 'divers'))

# partitivos (we also include here cardinales and ordinales)
partitives = list_checker((
    'grup', 'grups', 'equip', 'alguns', 'quantitat', 'total', 'tot', 'milers', 'quilos', 'quilo', 'mig', 'mitja',
    'segon', 'segona', 'segones', 'tercer', 'tercera', 'terceres', 'quart', 'quarta', 'quarts', 'quartes', 'cinquè',
    'cinquena', 'cinquens', 'cinquenes', 'sisena', 'sisè', 'sisenes', 'sinsens', 'setè', 'setena', 'setens', 'sentenes',
    'vuitena', 'vuitè', 'vuitenes', 'vuitens', 'novena', 'novè', 'novenes', 'novens', 'desena', 'desè', 'desenes',
    'desens', 'onzè', 'onzena', 'oncenes', 'oncens', 'dotzena', 'dotzè', 'dotzenes', 'dotzens', 'tretzena', 'tretzè',
    'tretzenes', 'tretzens', 'catorzena', 'catorzè', 'catorzenes', 'catorzens', 'quinzena', 'quinzè', 'quinzenes',
    'quinzens', 'setzena', 'setzè', 'setzenes', 'setzens', 'dissetena', 'dissetè', 'dissetenes', 'dissetens',
    'divuitena', 'divuitè', 'divuitenes', 'divuitens', 'dinovena', 'dinovè', 'dinovenes', 'dinovens', 'vint', 'vintena',
    'vintenes', 'vintens', 'trentena', 'trentè', 'trentenes', 'trentens', 'quarantena', 'quarantè', 'quarentenes',
    'quarantens', 'cinquantena', 'cinquantè', 'cinquantenes', 'cinquantens', 'seixantena', 'seixantè', 'seixantenes',
    'seixentens', 'setantena', 'setantè', 'setentenes', 'sententens', 'vuitantena', 'vuitantè', 'vuitantenes',
    'vuitantens', 'norantena', 'norantè', 'norantenes', 'norantens', 'centena', 'cèntim', 'centèsima', 'centè',
    'milimésima', 'un', 'una', 'dos', 'dues', 'tres', 'quatre', 'cinc', 'sis', 'set', 'vuit', 'nou', 'deu', 'onze',
    'dotze', 'tretze', 'catorze', 'quinze', 'setze', 'disset', 'divuit', 'dinou', 'vint', 'vintiú', 'vintidos',
    'vintitres', 'vintiquatre ', 'vinticinc', 'vintisis', 'vintiset', 'vintivuit', 'vintinou', 'trenta', 'quaranta',
    'cinquanta', 'seixanta', 'setanta', 'vuitanta', 'noranta', 'cent', 'docents', 'dues-centes', 'tres-cents',
    'tres-centes', 'quatre-centes', 'quatre-cents', 'cinc-cents', 'cinc-centes', 'sis-centes', 'sis-cents',
    'vuit-centes', 'vuit-cents', 'nou-centes', 'nou-cents', 'mil', 'milers', 'milió', 'milions', 'bilió', 'bilions'))

partitive_particle = equality_checker("de")
