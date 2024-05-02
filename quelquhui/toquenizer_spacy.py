from spacy.tokens import Doc
from spacy.vocab import Vocab
from typing import Callable, Iterable
from quelquhui.itersplit import alternatefalsetrue, infinitefalse


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

    def itersplit(self, words: Iterable[tuple]) -> Iterable[str]:
        """split itérativement un mot à l'aide d'une liste de fonction."""

        # itération sur les fonctions de splitting. l'ordre est important: une fois qu'un élément extrait est extrait comme étant un token par l'une des fonctions, les fonctions suivantes ne le modifieront plus (le token est gelé).
        for fn in self.splitpatterns:
            search, split = fn.search, fn.split
            words = (
                zip(split(i[0]), alternatefalsetrue())
                if i[1] is False and search(i[0])
                else [i]
                for i in words
            )
            # unnest la nested list et enlève les éléments vides
            words = (x for y in words for x in y if x[0] != "")
        return words

    def findsplit(self, substring: str) -> list[str]:
        """split a substring into many using two functions: one that find potential boundaries, and another one that find some exceptions that will be substract for the boundaries."""

        # find borders, typically: punctuation.
        s = set().union(
            *[(i.start(), i.end()) for i in self.findborder(substring)]
        )

        # find exceptions, and remove exceptions from borders. for example: inword parenthese(s)
        s.difference_update(
            *[
                range(i.start(), i.end())
                for i in self.findfreeze(substring)
            ]
        )

        if len(s) == 0:
            # if no borders remains, return substring without any change
            return [substring]

        # else, add all subwords
        s.update([0, len(substring)])
        x = sorted(s)
        words = []
        prev = 0
        for i in x[1:]:
            words.append(substring[prev:i])
            prev = i

        return words

    def findidxspaces(self, words: list[str]) -> list[int]:
        spaces = []
        n = 0
        for i in words[:-1]:
            n += len(i)
            spaces.append(n)
        return spaces

    def tokenize(self, text: str, **kwargs) -> Doc:
        """tokenize a text."""

        a = self.splitspace(text)
        nonspace = zip(a, infinitefalse())
        words = self.itersplit(nonspace)
        words = (i[0] if i[1] is True else self.findsplit(i[0]) for i in words)
        words = [x for y in words for x in y]

        # créer une liste qui dit si les mots sont suivis ou non par des espaces.
        spaces_after_idx = set(self.findidxspaces(a))
        spaces = []
        idx = 0
        for i in words:
            idx += len(i)
            if idx in spaces_after_idx:
                spaces.append(True)
            else:
                spaces.append(False)

        # to avoid error. returns empty docs before the end of the processing.
        if len(words) == 0:
            return Doc(words=[], spaces=[], vocab=self.vocab)
        else:
            doc = Doc(
                words=words, spaces=spaces, vocab=self.vocab, **kwargs
            )
            assert doc.text == text
            return doc

    def __call__(self, text: str, **kwargs) -> Doc:
        return self.tokenize(text, **kwargs)
