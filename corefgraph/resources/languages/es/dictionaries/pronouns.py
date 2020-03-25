#coding=utf-8
""" This module contains all the list of pronouns form used in the system.

These lists(in fact tuples or sets) are used to detect pronouns and extract function and features of them. Each element
 of these list are a lowercase form of the pronoun .

Language: Spanish
Language-code: ES

Expected list form the system are:

 + all: A list that contains all pronouns of the language

 + Features lists:
     + plural: All undoubtedly
     + singular: All undoubtedly
     + male: All undoubtedly
     + female: All undoubtedly
     + neutral: All undoubtedly
     + animate: All undoubtedly
     + inanimate: All undoubtedly
     + first_person: All undoubtedly
     + second_person: All undoubtedly
     + third_person: All undoubtedly
     + indefinite:  All undoubtedly
 + function lists:
  + relative: All relative pronoun forms.
  + reflexive: All reflexive pronoun forms
 + others list
  + pleonastic: The pronouns that can be pleonastic (http://en.wikipedia.org/wiki/Dummy_pronoun).
  + no_organization: The pronouns that can't match with an organization NE.

Additional or language specific elements:

(Put here any additional list added)

Notes:
 + Mark internal use elements with a initial "_".
 + Use tuples or sets
"""
from corefgraph.resources.lambdas import list_checker, equality_checker, matcher, fail

__author__ = 'Rodrigo Agerri <rodrigo.agerri@ehu.es>'
__date__ = '2013-05-03'


# from Freeling dict (P[PDXITR][123][MFCN]P.*')
# plural = list_checker(('ellas', 'ellos', 'las', 'les', 'los', 'mías', 'míos', 'nos', 'nosotras', 'nosotros', 'nuestras',
#                        'nuestros', 'os', 'suyas', 'suyos', 'tuyas', 'tuyos', 'ustedes', 'vosotras', 'vosotros',
#                        'vuestras', 'vuestros'))
plural = list_checker(('ellas', 'ellos', 'las', 'les', 'los', 'nos', 'nosotras', 'nosotros', 'nuestras',
                        'nuestros', 'os', 'ustedes', 'vosotras', 'vosotros',
                        'vuestras', 'vuestros', 'nuestra', 'nuestro', 'nuestro', 'vuestra', 'vuestro', 'vuestro',))
# from Freeling dict P[PDXITR][123][MFCN]S.*'
# singular = list_checker(('conmigo', 'contigo', 'él', 'ella', 'la', 'le', 'lo', 'me', 'mía', 'mí', 'mío', 'nuestra',
#                          'nuestro', 'nuestro', 'suya', 'suyo', 'suyo', 'te', 'ti', 'tú', 'tuya', 'tuyo', 'tuyo',
#                          'usted', 'vos', 'vuestra', 'vuestro', 'vuestro', 'yo'))
singular = list_checker(('conmigo', 'contigo', 'él', 'ella', 'la', 'le', 'lo', 'me', 'mía', 'mí', 'mío',
                         'te', 'ti', 'tú', 'mías', 'míos', "tus", 'tuya', 'tuyo', 'tuyas', 'tuyos',
                         'usted', 'vos',  'yo', 'mías', 'míos', 'ello'))
# from Freeling dict P[PDXITR][123]F.*'
# female = list_checker(('ella', 'ellas', 'la', 'las', 'mía', 'mías', 'nosotras', 'nuestra', 'nuestras', 'suyas', 'suya',
#                        'tuyas', 'tuya', 'vosotras', 'vuestras', 'vuestra'))
female = list_checker(('ella', 'ellas', 'la', 'las', 'nosotras', 'vosotras',))
# from Freeling dict P[PDXITR][123]M.*
# male = list_checker(('él', 'ellos', 'lo', 'los', 'mío', 'míos', 'nosotros', 'nuestro', 'nuestros', 'suyos', 'suyo',
#                      'tuyos', 'tuyo', 'vosotros', 'vuestros', 'vuestro'))
male = list_checker(('él', 'ellos', 'los', 'nosotros',  'vosotros', ))
# from Freeling dict P[PDXITR][123][CN].*
# neutral = list_checker(('conmigo', 'consigo', 'contigo', 'le', 'les', 'lo', 'me', 'mía', 'mío', 'nos', 'nuestro', 'os',
#                         'se', 'sí', 'suyo', 'te', 'ti', 'tú', 'tuyo', 'ustedes', 'usted', 'vos', 'vuestro', 'yo'))
neutral = list_checker(('lo', 'sí', 'ello'))

# from Freeling dict P[PDXITR][123].* and manually remove the ones used for inanimate too
animate = list_checker(('contigo', 'él', 'ella', 'ellas', 'ellos', 'le', 'les', 'me', 'mí', 'nos', 'nosotras',
                        'nosotros', 'os', 'te', 'ti', 'tí', 'ustedes', 'usted', 'vosotras', 'vosotros', 'vos', 'yo'))
# from Freeling dict P[PDXITR][123].* and manually removing the ones used for animate too
inanimate = list_checker(('lo', 'sí', 'ello', 'esto'))

# from Freeling dict PI.*
indefinite = list_checker(('algo', 'alguien', 'alguna', 'algunas', 'alguno', 'algunos', 'ambas', 'ambos', 'bastante',
                           'bastantes', 'cual', 'cualesquiera', 'cualquiera', 'demás', 'demasiada', 'demasiadas',
                           'demasiado', 'demasiados', 'media', 'medias', 'medio', 'medios', 'misma', 'mismas', 'mismo',
                           'mismos', 'mucha', 'muchas', 'mucho', 'muchos', 'nada', 'nadie', 'naide', 'ninguna',
                           'ningunas', 'ninguno', 'ningunos', 'otra', 'otras', 'otro', 'otros', 'poca', 'pocas', 'poco',
                           'pocos', 'quienesquiera', 'quienquiera', 'tantas', 'tanta', 'tantos', 'tanto', 'todas',
                           'toda', 'todos', 'todo', 'unas', 'una', 'unos', 'uno', 'varias', 'varios'))

# from Freeling dict PR.*
relative = list_checker(('adonde', 'como', 'cual', 'cuales', 'cuando', 'cuanta', 'cuantas', 'cuanto', 'cuantos', 'cuya',
                         'cuyas', 'cuyo', 'cuyos', 'donde', 'que', 'quienes', 'quien',
                         "el que", "los que", "la que", "las que", "lo que"))

reflexive = matcher(r'^[^\s]* mism(o|a)s?$')

no_organization = fail()

first_person = list_checker(("conmigo", "me", "me", "mía", "mías", "mí", "mío", "mío", "míos", "nos", "nos", "nosotras",
                             "nosotros", "nuestra", "nuestras", "nuestro", "nuestro", "nuestros", "yo",))

second_person = list_checker(("contigo", "os", "os", "te", "te", "ti", "tú", "tuyas", "tuya", "tuyos", "tuyo", "tuyo", 
                              "ustedes", "usted", "vosotras", "vosotros", "vos", "vuestras", "vuestra", "vuestros", 
                              "vuestro", "vuestro", ))

third_person = list_checker(("consigo", "él", "ella", "ellas", "ellos", "la", "las", "le", "les", "lo", "lo", "los",
                             "se", "se", "sí", "suyas", "suya", "suyos", "suyo", "suyo",))


all = list_checker(("_", "su", "sus", "suyos"))

pleonastic = list_checker(("eso", "_"))
