from quelquhui.toquenizer_light import QQHuiToquenizer
from spacy.tokens import Doc
from spacy.vocab import Vocab
from typing import Callable, Iterable


class QQSpacyToquenizer(QQHuiToquenizer):
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

    def findidxspaces(self, words: list[str]) -> list[int]:
        spaces = []
        n = 0
        for i in words[:-1]:
            n += len(i)
            spaces.append(n)
        return spaces

    def tokenize(self, text: str, **kwargs) -> Doc:
        """tokenize a text."""

        nonspaces = self.splitspace(text)
        words = self.cut(nonspaces)

        # créer une liste qui dit si les mots sont suivis ou non par des espaces.
        spaces_after_idx = set(self.findidxspaces(nonspaces))
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
