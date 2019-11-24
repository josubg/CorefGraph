# coding=utf-8
""" List of verbs used in sieves and mention detection.
"""

from corefgraph.resources.lambdas import list_checker, equality_checker

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

# Source: Are based on list found Stanford CoreLP, also it may been modified.
_ser = list_checker((
    'ser', 'erais', 'éramos', 'eran', 'era', 'era', 'eras', 'eres', 'es', 'fuerais', 'fuéramos', 'fueran', 'fuera',
    'fuera', 'fueras', 'fuereis', 'fuéremos', 'fueren', 'fuere', 'fuere', 'fueres', 'fueron', 'fueseis', 'fuésemos',
    'fuesen', 'fue', 'fuese', 'fuese', 'fueses', 'fuimos', 'fui', 'fuisteis', 'fuiste', 'seréis', 'seamos', 'seamos',
    'sean', 'sean', 'sea', 'sea', 'sea', 'seas', 'sed', 'serían', 'sería', 'serías', 'seriáis', 'seremos', 'ser',
    'seráis', 'seríamos', 'serán', 'será', 'seré', 'serás', 'ser', 'sé', 'sido', 'siendo', 'sois', 'somos', 'son',
    'soy'))

_estar = list_checker((
    'estoy', 'estás', 'está', 'estamos', 'estáis', 'están', 'estaba', 'estabas', 'estaba', 'estábamos', 'estabais',
    'estaban', 'estaré', 'estarás', 'estará', 'estaremos', 'estaréis', 'estarán', 'estaría', 'estarías', 'estaría',
    'estaríamos', 'estaríais', 'estarían', 'estuve', 'estuviste', 'estuvo', 'estuvimos', 'estuvisteis', 'estuvieron',
    'esté', 'estés', 'esté', 'estemos', 'estéis', 'estén', 'estuviera' 'estuvieras', 'estuviera', 'estuviéramos',
    'estuvierais', 'estuvieran' 'estuviese', 'estuvieses', 'estuviese', 'estuviésemos', 'estuvieseis',
    'estuviesen' 'estuviere', 'estuvieres', 'estuviere', 'estuviéremos', 'estuviereis', 'estuvieren' 'está', 'esté',
    'estemos', 'estad', 'estén', 'estar', 'estando', 'estado'))

_parecer = list_checker((
    'parezco', 'pareces', 'parece', 'parecemos', 'parecéis', 'parecen', 'parecía', 'parecías', 'parecía', 'parecíamos',
    'parecíais', 'parecían', 'pareceré', 'parecerás', 'parecerá', 'pareceremos', 'pareceréis', 'parecerán', 'parecería',
    'parecerías', 'parecería', 'pareceríamos', 'pareceríais', 'parecerían', 'parecí', 'pareciste', 'pareció',
    'parecimos',
    'parecisteis', 'parecieron', 'parezca', 'parezcas', 'parezca', 'parezcamos', 'parezcáis', 'parezcan', 'pareciera',
    'parecieras', 'pareciera', 'pareciéramos', 'parecierais', 'parecieran', 'pareciese', 'parecieses', 'pareciese',
    'pareciésemos', 'parecieseis', 'pareciesen', 'pareciere', 'parecieres', 'pareciere', 'pareciéremos', 'pareciereis',
    'parecieren', 'parece', 'parezca', 'parezcamos', 'pareced', 'parezcan', 'parecer', 'pareciendo', 'parecido'))

copulative = lambda x: _ser(x) or _estar(x) or _parecer(x)

# From StanfordCoreNLP
reporting = list_checker((
    "acusar", "reconocer", "añadir", "admitir", "aconsejar", "acordar", "alertar",
    "alegar", "anunciar", "responder", "disculpar", "discutir",
    "preguntar", "afirmar", "asegurar", "suplicar", "rogar", "culpar", "jactar",
    "Precaución", "carga", "citar", "reclamo", "aclarar", "ordenar", "comentar",
    "comparar", "quejar", "reclamar", "explicar", "reconocer", "concluir", "confirmar", "enfrentar", "felicitar",
    "argüir", "sostener", "contradecir", "replicar", "transmitir", "expreso", "criticar",
    "debatir", "decidir", "declarar", "defender", "demandar", "demostrar", "negar",
    "describir", "determinar", "discrepar", "diferir", "disientir", "revelar", "discutir",
    "descartar", "disputar", "ignorar", "dudar", "enfatizar", "animar", "apoyar",
    "comparar", "estimar", "esperar", "explicar", "expresar", "ensalzar", "temer", "sentir",
    "buscar", "prohibir", "preveer", "predecir", "olvidar", "deducir", "garantizar", "adivinar",
    "oir", "indicar", "desear", "ilustrar", "imaginar", "insinuar", "indicar", "informar",
    "insistir", "instruir", "intérprete", "entrevista", "invitar", "publico",
    "justificar", "aprender", "mantener", "mediar", "mencionar", "negociar", "anotar",
    "observar", "ofrecer", "oponer", "ordenar", "persuadir", "prometer", "puntualizar", "señalar",
    "alabar", "rezar", "predecir", "presentar", "prometer", "enviar", "proponer",
    "protestar", "probar", "provocar", "preguntar", "citar", "pensar", "creer", "leer",
    "reafirmar", "saber", "refutar", "recordar", "reconozer", "recomendar", "referirse",
    "reflexionar", "rechazar", "refutar", "reiterar", "rechazar", "relacionarse", "observación",
    "recordar", "repetir", "respuesta", "denunciar", "solicitar", "responder",
    "reformular", "revelar", "reglar", "decir", "mostrar", "señal", "cantar",
    "especular", "difundir", "enuciar", "manifestar", "exponer", "estipular", "enfatizar",
    "sugerir", "apoyar", "suponer", "conjeturar", "sospechar", "jurar", "enseñar",
    "decir", "testificar", "pensar", "amenazar", "descubrir", "subrayar",
    "destacar", "enfatizar", "urguir", "expresar", "jurar", "prometer", "avisar", "saludar",
    "desear", "cuestionar", "preocupar", "escribir"
))

generics_you_verbs = equality_checker("sabes")

pleonastic_verbs = list_checker(("ser", "estar", "parecer", "explicar"))
