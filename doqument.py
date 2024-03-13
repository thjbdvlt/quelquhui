from dataclasses import dataclass


@dataclass
class Toquen:
    """a little piece of text: word, punctuation or newline."""

    text: str
    trspace: str = ""
    i: int = None
    startchar: int = None
    endchar: int = None

    def __str__(self):
        return self.text + self.trspace

    def __repr__(self):
        return self.text

    def __len__(self):
        return len(self.text) + len(self.trspace)


class Doqument:
    """a split text, with method to output in few formats"""

    def __init__(self, words: list[Toquen], text: str = None):
        self.toquens = words

        # if original text isn't submitted: rebuild it
        self.text = text if text is not None else self.gettext()

        # add property Toquen.idx (char_start) and property i
        idx = 0
        for i, word in enumerate(self.toquens):
            word.i = i
            word.startchar = idx
            textlen = len(word.text)
            word.endchar = idx + textlen
            idx += textlen + len(word.trspace)

    @property
    def words(self):
        """a list of all token text. spaces are skipped."""
        return [i.text for i in self.toquens]

    def tojson(self, **kwargs):
        """output in json format.

        kwargs are given to json.dumps()
        """

        import json

        # set default value for 'ensure_ascii' to False
        if "ensure_ascii" not in kwargs:
            kwargs["ensure_ascii"] = False

        def toquentojson(t: Toquen):
            # doesn't print Toquen.text as it's already in the Doqument.text
            return {
                "id": t.i,
                "startchar": t.startchar,
                "endchar": t.endchar,
            }

        return json.dumps(
            obj={
                "words": [toquentojson(t) for t in self.toquens],
                "text": self.text,
            },
            **kwargs,
        )

    def tospacy(self, vocab, **kwargs):
        """words and spaces to initiate a spacy.Doc"""

        from spacy.tokens import Doc

        words = []
        spaces = []
        for i in self.toquens:
            if i.trspace == "":
                words.append(i.text)
                spaces.append(False)
            elif i.trspace == " ":
                words.append(i.text)
                spaces.append(True)
            elif i.trspace.startswith(" "):
                words.extend([i.text, i.trspace[1:]])
                spaces.extend([True, False])
            else:
                words.extend([i.text, i.trspace])
                spaces.extend([False, False])
        return Doc(vocab=vocab, words=words, spaces=spaces, **kwargs)

    def toflatlist(self):
        """a list of all words and spaces."""
        a = [(i.text, i.trspace) for i in self.toquens]
        return [c for b in a for c in b]

    def __str__(self):
        return self.text

    def __repr__(self):
        return f'[{" ".join([i.text for i in self.toquens])}]'

    def __getitem__(self, i):
        return self.toquens[i]

    def __len__(self):
        return len(self.toquens)

    def gettext(self):
        """original text, rebuilt from toquens"""
        return "".join([str(i) for i in self.toquens])
