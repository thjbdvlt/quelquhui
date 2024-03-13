from quelquhui.doqument import Toquen, Doqument


class Toquenizer:
    """tokenize texts."""

    def __init__(self, abbrev, vocab=None):
        """only one argument: context-specific abbreviations."""
        self.abbrev = abbrev
        self.vocab = vocab

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
                        # essayer extend..? et liste comprehension
        # remove empty token at end, if there are some (which is the case when first or last string is a space). i don't remove them at start, because if there is one, it's because the first character is a space, so it would be attach as the trailing space of the empty initial character.
        if (
            len(doc) > 0
            and doc[-1].text == ""
            and doc[-1].trspace == ""
        ):
            doc = doc[:-1]
        return Doqument(words=doc, text=text)

    def __call__(self, text):
        return self.toquenize(text)

    def spacytokenize(self, text):
        re_freeze = self.re_freeze
        re_splitpunct = self.re_splitpunct
        re_splitspace = self.re_splitspacystyle
        words = re_splitspace(text)
        spaces = []
        for idx, substring in enumerate(words):
            # get positions of punctuation signs that might split tokens.
            puncts = re_splitpunct(substring)
            s = set().union(*[(i.start(), i.end()) for i in puncts])
            # and remove from these numerical positions those which are marked as 'frozen' (exception).
            frozen = re_freeze(substring)
            s.difference_update(
                *[range(i.start(), i.end()) for i in frozen]
            )
            if len(s) == 0:
                # if no split-punct remains, append substring as-is
                words[idx] = [substring]
            else:
                # else, add all parts one after the other. add 0 and len(substring.text) to ensure all text is kept.
                s.update([0, len(substring)])
                x = sorted(s)
                words[idx] = [
                    substring[i : x[n + 1]]
                    for n, i in enumerate(x[:-1])
                ]
        spaces = [[False] * (len(i) - 1) + [True] for i in words]
        # unnest
        spaces = [x for y in spaces for x in y]
        words = [x for y in words for x in y]
        # if there is an empty token, then the string ends with a space. i remove the empty token, but i keep 'True' as the last values in 'spaces'. else, i change last value to 'False' because the last token isn't followed by a space.
        if words[-1] == "":
            words = words[:-1]
            spaces = spaces[:-1]
        else:
            spaces[-1] = False
        return words, spaces
