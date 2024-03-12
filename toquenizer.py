from dataclasses import dataclass


@dataclass
class Toquen:
    """a little piece of text."""
    text: str
    isspace: bool
    trailingspace: str = None

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text

    def __len__(self):
        return len(self.text)


class Toquenizer:
    """can be used to tokenize texts."""

    def __init__(self, abbrev):
        self.abbrev = abbrev

    def toquenize(self, text):
        """split a text into tokens."""
        re_splitspace = self.re_splitspace
        re_freeze = self.re_freeze
        re_splitpunct = self.re_splitpunct
        spacesplitted = re_splitspace(text)
        spacesplitted = [
            Toquen(text=i[0], isspace=i[1])
            for i in zip(
                spacesplitted, [False, True] * len(spacesplitted)
            )
        ]
        # remove empty token at start and ends, if there are some (which is the case when first or last string is a space).
        if len(spacesplitted) > 0 and spacesplitted[0].text == "":
            spacesplitted = spacesplitted[1:]
        if len(spacesplitted) > 0 and spacesplitted[-1].text == "":
            spacesplitted = spacesplitted[:-1]
        # initiate a document, in which tokens will be put.
        doc = []
        for substring in spacesplitted:
            if substring.isspace is True:
                doc.append(substring)
            else:
                # get positions of punctuation signs that might split tokens.
                puncts = re_splitpunct(substring.text)
                s = set().union(
                    *[(i.start(), i.end()) for i in puncts]
                )
                # and remove from these numerical positions those which are marked as 'frozen' (exception).
                frozen = re_freeze(substring.text)
                s.difference_update(
                    *[range(i.start(), i.end()) for i in frozen]
                )
                if len(s) == 0:
                    # if no split-punct remains, append substring as-is
                    doc.append(substring)
                else:
                    # else, add all parts one after the other.
                    # add 0 and len(substring.text) to ensure all text is kept.
                    s.update([0, len(substring.text)])
                    x = sorted(s)
                    for n, i in enumerate(x[:-1]):
                        doc.append(
                            Toquen(
                                text=substring.text[i : x[n + 1]],
                                isspace=False,
                            )
                        )
        return doc

    def __call__(self, text):
        return self.toquenize(text)
