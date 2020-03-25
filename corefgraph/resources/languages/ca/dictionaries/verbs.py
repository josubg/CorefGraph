# coding=utf-8
""" List of verbs used in sieves and mention detection.
"""

from corefgraph.resources.lambdas import list_checker, equality_checker

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

# Source: Are based on list found Stanford CoreLP, also it may been modified.
_ser = list_checker((
#    'ser', 'erais', 'éramos', 'eran', 'era', 'era', 'eras', 'eres', 'es', 'fuerais', 'fuéramos', 'fueran', 'fuera',
#    'fuera', 'fueras', 'fuereis', 'fuéremos', 'fueren', 'fuere', 'fuere', 'fueres', 'fueron', 'fueseis', 'fuésemos',
#    'fuesen', 'fue', 'fuese', 'fuese', 'fueses', 'fuimos', 'fui', 'fuisteis', 'fuiste', 'seréis', 'seamos', 'seamos',
#    'sean', 'sean', 'sea', 'sea', 'sea', 'seas', 'sed', 'serían', 'sería', 'serías', 'seriáis', 'seremos', 'ser',
#    'seráis', 'seríamos', 'serán', 'será', 'seré', 'serás', 'ser', 'sé', 'sido', 'siendo', 'sois', 'somos', 'son',
#    'soy'))
	'ser', 'éreu', 'érem', 'eren', 'eran', 'era', 'eres', 'ets', 'és', 'fóssiu', 'fóssim', 'fossin', 'fou', 'fossis', 'fos', 
	'fórem', 'siguin', 'sigui', 'siguis', 'siguem', 'sigueu', 'serieu', 'serem', 'sereu', 'seria', 'serian', 'seríem', 'seré', 'seràs', 'ser',
        'sé', 'estat', 'ets', 'es', 'sent', 'sou', 'som', 'són', 'sóc'))

_estar = list_checker((
#    'estoy', 'estás', 'está', 'estamos', 'estáis', 'están', 'estaba', 'estabas', 'estaba', 'estábamos', 'estabais',
#    'estaban', 'estaré', 'estarás', 'estará', 'estaremos', 'estaréis', 'estarán', 'estaría', 'estarías', 'estaría',
#    'estaríamos', 'estaríais', 'estarían', 'estuve', 'estuviste', 'estuvo', 'estuvimos', 'estuvisteis', 'estuvieron',
#    'esté', 'estés', 'esté', 'estemos', 'estéis', 'estén', 'estuviera' 'estuvieras', 'estuviera', 'estuviéramos',
#    'estuvierais', 'estuvieran' 'estuviese', 'estuvieses', 'estuviese', 'estuviésemos', 'estuvieseis',
#    'estuviesen' 'estuviere', 'estuvieres', 'estuviere', 'estuviéremos', 'estuviereis', 'estuvieren' 'está', 'esté',
#    'estemos', 'estad', 'estén', 'estar', 'estando', 'estado'))
	'estic', 'estàs', 'està', 'estem', 'esteu', 'estan', 'estava', 'estaves', 'estava', 'estàvem', 'estàveu', 
	'estaven', 'estaré', 'estaràs', 'estarà', 'estarem', 'estareu', 'estaran', 'estaria', 'estaries', 'estaria', 
	'estaríem', 'estaríeu', 'estarien', 'estar', 
	'estigui', 'estiguis', 'estigui', 'estiguem', 'estigueu', 'estiguin', 'estigués', 'estiguessis', 'estigués', 
	'estiguéssim', 'estiguéssiu', 'estiguessin' 'estigués', 'estiguessis', 
	'estar', 'estant', 'estat'))

_parecer = list_checker((
#    'parezco', 'pareces', 'parece', 'parecemos', 'parecéis', 'parecen', 'parecía', 'parecías', 'parecía', 'parecíamos',
#    'parecíais', 'parecían', 'pareceré', 'parecerás', 'parecerá', 'pareceremos', 'pareceréis', 'parecerán', 'parecería',
#    'parecerías', 'parecería', 'pareceríamos', 'pareceríais', 'parecerían', 'parecí', 'pareciste', 'pareció',
#    'parecimos',
#    'parecisteis', 'parecieron', 'parezca', 'parezcas', 'parezca', 'parezcamos', 'parezcáis', 'parezcan', 'pareciera',
#    'parecieras', 'pareciera', 'pareciéramos', 'parecierais', 'parecieran', 'pareciese', 'parecieses', 'pareciese',
#    'pareciésemos', 'parecieseis', 'pareciesen', 'pareciere', 'parecieres', 'pareciere', 'pareciéremos', 'pareciereis',
#    'parecieren', 'parece', 'parezca', 'parezcamos', 'pareced', 'parezcan', 'parecer', 'pareciendo', 'parecido'))
	'semblo', 'sembles', 'sembla', 'semblem', 'sembleu', 'semblen', 'semblava', 'semblaves', 'semblava', 'semblàvem', 
	'semblàvau', 'semblaven', 'semblaré', 'semblaràs', 'semblarà', 'semblarem', 'semblareu', 'semblaran', 'semblaria', 
	'semblaries', 'semblaria', 'semblaríem', 'semblariau', 'semblarien', 'semblar', 'sembli', 'semblis', 'sembleu', 
	'semblem', 'sembleu', 'semblin', 'semblés', 'semblesis', 'semblés', 'semblesiu', 'semblessin', 'sembla'))


copulative = lambda x: _ser(x) or _estar(x) or _parecer(x)

