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

from re import escape

punct = {
    "apostrophe": "'`´’",
    "single_quote": "‘´’",
    "hyphen": "-–—",
    "period": ".",
    "period_centered": "·",
    "comma": ",",
    "slash": "/",
    "question": "?",
    "exclam": "!",
    "parentheses": "()",
    "brackets": "[]",
    "braces": "{}",
}
for i in punct:
    punct[i] = escape(punct[i])

alpha = {
    'lower': "a-zà-ÿ"
}
alpha['upper'] = alpha['lower'].upper()
alpha['letter'] = alpha['lower'] + alpha['upper']
