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
        s = [((i.start(), i.end()), False) for i in self.splitspace(text)]
        for fn in self.splitwords:
            for idx, token in enumerate(s):
                (start, end), frozen = token
                if frozen is False:
                    substring = text[start:end]
                    x = list(fn(substring))
                    if len(x) > 0:
                        # récupère le début et fin de chaque segment matched par la fonction
                        matches = [(i.start() + start, i.end() + start) for i in x]
                        # ajoute les interstices entre les matches (non-matches), ainsi que les non-matches aux extrémités: entre le début de la substring et le début du premier match, et entre la fin du dernier match et la fin de la substring.
                        nonmatches = [
                            (matches[n][1], matches[n + 1][0])
                            for n in range(len(matches) - 1)
                        ] + [(start, matches[0][0]), (matches[-1][1], end)]
                        # ajouter les valeurs 'frozen': True pour les matches, et False pour les non-matches.
                        subtokens = [(i, True) for i in matches] + [
                            (i, False) for i in nonmatches
                        ]
                        s[idx] = subtokens
                        continue
                s[idx] = [token]
            # unnest
            s = [x for y in sorted(s) for x in y]
            # enlever les valeurs nulles
            s = [i for i in s if i[0][0] != i[0][1]]
        return s

    def tokenize(self, text: str) -> list[tuple[int, int]]:
        """split a text into tokens."""
        # three functions that do the job by freezing and splitting.
        findborder = self.findborder
        findfreeze = self.findfreeze
        d = []
        for nonspace in self.itersplit(text):
            (start, end), frozen = nonspace
            if frozen is True:
                d.append((start, end))
                continue
            substring = text[start:end]

            # get positions of punctuation signs that might split tokens.
            puncts = findborder(substring)
            s = set().union(*[(i.start(), i.end()) for i in puncts])

            # and remove from these numerical positions those which are marked as 'frozen' (exception).
            frozen = findfreeze(substring)
            s.difference_update(*[range(i.start(), i.end()) for i in frozen])
            if len(s) == 0:
                # if no split-punct remains, append substring indexes as-is
                d.append((start, end))
                continue
            # else, add all parts one after the other. add 0 and len(substring.text) to ensure all text is kept.
            s.update([0, len(substring)])
            x = sorted(s)
            d.extend([(start + sub, start + x[n + 1]) for n, sub in enumerate(x[:-1])])
        return d

    def __call__(self, text):
        return self.tokenize(text)