# From StanfordCoreNLP
reporting = list_checker((
#    "acusar", "reconocer", "añadir", "admitir", "aconsejar", "acordar", "alertar",
#    "alegar", "anunciar", "responder", "disculpar", "discutir",
#    "preguntar", "afirmar", "asegurar", "suplicar", "rogar", "culpar", "jactar",
#    "Precaución", "carga", "citar", "reclamo", "aclarar", "ordenar", "comentar",
#    "comparar", "quejar", "reclamar", "explicar", "reconocer", "concluir", "confirmar", "enfrentar", "felicitar",
#    "argüir", "sostener", "contradecir", "replicar", "transmitir", "expreso", "criticar",
#    "debatir", "decidir", "declarar", "defender", "demandar", "demostrar", "negar",
#    "describir", "determinar", "discrepar", "diferir", "disientir", "revelar", "discutir",
#    "descartar", "disputar", "ignorar", "dudar", "enfatizar", "animar", "apoyar",
#    "comparar", "estimar", "esperar", "explicar", "expresar", "ensalzar", "temer", "sentir",
#    "buscar", "prohibir", "preveer", "predecir", "olvidar", "deducir", "garantizar", "adivinar",
#    "oir", "indicar", "desear", "ilustrar", "imaginar", "insinuar", "indicar", "informar",
#    "insistir", "instruir", "intérprete", "entrevista", "invitar", "publico",
#    "justificar", "aprender", "mantener", "mediar", "mencionar", "negociar", "anotar",
#    "observar", "ofrecer", "oponer", "ordenar", "persuadir", "prometer", "puntualizar", "señalar",
#    "alabar", "rezar", "predecir", "presentar", "prometer", "enviar", "proponer",
#    "protestar", "probar", "provocar", "preguntar", "citar", "pensar", "creer", "leer",
#    "reafirmar", "saber", "refutar", "recordar", "reconozer", "recomendar", "referirse",
#    "reflexionar", "rechazar", "refutar", "reiterar", "rechazar", "relacionarse", "observación",
#    "recordar", "repetir", "respuesta", "denunciar", "solicitar", "responder",
#    "reformular", "revelar", "reglar", "decir", "mostrar", "señal", "cantar",
#    "especular", "difundir", "enuciar", "manifestar", "exponer", "estipular", "enfatizar",
#    "sugerir", "apoyar", "suponer", "conjeturar", "sospechar", "jurar", "enseñar",
#    "decir", "testificar", "pensar", "amenazar", "descubrir", "subrayar",
#    "destacar", "enfatizar", "urguir", "expresar", "jurar", "prometer", "avisar", "saludar",
#    "desear", "cuestionar", "preocupar", "escribir"
	"acusar", "reconèixer", "afegir", "admetre", "aconsellar", "acordar", "alertar", 
	"al·legar", "anunciar", "respondre", "disculpar", "discutir", 
	"preguntar", "afirmar", "assegurar", "suplicar", "pregar", "culpar", 
	"càrrega", "citar", "reclamar", "aclarir", "ordenar", "comentar", 
	"comparar", "queixar", "reclamar", "explicar", "reconèixer", "concloure", "confirmar", "enfrontar", "felicitar", 
	"sostenir", "contradir", "replicar", "transmetre", "criticar",
	"debatre", "decidir", "declarar", "defensar", "demanar", "demostrar", "negar",
	"descriure", "determinar", "discrepar", "diferir", "disentir", "revelar", "discutir", 
	"descartar", "disputar", "ignorar", "dubtar", "emfatitzar", "animar", "recolsar", 
	"comparar", "estimar", "esperar", "explicar", "expressar", "enaltir", "témer", "sentir",
	"buscar", "prohibir", "preveure", "predir", "oblidar", "deduir", "garantir", "endevinar", 
	"sentir", "escoltar", "indicar", "desitjar", "il·lustrar", "imaginar", "insinuar", "indicar", "informar",
	"insistir", "instruir", "interpretar", "entrevistar", "convidar", "publicar",
	"justificar", "aprendre", "mantenir", "intervenir", "esmentar", "negociar" , "anotar", 
	"observar", "oferir", "oposar", "ordenar", "persuadir", "prometre", "puntualitzar", "assenyalar", 
	"lloar", "resar", "predir", "presentar", "prometre", "enviar", "proposar", 
	"protestar", "provar", "provocar", "preguntar", "citar", "pensar", "creure", "llegir", 
	"reafirmar" , "saber", "refutar", "recordar", "reconeixer", "recomanar", "referir", 
	"reflexionar", "rebutjar", "refutar", "reiterar", "rebutjar", "relacionar-se", "observar", 
	"recordar", "repetir", "respondre", "denunciar", "sol·licitar", 
	"reformular", "revelar", "reglar", "dir", "mostrar", "senyalar" , "cantar", 
	"especular", "difondre", "enunciar", "manifestar", "exposar", "estipular", "emfatitzar", 
	"suggerir", "recolsar", "suposar", "conjecturar", "sospitar", "jurar", "ensenyar",
	"dir", "testificar", "pensar", "amenaçar", "descobrir", "subratllar", 
	"destacar", "emfatitzar", "urguir", "expressar", "jurar", "prometre", "avisa", "saludar",
	"desitjar", "qüestionar", "preocupar", "escriure"
))

generics_you_verbs = equality_checker("saps")

pleonastic_verbs = list_checker(("ser", "estar", "semblar", "explicar"))

