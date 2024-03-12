from dataclasses import dataclass


@dataclass
class Toquen:
    """a little piece of text"""

    text: str
    trailingspace: str = ""
    idx: int = None

    def __str__(self):
        return self.text + self.trailingspace

    def __repr__(self):
        return self.text

    def __len__(self):
        return len(self.text) + len(self.trailingspace)


@dataclass
class Doqument:
    """a split text, with method to output in few formats"""

    words: list[Toquen]
    text: str

    @property
    def text(self):
        return "".join([str(i) for i in self.words])

    def __getitem__(self, i):
        return self.words[i]


class Toquenizer:
    """tokenize texts."""

    def __init__(self, abbrev):
        """only one argument: context-specific abbreviations."""
        self.abbrev = abbrev

    def toquenize(self, text):
        """split a text into tokens."""
        # three functions that do the job by freezing and splitting.
        re_splitspace = self.re_splitspace
        re_freeze = self.re_freeze
        re_splitpunct = self.re_splitpunct
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
                doc[-1].trailingspace = substring
                substring = substring
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
            and doc[-1].trailingspace == ""
        ):
            doc = doc[:-1]

        # add property Toquen.idx
        n = 0
        for i in doc:
            i.idx = n
            n += len(i.text) + len(i.trailingspace)
        return Doqument(words=doc, text=text)

    def __call__(self, text):
        return self.toquenize(text)