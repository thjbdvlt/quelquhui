"""
1. signes de ponctuations
=========================

1.1) inclut certaines variantes, par exemple les apostrophes courbes et droites, les différents tirets, car il peut s'agir de variantes signifiantes; mais en exclut d'autres, par exemple les autres caractères unicode qui sont des parenthèses, car il ne s'agit pas de variantes signifiantes: le passage de ces variantes à caractère standard peut facilement être fait en preprocessing; et il vaut mieux, à mon avis, adapter ponctuellement le comportement du tokenizer pour les cas qui présentent de telles variantes, que d'inclure ces signes par défaut.
1.2) je place dans les apostrophes certains signes qui sont en fait des 'single quote', car elles peuvent être (et je crois qu'elles sont souvent) utilisées ainsi.

2. caractères alphabétiques
===========================

2.1) inclut les caractères accentués mais excluant les nombres.
2.2) utile surtout pour, dans une 'regular expression', distinguer entre majuscule et minuscule (substitut à `str.is_upper()`).
"""

import re

APOSTROPHE = re.escape("'`´’")
SINGLE_QUOTE = re.escape("‘´’")
HYPHEN = re.escape("-–—")
PERIOD = re.escape(".")
PERIOD_CENTERED = re.escape("·")
PARENTHESES = re.escape("()")
BRACKETS = re.escape("[]")
BRACES = re.escape("{}")
COMMA = re.escape(",")
SLASH = re.escape("/")
QUESTION = re.escape("?")
EXCLAM = re.escape("!")
ALPHA_LOWER = "a-zà-ÿ"
ALPHA_UPPER = ALPHA_LOWER.upper()
ALPHA = ALPHA_LOWER + ALPHA_UPPER
ALPHA_NOT_A = "b-zB-Z"
