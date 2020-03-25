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
plural = list_checker(('elles', 'ells', 'les', 'els', 'meves', 'meus', 'ens', 'nosaltres', 'nostres', 'seves', 'seus', 'teves', 'teus', 'vostès', 'vosaltres', 'vostres', 'nostros', 'vostros'))

# from Freeling dict P[PDXITR][123][MFCN]S.*'
# singular = list_checker(('conmigo', 'contigo', 'él', 'ella', 'la', 'le', 'lo', 'me', 'mía', 'mí', 'mío', 'nuestra',
#                          'nuestro', 'nuestro', 'suya', 'suyo', 'suyo', 'te', 'ti', 'tú', 'tuya', 'tuyo', 'tuyo',
#                          'usted', 'vos', 'vuestra', 'vuestro', 'vuestro', 'yo'))
singular = list_checker(('ell', 'ella', 'la', 'li', 'meva', 'meu', 'seva', 'seu', 'seua', 'vostè', 'tu', 'teua', 'teu', 'vós', 'vostra', 'vostre', 'jo'))

# from Freeling dict P[PDXITR][123]F.*'
# female = list_checker(('ella', 'ellas', 'la', 'las', 'mía', 'mías', 'nosotras', 'nuestra', 'nuestras', 'suyas', 'suya',
#                        'tuyas', 'tuya', 'vosotras', 'vuestras', 'vuestra'))
female = list_checker(('ella', 'elles', 'la', 'les', 'nostra', 'meva', 'teva', 'seva', 'meua', 'teua', 'seua'))

# from Freeling dict P[PDXITR][123]M.*
# male = list_checker(('él', 'ellos', 'lo', 'los', 'mío', 'míos', 'nosotros', 'nuestro', 'nuestros', 'suyos', 'suyo',
#                      'tuyos', 'tuyo', 'vosotros', 'vuestros', 'vuestro'))
male = list_checker(('ell', 'ells', 'meu', 'meus', 'nostre', 'nostres', 'seu', 'seus', 'vostre', 'vostres'))


# from Freeling dict P[PDXITR][123][CN].*
# neutral = list_checker(('conmigo', 'consigo', 'contigo', 'le', 'les', 'lo', 'me', 'mía', 'mío', 'nos', 'nuestro', 'os',
#                         'se', 'sí', 'suyo', 'te', 'ti', 'tú', 'tuyo', 'ustedes', 'usted', 'vos', 'vuestro', 'yo'))
neutral = list_checker(('vostè', 'tu', 'teu', 'vostès', 'vos', 'vostre', 'jo'))

# from Freeling dict P[PDXITR][123].* and manually remove the ones used for inanimate too
animate = list_checker(('ell', 'ella', 'elles', 'ells', 'li', 'els', 'em', 'ens', 'nosaltres', 'us', 'vostè', 'tu', 'vostès', 'vostè', 'vosaltres', 'vos', 'jo'))

# from Freeling dict P[PDXITR][123].* and manually removing the ones used for animate too
inanimate = list_checker(('això', 'allò'))

# from Freeling dict PI.*
indefinite = list_checker(('quelcom', 'algú', 'alguna', 'algunes', 'algun', 'alguns', 'ambdues', 'ambdós', 'bastant', 'bastants', 
	'qualssevol', 'qualsevol', 'altres', 'massa', 'mitja', 'mitjans', 'mateixa',' mateixes ',' mateix ', 'mateixos', 'molta', 
	'moltes', 'molt', 'molts', 'res', 'ningú', 'cap', 'gens', 'ningú', 'ninguns', 'altres', 'altre', 'poca', 'poques', 'poc',
	'pocs', 'qualsevol', 'tantes', 'tanta', 'tants', 'tant', 'totes', 'tota', 'tots', 'tot', 'unes', 'una', 'uns', 'un', 'diverses', 'diversos'))

# from Freeling dict PR.*
relative = list_checker(('on', 'com', 'qui', 'quins', 'quan', 'quanta', 'quantes', 'quants', 'que', 'qui', 'quins'))

reflexive = matcher(r'^[^\s]* mism(o|a)s?$')

no_organization = fail()

first_person = list_checker(("em", "meva", "meves", "me", "meu", "meu", "meus", "meues", "ens", "ens", "nosaltres", "nosaltres", "nostra", "nostres", "nostre", "jo"))

second_person = list_checker(("us", "et", "tu", "teves", "teva", "teus", "teu", "teues", "vostès", "vostè", "vosaltres", "vós", "vostres", "vostra", "vostres", "vostre"))

third_person = list_checker(("ell", "ella", "elles", "ells", "la", "les", "li", "els", "el", "seves", "seva", "seus", "seu", "seues"))

pleonastic = list_checker(("això", "_"))

all = lambda x: first_person(x) or second_person(x) or third_person(x) or  plural(x) or singular(x) or male(x) or\
				female(x) or neutral(x) or animate(x) or inanimate(x)