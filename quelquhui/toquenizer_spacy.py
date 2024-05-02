from spacy.tokens import Doc
from spacy.vocab import Vocab
from typing import Callable, Iterable
from quelquhui.itersplit import alternatefalsetrue, infinitefalse


def wherespaces(spacesidx: list[int], words: list[str]):
    n = idx = 0
    spaces = []
    lo = [len(i) for i in words]
    for i in lo:
        idx += i
        if spacesidx[n] == idx:
            spaces.append(True)
        else:
            spaces.append(False)
    return spaces


class QQSpacyToquenizer:
    def __init__(
        self,
        splitspace: Callable,
        splitwords: Iterable[Callable],
        findborder: Callable,
        findfreeze: Callable,
        vocab: Vocab = None,
        **kwargs,
    ):
        if vocab is None:
            vocab = Vocab(**kwargs)
        self.vocab = vocab
        self.splitspace = splitspace
        self.splitpatterns = splitwords
        self.findborder = findborder
        self.findfreeze = findfreeze

    def itersplit(self, word: list[tuple]) -> list[str]:
        """split itérativement un mot à l'aide d'une liste de fonction."""

        # itération sur les fonctions de splitting. l'ordre est important: une fois qu'un élément extrait est extrait comme étant un token par l'une des fonctions, les fonctions suivantes ne le modifieront plus (le token est gelé).
        words = [word]
        for fn in self.splitpatterns:
            search, split = fn.search, fn.split
            words = (
                zip(split(i[0]), alternatefalsetrue())
                if i[1] is False and search(i[0])
                else [i]
                for i in words
            )
            # unnest la nested list et enlève les éléments vides
            words = [x for y in words for x in y if x[0] != ""]
        return words

    def findsplit(self, substring: str) -> list[str]:
        """split a substring into many using two functions: one that find potential boundaries, and another one that find some exceptions that will be substract for the boundaries."""
        # find borders
        s = set().union(
            *[(i.start(), i.end()) for i in self.findborder(substring)]
        )
        # find exceptions, and remove exceptions from borders
        s.difference_update(
            *[
                range(i.start(), i.end())
                for i in self.findfreeze(substring)
            ]
        )
        if len(s) == 0:
            # if no borders remains, return substring without any change
            return [substring]
        # else, add all parts one after the other. add 0 and len(substring.text) to ensure all text is kept.
        s.update([0, len(substring)])
        x = sorted(s)
        words = [
            substring[i : x[n + 1]] for n, i in enumerate(x[:-1])
        ]
        return words

    def tokenize(self, text: str, **kwargs) -> Doc:
        # 1. split text on spaces, then re-split with self.split functions.
        # 2. for each substring:
        #    2.1 find characters to split on.
        #    2.2 find characters found in 2.1 but not to split on.
        #    2.3 split on 2.1 - 2.2
        # freeze = self.freeze
        # findborder = self.findborder
        # split on spaces, then eventually split on url, then emoji, then emoticon (or using other split rules submitted in split_patterns).
        nonspace = list(zip(self.splitspace(text), infinitefalse()))
        # si le dernier token est "", alors c'est que le texte termine par un espace. cela nécessite quelques ajustements pour la suite
        if nonspace[-1][0] == "":
            nonspace = nonspace[:-1]
            nonspace[-1] = (nonspace[-1][0], True)
        words = []
        for i in nonspace:
            x = self.itersplit(i)
            subwords = [self.findsplit(word[0]) if word[1] is False else [word[0]] for word in x]
            words.append([a for u in subwords for a in u])
        # créer une liste qui dit si les mots sont suivis ou non par des espaces.
        spaces = [[False] * (len(i) - 1) + [True] for i in words]
        # unnest both lists: first, spaces.
        spaces = [x for y in spaces for x in y]
        words = [x for y in words for x in y]
        # to avoid error. returns empty docs before the end of the processing.
        if len(words) == 0:
            return Doc(words=[], spaces=[], vocab=self.vocab)
        else:
            return Doc(
                words=words, spaces=spaces, vocab=self.vocab, **kwargs
            )

    def __call__(self, text: str, **kwargs) -> Doc:
        return self.tokenize(text, **kwargs)
