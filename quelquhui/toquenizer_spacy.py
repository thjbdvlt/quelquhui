from spacy.tokens import Doc
from spacy.vocab import Vocab
from typing import Callable, Iterable
from quelquhui.itersplit import alternatefalsetrue


class QQSpacyToquenizer:
    def __init__(
        self,
        split_space: Callable,
        split_patterns: Iterable[Callable],
        findborder: Callable,
        freeze: Callable,
        vocab: Vocab = None,
        **kwargs,
    ):
        if vocab is None:
            vocab = Vocab(**kwargs)
        self.vocab = vocab
        self.splitspace = split_space
        self.splitpatterns = split_patterns
        self.findborder = findborder
        self.freeze = freeze

    def itersplit(self, text: str) -> list[str]:
        """split itérativement un texte à l'aide d'une liste de fonction."""

        # split d'abord sur les espaces, sans les conserver.
        s = self.splitspace(text)
        # au départ, aucun mot n'est gelé au départ.
        s = list(zip(s, len(s) * [False]))
        # itération sur les fonctions de splitting. l'ordre est important: une fois qu'un élément extrait est extrait comme étant un token par l'une des fonctions, les fonctions suivantes ne le modifieront plus (le token est gelé).
        for fn in self.splitpatterns:
            # itération sur les segments de textes (les tokens en devenir).
            for n, i in enumerate(s):
                # ne modifié les tokens qui ne sont pas marqué comme gelés
                if i[1] is False:
                    # split à l'aide de la fonction
                    x = fn(i[0])
                    # si la longueur de la nouvelle liste est supérieur à 1, alors la fonction a modifié quelque chose: les segments extraits sont isolés et gelés, et l'ancien segment est remplacé dans la liste des segments.
                    if len(x) > 1:
                        s[n] = list(zip(x, alternatefalsetrue()))
                        continue
                # sinon (si le token est gelé ou si la liste a une longueur de 1) alors le segment est simplement remplacé par une liste ne contenant que lui-même.
                s[n] = [i]
            # unnest la nested list.
            s = [x for y in s for x in y]
        print(s)
        return [i for i in s if i[0] != ""]

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
            # get positions of punctuation signs that might split tokens.
            puncts = findborder(substring)
            s = set().union(*[(i.start(), i.end()) for i in puncts])
            # and remove from these numerical positions those which are marked as 'frozen' (exception).
            frozenchars = freeze(substring)
            s.difference_update(*[range(i.start(), i.end()) for i in frozenchars])
            if len(s) == 0:
                # if no split-punct remains, append substring as-is
                words[idx] = [substring]
                continue
            # else, add all parts one after the other. add 0 and len(substring.text) to ensure all text is kept.
            s.update([0, len(substring)])
            x = sorted(s)
            words[idx] = [substring[i : x[n + 1]] for n, i in enumerate(x[:-1])]
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
        return Doc(words=words, spaces=spaces, vocab=self.vocab, **kwargs)

    def __call__(self, text: str, **kwargs) -> Doc:
        return self.tokenize(text, **kwargs)
