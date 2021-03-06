# coding=utf-8
from corefgraph.resources.lambdas import list_checker

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


temporals = list_checker(("segundo", "minuto", "hora", "día", "semana", "mes", "año", "década", "siglo", "milenio",
             "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo", "ahora",
             "ayer", "mañana", "edad", "tiempo", "era", "época", "noche", "mediodía", "tarde",
             "semestre", "trimestre", "cuatrimestre", "término", "invierno", "primavera", "verano", "otoño", "estación",
             "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
             "noviembre", "diciembre"))
