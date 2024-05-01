class QQHuiToquenizer:
    """tokenize texts."""

    def __init__(
        self,
        findborder,
        findfreeze,
        splitspace,
        splitwords,
    ):
        self.findborder = findborder
        self.findfreeze = findfreeze
        self.splitspace = splitspace
        self.splitwords = splitwords

    def itersplit(self, text: str):
        # non ça ne va pas du tout, c'est beauuuucoup trop long
        s = [
            (i.start(), i.end())
            for i in self.splitspace(text)
        ]
        return s

    def tokenize(self, text: str) -> list[tuple[int, int]]:
        """split a text into tokens."""
        # three functions that do the job by freezing and splitting.
        findborder = self.findborder
        findfreeze = self.findfreeze
        d = []
        for nonspace in self.itersplit(text):
            start, end = nonspace
            substring = text[start:end]

            # get positions of punctuation signs that might split tokens.
            puncts = findborder(substring)
            s = set().union(*[(i.start(), i.end()) for i in puncts])

            # and remove from these numerical positions those which are marked as 'frozen' (exception).
            frozen = findfreeze(substring)
            s.difference_update(
                *[range(i.start(), i.end()) for i in frozen]
            )
            if len(s) == 0:
                # if no split-punct remains, append substring indexes as-is
                d.append((start, end))
                continue
            # else, add all parts one after the other. add 0 and len(substring.text) to ensure all text is kept.
            s.update([0, len(substring)])
            x = sorted(s)
            d.extend(
                [
                    (start + sub, start + x[n + 1])
                    for n, sub in enumerate(x[:-1])
                ]
            )
        return d

    def __call__(self, text):
        return self.tokenize(text)
