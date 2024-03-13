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

        # add property Toquen.idx (char_start)
        # and property i
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

    def __str__(self):
        return self.text

    def __repr__(self):
        return f'[{" ".join([i.text for i in self.toquens])}]'

    def __getitem__(self, i):
        return self.toquens[i]

    def toflatlist(self):
        """a list of all words and spaces."""
        a = [(i.text, i.trspace) for i in self.toquens]
        return [c for b in a for c in b]

    def tospacedeli(self):
        """return all toquen.text separated by a ' '."""
        return " ".join([i.text for i in self.toquens])

    def tojson(self, skipspace: bool = False, **kwargs):
        """output in json format.

        kwargs are given to json.dumps()
        """

        import json

        # set default value for 'ensure_ascii' to False
        if "ensure_ascii" not in kwargs:
            kwargs["ensure_ascii"] = False

        if skipspace is True:

            def toquentojson(t: Toquen):
                return {"text": t.text, "i": t.i, "idx": t.startchar}

        else:

            def toquentojson(t: Toquen):
                return t.__dict__

        return json.dumps(
            obj={
                "words": [toquentojson(t) for t in self.toquens],
                "text": self.text,
            },
            **kwargs,
        )

    def gettext(self):
        """original text, rebuilt from toquens"""
        return "".join([str(i) for i in self.toquens])
