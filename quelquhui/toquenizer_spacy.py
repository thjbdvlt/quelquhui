import quelquhui.toquenizer_light
from spacy.tokens import Doc


class Toquenizer(quelquhui.toquenizer_light.Toquenizer):
    def __init__(self, vocab, **kwargs):
        """Initiate a Toquenizer to be used on raw text.

        Args:
            vocab: a spacy vocab (required to make Docs).
            See quelquhui.French, all other args go there.

        Returns (None)
        """

        self.vocab = vocab
        super().__init__(**kwargs)

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

        Returns (list[str]): the tokenized text.
        """

        nonspaces = self.splitspace(text)
        words = self.cut(nonspaces)

        # create a list that says if words are followed by spaces.
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
