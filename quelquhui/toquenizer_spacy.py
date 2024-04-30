from spacy.tokens import Doc
from spacy.vocab import Vocab
from typing import Callable
import re


class QQSpacyToquenizer:

    def __init__(
        self,
        re_split: list[Callable],
        re_findborder: Callable,
        re_freeze: Callable,
        vocab: Vocab = None,
        **kwargs
    ):
        if vocab is None:
            vocab = Vocab(**kwargs)
        self.vocab = vocab
        self.re_findborder = re_findborder
        self.re_freeze = re_freeze
        self.re_split = [re.compile(r"(?<=[^ ]) ").split] + splitpatterns
        self.re_decouper


    def decouper(self, text: str) -> list[str]:
        patterns = self.patterns
        s = patterns[0](text)
        for pattern in patterns[1:]:
            for n, i in enumerate(s):
                s[n] = pattern(i)
            s = [x for y in s for x in y]
        s = [i for i in s if i != ""]
        return s

    def tokenize(self, text: str, **kwargs) -> Doc:
        # 1. split text on spaces.
        # 2. for each substring:
        #    2.1 find characters to split on.
        #    2.2 find characters found in 2.1 but not to split on.
        #    2.3 split on 2.1 - 2.2
        re_splitspace = self.re_split
        re_freeze = self.re_freeze
        re_findborder = self.re_findborder
        # split on spaces
        words = re_splitspace(text)
        for idx, substring in enumerate(words):
            # get positions of punctuation signs that might split tokens.
            puncts = re_findborder(substring)
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
        # unnest both lists.
        spaces = [x for y in spaces for x in y]
        words = [x for y in words for x in y]
        # to avoid error. returns empty docs before the end of the processing.
        if len(words) == 0:
            return Doc(words=[], spaces=[], vocab=self.vocab)
        # if there is an empty token, then the string ends with a space. i remove the empty token, but i keep 'True' as the last values in 'spaces'. else, i change last value to 'False' because the last token isn't followed by a space.
        elif words[-1] == "":
            words = words[:-1]
            spaces = spaces[:-1]
        else:
            spaces[-1] = False
        return Doc(
            words=words, spaces=spaces, vocab=self.vocab, **kwargs
        )

    def __call__(self, text: str, **kwargs) -> Doc:
        return self.tokenize(text, **kwargs)
