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
        # ha mais je testais mal, je reesaie
        s = [
            (i.start(), i.end(), False)
            for i in self.splitspace(text)
        ]
        for fn in self.splitwords:
            for n, token in enumerate(s):
                start, end, frozen = token
                substring = text[start:end]
                x = list(fn.finditer(substring))
                if len(x) == 0:
                    s[n] = [token]
                    continue
                matches = [(i.start()+start, i.end()+start, True) for i in x]
                nonmatches = [(matches[n][1], matches[n+1][0], False) for n in range(len(matches)-1)] + [(start, matches[0][0], False), (matches[-1][1], end, False)]
                s[n] = sorted(matches + nonmatches)
            s = [x for y in s for x in y]
        return s

    def tokenize(self, text: str) -> list[tuple[int, int]]:
        """split a text into tokens."""
        # three functions that do the job by freezing and splitting.
        re_splitpunct = self.findborder
        re_freeze = self.findfreeze
        d = []
        for nonspace in self.itersplit(text):
            start, end, frozen = nonspace
            if frozen is True:
                d.append((start, end))
                continue
            substring = text[start:end]

            # get positions of punctuation signs that might split tokens.
            puncts = re_splitpunct(substring)
            s = set().union(*[(i.start(), i.end()) for i in puncts])

            # and remove from these numerical positions those which are marked as 'frozen' (exception).
            frozen = re_freeze(substring)
            s.difference_update(
                *[range(i.start(), i.end()) for i in frozen]
            )
            if len(s) == 0:
                # if no split-punct remains, append substring indexes as-is
                d.append((start, end))
            else:
                # else, add all parts one after the other. add 0 and len(substring.text) to ensure all text is kept.
                s.update([0, len(substring)])
                x = sorted(s)
                d.extend([
                    (start + sub, start + x[n + 1])
                    for n, sub in enumerate(x[:-1])
                ])
        return d

    def __call__(self, text):
        return self.tokenize(text)
