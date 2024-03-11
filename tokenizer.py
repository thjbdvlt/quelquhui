from dataclasses import dataclass
import re
import texts
import default


@dataclass
class Token:
    text: str
    isspace: bool

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text

    def __len__(self):
        return len(self.text)


class Tokenizer:
    def __init__(
        self, abbrev, re_splitspace, re_splitpunct, re_freeze
    ):
        self.abbrev = abbrev
        self.re_splitpunct = re_splitpunct
        self.re_splitspace = re_splitspace
        self.re_freeze = re_freeze

    def tokenize(self, text):
        re_splitspace = self.re_splitspace
        re_freeze = self.re_freeze
        re_splitpunct = self.re_splitpunct
        spacesplitted = re_splitspace(text)
        spacesplitted = [
            Token(text=i[0], isspace=i[1])
            for i in zip(
                spacesplitted, [False, True] * len(spacesplitted)
            )
        ]
        doc = []
        for substring in spacesplitted:
            if substring.isspace is True:
                doc.append(substring)
            else:
                puncts = re_splitpunct(substring.text)
                s = []
                for i in puncts:
                    s.extend([i.start(), i.end()])
                s = set(s)
                frozen = re_freeze(substring.text)
                for i in frozen:
                    s.difference_update(range(i.start(), i.end() + 1))
                if len(s) == 0:
                    doc.append(substring)
                else:
                    x = sorted(s)
                    x = [0] + x + [len(substring.text)]
                    for n, i in enumerate(x[:-1]):
                        doc.append(
                            Token(
                                text=substring.text[i : x[n + 1]],
                                isspace=False,
                            )
                        )
        return doc


regex_url = r"(?:\w+://|www\.)[\S]+[\w/]"
regex_incl = r"\.(?=e\b|ice\b|x\b|es\b|s\b)"
regex_apos = r"((?:c|n|j|t|m|s)')"
regex_hyphen = r"((?:c|n|j|t|m|s)')"
regex_freeze = r"|".join([rf"({i})" for i in [regex_url, regex_incl]])
re_freeze = re.compile(regex_freeze).finditer
re_punct = re.compile(r"([^\w'-])" + r"|" + regex_apos).finditer
re_splitspace = re.compile(r"(\s+)").split

text = texts.apostrophes
nlp = Tokenizer(
    abbrev=[],
    re_splitspace=re_splitspace,
    re_freeze=re_freeze,
    re_splitpunct=re_punct,
)
doc = nlp.tokenize(text)
"".join([i.text for i in doc]) == text
print("\n".join([i.text for i in doc]))


