from spacy.tokens import Doc
from spacy.vocab import Vocab
from typing import Callable, Iterable
from quelquhui.itersplit import alternatefalsetrue, infinitefalse


class QQSpacyToquenizer:
    def __init__(
        self,
        splitspace: Callable,
        splitwords: Iterable[Callable],
        findborder: Callable,
        findfreeze: Callable,
        vocab: Vocab = None,
        **kwargs,
    ):
        if vocab is None:
            vocab = Vocab(**kwargs)
        self.vocab = vocab
        self.splitspace = splitspace
        self.splitpatterns = splitwords
        self.findborder = findborder
        self.freeze = findfreeze

    def itersplit(self, text: str) -> list[str]:
        """split itérativement un texte à l'aide d'une liste de fonction."""

        # split d'abord sur les espaces, sans les conserver. au départ, aucun mot n'est gelé au départ.
        s = zip(self.splitspace(text), infinitefalse())
        # itération sur les fonctions de splitting. l'ordre est important: une fois qu'un élément extrait est extrait comme étant un token par l'une des fonctions, les fonctions suivantes ne le modifieront plus (le token est gelé).
        for fn in self.splitpatterns:
            split = fn.split
            search = fn.search
            s = (
                zip(split(i[0]), alternatefalsetrue())
                if i[1] is False and search(i[0])
                else [i]
                for i in s
            )
            # unnest la nested list et enlève les éléments vides
            s = [x for y in s for x in y if x[0] != ""]
        return s

    def tokenize(self, text: str, **kwargs) -> Doc:
        # 1. split text on spaces, then re-split with self.split functions.
        # 2. for each substring:
        #    2.1 find characters to split on.
        #    2.2 find characters found in 2.1 but not to split on.
        #    2.3 split on 2.1 - 2.2
        freeze = self.freeze
        findborder = self.findborder
        # split on spaces, then eventually split on url, then emoji, then emoticon (or using other split rules submitted in split_patterns).
        words = self.itersplit(text)
        for idx, (substring, isfrozen) in enumerate(words):
            if isfrozen is True:
                words[idx] = [substring]
                continue
            # get positions of chars that might split tokens.
            s = set().union(
                *[(i.start(), i.end()) for i in findborder(substring)]
            )
            # and remove from these numerical positions those which are marked as 'frozen' (exception).
            s.difference_update(
                *[
                    range(i.start(), i.end())
                    for i in freeze(substring)
                ]
            )
            if len(s) == 0:
                # if no split-punct remains, append substring as-is
                words[idx] = [substring]
                continue
            # else, add all parts one after the other. add 0 and len(substring.text) to ensure all text is kept.
            s.update([0, len(substring)])
            x = sorted(s)
            words[idx] = [
                substring[i : x[n + 1]] for n, i in enumerate(x[:-1])
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
