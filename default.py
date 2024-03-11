from re import escape
from dataclasses import dataclass


@dataclass
class Chars:
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

    APOSTROPHES = escape("'`´’")
    SINGLE_QUOTES = escape("‘´’")
    HYPHENS = escape("-–—")
    PERIOD = escape(".")
    PERIOD_CENTERED = escape("·")
    PARENTHESES = escape("()")
    BRACKETS = escape("[]")
    BRACES = escape("{}")
    COMMA = escape(",")
    SLASH = escape("/")
    QUESTION = escape("?")
    EXCLAM = escape("!")
    ALPHA_LOWER = "a-zà-ÿ"
    ALPHA_UPPER = ALPHA_LOWER.upper()
    ALPHA = ALPHA_LOWER + ALPHA_UPPER


@dataclass
class Words:
    """
    1. inversion
    ============

    les mots qui précèdent les traits d'union

    essentiellement des pronoms mais aussi des adverbes.

    2. elision
    ==========

    les mots élisés qui doivent être analysés comme des tokens séparés.

    en priorité, il s'agit de mots extrêmement courants: déterminants, pronoms, négation, conjonction.
    il y a ensuite d'autres mots tout aussi courants, quoiqu'un peu plus rares (et longs), qui contiennent tous la conjonction "qu[e]".

    3. écriture inclusive
    =====================

    liste de suffixes pour l'écriture inclusives.
    """

    INVERSION = [
        # les pronoms sujets. p.ex. "que vois-je"
        "je",
        "tu",
        "on",
        "nous",
        "vous",
        "elle",
        "il",
        "ils",
        "elles",
        # j'inclus "iel", qu'on retrouve évidemment sur le web.
        "iel",
        "iels",
        # les pronoms objets dont la forme est différente des pronoms sujets. p.ex "arrête-moi si je me trompe".
        "moi",
        "toi",
        "lui",
        "leur",
        "eux",
        # les pronoms dit 'adverbiaux'. p.ex. "allons-y", "prends-en".
        # j'ajoute un negative-forehead hyphen pour des cas comme Villard-le-bois et Bise-en-Bulle.
        r"en(?![{hyphen}])",
        "y",
        # les pronoms 'compléments'. p.ex. "écoutons-les"
        r"la(?![{hyphen}])",
        r"le(?![{hyphen}])",
        r"les(?![{hyphen}])",
        # deux pronoms objet personnels élisés, avec un regex qui permet d'ajouter une condition pour les prendre en compte. je les ajoute pour des cas un peu plus compliqués qui mêlent élision et tiret d'inversion. p.ex. "a-t-il", "pourra-t'on"
        r"t[{hyphen}]??[{apostrophe}]?",
        r"m[{apostrophe}]?",  # p.ex. "dis-m'en plus"
        # également deux adverbes
        "là",
        "ici",
    ]

    ELISION = [
        "n",  # ne
        "s",  # se
        "c",  # ce
        "d",  # de
        "j",  # je
        "m",  # me
        "t",  # tu, te
        "l",  # la, le
        "qu",  # que
        # "quelqu" reçoit un traitement particulier pour être cohérent avec "quelques-une"
        r"quelqu(?![{apostrophe}]un[exs]*\b)",  # quelque
        "jusqu",  # jusque
        "presqu",  # presque
        "lorsqu",  # lorsque
        "puisqu",  # puisque
        "quoiqu",  # quoique
    ]

    SUFF_FEMININE = [
        "e",  # chacune
        "le",  # intellectuelle
        "lle",  # ?
        "te",  # toute
        "tte",  # ?
        "euse",  # chercheur.euse
        "ère",  # usager.ère
        "ice",  # acteur.ice
        "rice",  # acteur.rice
        "trice",  # aut.trice
        "ale",  # élu.e local.e
        "ne",  # citoyen.ne
        "ive",  # créatif.ive
        "esse",  # ?
        "oresse",  # docteur.oresse
        "se",  # curieux.se
        "fe",  # cheffe
    ]

    SUFF_PLURAL = ["s", "x"]

    SUFF_NONBINARY = ["x"]
