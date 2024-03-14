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

        opts = {"ensure_ascii": False, "indent": 2}
        opts.update(kwargs)

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
            **opts,
        )

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


class QQHuiToquenizer:
    """tokenize texts."""

    def __init__(
        self, re_splitpunct, re_freeze, re_splitspace
    ):
        """only one argument: context-specific abbreviations."""
        self.re_splitspace = re_splitspace
        self.re_splitpunct = re_splitpunct
        self.re_freeze = re_freeze

    def tokenize(self, text):
        """split a text into tokens."""
        # three functions that do the job by freezing and splitting.
        re_splitspace = self.re_splitspace
        re_splitpunct = self.re_splitpunct
        re_freeze = self.re_freeze
        # split on space
        spacesplitted = re_splitspace(text)
        # mark spaces as space, so they will be processed specifically.
        spacesplitted = [
            (i[0], i[1])
            for i in zip(
                spacesplitted, [False, True] * len(spacesplitted)
            )
        ]
        # initiate a document, in which tokens will be put.
        doc = []
        for substring, isspace in spacesplitted:
            if isspace is True:
                doc[-1].trspace = substring
            else:
                # get positions of punctuation signs that might split tokens.
                puncts = re_splitpunct(substring)
                s = set().union(
                    *[(i.start(), i.end()) for i in puncts]
                )
                # and remove from these numerical positions those which are marked as 'frozen' (exception).
                frozen = re_freeze(substring)
                s.difference_update(
                    *[range(i.start(), i.end()) for i in frozen]
                )
                if len(s) == 0:
                    # if no split-punct remains, append substring as-is
                    doc.append(Toquen(text=substring))
                else:
                    # else, add all parts one after the other. add 0 and len(substring.text) to ensure all text is kept.
                    s.update([0, len(substring)])
                    x = sorted(s)
                    for n, i in enumerate(x[:-1]):
                        doc.append(
                            Toquen(text=substring[i : x[n + 1]])
                        )
        # remove empty token at end, if there are some (which is the case when first or last string is a space). i don't remove them at start, because if there is one, it's because the first character is a space, so it would be attach as the trailing space of the empty initial character.
        if (
            len(doc) > 0
            and doc[-1].text == ""
            and doc[-1].trspace == ""
        ):
            doc = doc[:-1]
        return Doqument(words=doc, text=text)

    def __call__(self, text):
        return self.tokenize(text)
