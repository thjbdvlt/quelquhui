from quelquhui.toquenizer_light import QQHuiToquenizer
from spacy.tokens import Doc
from spacy.vocab import Vocab


class QQSpacyToquenizer(QQHuiToquenizer):
    def __init__(
        self,
        splitspace,
        splitwords,
        findborder,
        findfreeze,
        vocab=None,
        **kwargs,
    ):
        """Initiate a Tokenizer that creates Docs for spacy.

        Args:
            vocab: the vocab of the loaded model.
            splitspace: a function to split on spaces.
            splitwords: an iterable of re.Pattern used to split words and isolate some part of them (freeze).
            findborder: a function that find token boundaries.
            findfreeze: a function that find token boundaries exceptions.

        Returns (None)
        """

        if vocab is None:
            vocab = Vocab(**kwargs)
        self.vocab = vocab
        self.splitspace = splitspace
        self.splitpatterns = splitwords
        self.findborder = findborder
        self.findfreeze = findfreeze

    def findidxspaces(self, words):
        """Find spaces indexes.

        Args:
            words (list[str]): the list of words.

        Returns list[int]: indexes of spaces in text.
        """

        spaces = []
        n = 0
        for i in words[:-1]:
            n += len(i)
            spaces.append(n)
        return spaces

    def tokenize(self, text, **kwargs):
        """Tokenize a text.

        Args:
            text (str): the text to tokenize.

        Returns (list[str]): the text tokenized.
        """

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
