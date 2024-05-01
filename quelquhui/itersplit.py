from typing import Callable, Iterable, Generator


def alternatelabel(label) -> Generator:
    """alternativement un label et None"""
    while True:
        yield None
        yield label


def alternatefalsetrue() -> Generator:
    """alternativement False et True"""
    while True:
        yield False
        yield True


def itersplitlabel(
    text: str,
    splitspace: Callable,
    itersplit: Iterable[tuple[Callable, str]],
) -> list[str]:
    """split itérativement un texte à l'aide d'une liste de fonction.

    à chaque fonction (sauf la première, qui split sur les espace), est associé un label qui sera attribué aux tokens extraits par la fonction. il peut typiquement s'agir d'un sous-type de token, par exemple 'emoticon' ou 'url'."""

    # split d'abord sur les espaces, sans les conserver.
    s = splitspace(text)
    # au départ, aucun mot n'est gelé au départ.
    s = list(zip(s, len(s) * [None]))
    # itération sur les fonctions de splitting. l'ordre est important: une fois qu'un élément extrait est extrait comme étant un token par l'une des fonctions, les fonctions suivantes ne le modifieront plus (le token est gelé).
    for fn, fnlabel in itersplit:
        # itération sur les segments de textes (les tokens en devenir).
        for n, (i, tokenlabel) in enumerate(s):
            # ne pas modifié les tokens gelés
            if tokenlabel is None:
                # split à l'aide de la fonction
                x = fn(i)
                # si la longueur de la nouvelle liste est supérieur à 1, alors la fonction a modifié quelque chose: les segments extraits sont isolés et gelés, et l'ancien segment est remplacé dans la liste des segments.
                if len(x) > 1:
                    s[n] = list(zip(x, alternatelabel(fnlabel)))
                    continue
            # sinon (si le token est gelé ou si la liste a une longueur de 1) alors le segment est simplement remplacé par une liste ne contenant que lui-même.
            s[n] = [(i, tokenlabel)]
        # unnest la nested list.
        s = [x for y in s for x in y]
    # ne conserver que les segments non-vides
    noempty = [i for i in s if i[0] != ""]
    # les textes
    tokens = [i[0] for i in noempty]
    # les labels
    labels = [i[1] for i in noempty]
    return tokens, labels


def itersplit(
    text: str, splitspace: Callable, itersplit: Iterable[Callable]
) -> list[str]:
    """split itérativement un texte à l'aide d'une liste de fonction."""

    # split d'abord sur les espaces, sans les conserver.
    s = splitspace(text)
    # au départ, aucun mot n'est gelé au départ.
    s = list(zip(s, len(s) * [False]))
    # itération sur les fonctions de splitting. l'ordre est important: une fois qu'un élément extrait est extrait comme étant un token par l'une des fonctions, les fonctions suivantes ne le modifieront plus (le token est gelé).
    for fn in itersplit:
        # itération sur les segments de textes (les tokens en devenir).
        for n, i in enumerate(s):
            # ne pas modifié les tokens gelés
            if i[1] is False:
                # split à l'aide de la fonction
                x = fn(i[0])
                # si la longueur de la nouvelle liste est supérieur à 1, alors la fonction a modifié quelque chose: les segments extraits sont isolés et gelés, et l'ancien segment est remplacé dans la liste des segments.
                if len(x) > 1:
                    s[n] = list(zip(x, alternatefalsetrue()))
                    continue
            # sinon (si le token est gelé ou si la liste a une longueur de 1) alors le segment est simplement remplacé par une liste ne contenant que lui-même.
            s[n] = [i]
        # unnest la nested list.
        s = [x for y in s for x in y]
    # les textes
    return [i[0] for i in s if i[0] != ""]