class RegexMaker:
    re_splitspace = re.compile(r"(\s+)").split
    regex_url = r"(?:\w+://|www\.)[\S]+[\w/]"

    def __init__(
        self,
        abbrev: list[str] = [],
        url: bool = True,
        inclusive: bool = True,
        chars: default.Chars = default.Chars,
        words: default.Words = default.Words,
    ):
        self.abbrev = abbrev
        self.url = url
        self.inclusive = inclusive
        self.chars = chars
        self.words = words

    def _update_words(self) -> None:
        """format regex words with hyphen and apostrophe"""
        c = self.chars
        hyphen = c.HYPHEN
        apostrophe = c.APOSTROPHE
        self.words.INVERSION = [
            i.format(hyphen=hyphen, apostrophe=apostrophe)
            for i in self.words.INVERSION
        ]
        self.words.ELISION = [
            i.format(hyphen=hyphen, apostrophe=apostrophe)
            for i in self.words.ELISION
        ]

    def _genregex_hypheninversion(self):
        """match hyphen if preceded by letter and followed by registered word"""
        hyphen = self.chars.HYPHEN
        words = self.words.INVERSION
        words = [rf"\b{i}\b" for i in words]
        words_agg = r"|".join(words)
        lookbehind = r"(?<=[^\W\d])"
        return rf"{lookbehind}[{hyphen}](?:{words_agg})"

    def _genregex_apostrophe(self):
        """match apostrophe if preceded by registered word."""
        words = self.words.ELISION
        apostrophe = self.chars.APOSTROPHE
        words_agg = r"|".join(words)
        return rf"\b(?:{words_agg})[{apostrophe}]"

    def _genregex_digitpunct(self):
        """match digits and punctuation that needs to be frozen."""
        c = self.chars
        punct = c.COMMA + c.PERIOD + c.SLASH
        return rf"\d+[{punct}]\d+"

    def _genregex_inword_parenthese(self) -> (str, str):
        """match inside-word parenthese that must be frozen"""
        c = self.chars
        parentheses = (c.PARENTHESES, c.BRACKETS, c.BRACES)
        pattern = r"(?<=\w)\{l}\w+\{r}|\{l}\w+\{r}(?=\w)"
        a = [
            pattern.format(l=left, r=right)
            for left, right in parentheses
        ]
        return r"|".join(a)

    def _genregex_abbrev_singleletter(self) -> str:
        """match single letter abbreviations"""
        c = self.chars
        period = c.PERIOD
        letter = c.ALPHA
        return rf"\b[{letter}]{period}"

    def _genregex_abbrevmultipleletters(self) -> str:
        """match abbreviations"""
        c = self.chars
        period = c.PERIOD
        abbrev = self.abbrev
        abbrev = r"|".join([rf"(?:{i})" for i in abbrev])
        return rf"\b({abbrev}){period}"

    def _genregex_inclusive(self):
        """match period used for inclusive language.

        match cases like:
            - enseignant.e
            - enseignant.e.s
            - enseignant.es
            - enseignant.x.e.s
            - enseignant.xères
            - enseignant.exs
            - enseignant.eusexs
        but not:
            - enseignant.esdepuis ("depuis" isn't a registered suffix)
            - enseignant.sère (plural suff. does not precede feminine suff.)
        """

        period = self.chars.PERIOD
        w = self.words

        # join all forms for each suffix groups.
        f = r"|".join(w.SUFF_FEMININE)
        x = r"|".join(w.SUFF_NONBINARY)
        w = r"|".join(w.SUFF_PLURAL)

        # create named captures groups, so what can come after period depends on what came before..
        firstsuffix = rf"((?P<x>{x})|(?P<f>{f})|(?P<s>{w}))"

        # for each group, defining what can follow (word+feminine+plural is ok, but not word+plural+feminine, non-binary can be anywhere.).
        if_f = rf"({x}|{w}|\b)"
        if_x = rf"({f}|{w}|\b)"
        if_s = rf"({x}|\b)"

        # aggregate the 'come after' groups
        if_group_then = rf"(?(f){if_f}|(?(x){if_x}|{if_s}))"

        return rf"{period}(?={firstsuffix}(?={if_group_then}))"

    def _genregex_end_sentence(self):
        """match any number of .?!

        the purpose of this regex is to keep as a single token cases like:
            - ..?
            - ?!
            - !!!
        as it's focused on everyday use of punctuation: it excludes other pattern such as:
            - :.
            - ,-!
        which are not used (as far as i know).
        """
        c = self.chars
        endpunct = rf"[{c.PERIOD + c.QUESTION + c.EXCLAM}]"
        return rf"{endpunct}+"

    def _genregex_hyphenboundary(self):
        """match punctuation that need to be taken away from token if it is not in a word."""
        c = self.chars
        p = fr"[^\s\w{c.PARENTHESES + c.BRACES + c.BRACKETS}]"
        return rf"^{p}|\W{p}|{p}\W|{p}$"

    def _genregex_splitpunct(self):
        """punctuation that usually split"""
        c = self.chars
        exclude = (
            c.PERIOD_CENTERED
            + c.HYPHENS
            + c.APOSTROPHES
        )
        return rf"[^\s\w{exclude}]"

    def _aggregex_freeze(self):
        regex_freeze = [self._genregex_digitpunct(), self._genregex_inword_parenthese(), self._genregex_abbrev_singleletter()]
        if self.url is True:
            regex_freeze.append(self.regex_url)
        if self.inclusive is True:
            regex_inclusive = self._genregex_inclusive()
            regex_freeze.append(regex_inclusive)
        if self.abbrev is not None and len(self.abbrev) > 0:
            regex_freeze.append(self._genregex_abbrevmultipleletters())
        regex_freeze = [rf"(?:{i})" for i in regex_freeze]
        regex_freeze = r"|".join(regex_freeze)
        self.re_freeze = re.compile(regex_freeze).finditer

    def _aggregex_split(self):
        regexes = [
            self._genregex_end_sentence(),
            self._genregex_hypheninversion(),
            self._genregex_apostrophe(),
            self._genregex_hyphenboundary(),
            self._genregex_splitpunct()
        ]
        regexes = r"|".join([rf"(?:{i})" for i in regexes])
        self.re_splitpunct = re.compile(regexes).finditer

    def makeregexes(self):
        self._update_words()
        self._aggregex_freeze()
        self._aggregex_split()
