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
    "elleux",
    # les pronoms dit 'adverbiaux'. p.ex. "allons-y", "prends-en".
    # j'ajoute un negative-forehead hyphen pour des cas comme Villard-le-bois et Bise-en-Bulle.
    r"en(?![{hyphen}])",
    "ce",
    "y",
    # les pronoms 'compléments'. p.ex. "écoutons-les"
    # r"la(?![{hyphen}])",
    # r"le(?![{hyphen}])",
    # r"les(?![{hyphen}])",
    "la",
    "le",
    "les",
    # deux pronoms objet personnels élisés, avec un regex qui permet d'ajouter une condition pour les prendre en compte. je les ajoute pour des cas un peu plus compliqués qui mêlent élision et tiret d'inversion. p.ex. "a-t-il", "pourra-t'on"
    r"t[{hyphen}]??[{apostrophe}]?",
    r"m[{apostrophe}]?",  # p.ex. "dis-m'en plus"
    # également deux adverbes
    "là",  # celle-là
    "ci",  # celle-ci
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
    # j'enlève 'le' pour l'instant, car il faudrait dire seulement pour · et ., sinon "prends-le" va pas être tokenizé correctement
    # "le",  # intellectuelle
    "lle",  # ?
    "le",  # ?
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
