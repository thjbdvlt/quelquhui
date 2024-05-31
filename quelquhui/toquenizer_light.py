import quelquhui.itersplit
import quelquhui.french
import re


class Toquenizer:
    def __init__(self, **kwargs):
        """Initiate a Toquenizer to be used on raw text.

        Args:
            See quelquhui.French, all other args go there.

        Returns (None)
        """

        fr = quelquhui.french.French(**kwargs)
        self.splitspace = re.compile(r"(?<=[^ ]) ").split
        self.splitpatterns = fr.itersplit
        self.findborder = fr.findborder.finditer
        self.findfreeze = fr.findexcept.finditer

    def itersplit(self, words):
        """Iteratively split a list of tokens using an Iterable of `re.Pattern`.

        Args:
            words: an iterable of tuples like (False, 'je').

        Returns (Iterable[tuple]): same structure as argument `words`.
        """

        # itération sur les fonctions de splitting. l'ordre est important: une fois qu'un élément extrait est extrait comme étant un token par l'une des fonctions, les fonctions suivantes ne le modifieront plus (le token est gelé).
        for fn in self.splitpatterns:
            search, split = fn.search, fn.split
            words = [
                zip(
                    split(i[0]),
                    quelquhui.itersplit.alternatefalsetrue(),
                )
                if i[1] is False and search(i[0])
                else [i]
                for i in words
            ]
            # unnest la nested list et enlève les éléments vides
            words = [
                x for y in words for x in y if x[0] != "" and x[0]
            ]
        return words

    def findsplit(self, substring) -> list[str]:
        """Split a substring into many.

        Args:
            substring (str): a substring of the text being tokenized.

        Returns (list[str]): a list of sub-substrings.

        Note:
            It uses two functions: one that find potential boundaries, and another one that find some exceptions that will be substract for the boundaries.
        """

        # find borders, typically: punctuation.
        s = set().union(
            *[
                (i.start(), i.end())
                for i in self.findborder(substring)
            ]
        )

        # find exceptions, and remove exceptions from borders. for example: inword parenthese(s)
        s.difference_update(
            *[
                range(i.start(), i.end())
                for i in self.findfreeze(substring)
            ]
        )

        if len(s) == 0:
            # if no borders remains, return substring without any change
            return [substring]

        # else, add all subwords
        s.update([0, len(substring)])
        x = sorted(s)
        words = []
        prev = 0
        for i in x[1:]:
            words.append(substring[prev:i])
            prev = i

        return words

    def findidxspaces(self, words):
        """Find indexes of spaces.

        Args:
            words (list[str]): list of words.

        Note:
            Used to keep trace of position of each token in the text.
        """

        spaces = []
        n = 0
        for i in words[:-1]:
            n += len(i)
            spaces.append(n)
        return spaces

    def tokenize(self, text, **kwargs):
        """Tokenize a text.

        Args:
            text (str): the text to tokenize.

        Returns (list[str]): the text tokenized.
        """

        nonspace = self.splitspace(text)
        words = self.cut(nonspace)
        return words

    def cut(self, words):
        """Tokenize a text more precisely.

        Args:
            words (list[str]): words pre-tokenized on spaces.

        Returns (list[str]): words tokenized with precision.
        """

        words = zip(words, quelquhui.itersplit.infinitefalse())
        words = self.itersplit(words)
        words = (
            [i[0]] if i[1] is True else self.findsplit(i[0])
            for i in words
        )
        words = [x for y in words for x in y]
        return words

    def __call__(self, text: str, **kwargs) -> list[str]:
        """Tokenize a text (call self.tokenize).

        Args:
            text (str): the text to be tokenized.

        Returns (list[str]): the tokenized text.
        """

        return self.tokenize(text, **kwargs)
