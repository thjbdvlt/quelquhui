class QQHuiToquenizer:
    """tokenize texts."""

    def __init__(
        self,
        re_splitpunct,
        re_freeze,
        re_nonspace,
    ):
        """only one argument: context-specific abbreviations."""
        self.re_nonspace = re_nonspace
        self.re_splitpunct = re_splitpunct
        self.re_freeze = re_freeze

    def tokenize(self, text: str) -> list[tuple[int, int]]:
        """split a text into tokens."""
        # three functions that do the job by freezing and splitting.
        re_nonspace = self.re_nonspace
        re_splitpunct = self.re_splitpunct
        re_freeze = self.re_freeze
        d = []
        for nonspace in re_nonspace(text):
            start = nonspace.start()
            end = nonspace.end()
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
