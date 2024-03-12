from quelquhui.toquenizer import Toquenizer
from quelquhui.default import Chars, Words
import re


class FrenchToquenizer(Toquenizer):

    def __init__(
        self,
        abbrev: list[str] = [],
        url: bool = True,
        inclusive: bool = True,
        chars: Chars = Chars,
        words: Words = Words,
        regexspace: str = r"([ \t]+)",
        regexurl: str = r"(?:\w+://|www\.)[\S]+[\w/]"

    ):
        self.abbrev = abbrev
        self.url = url
        self.inclusive = inclusive
        self.chars = chars
        self.words = words
        # self.re_splitspace = re.compile(regexspace).split
        self.re_splitspace = re.compile(regexspace).split
        self.regex_url = regexurl
        self.makeregexes()

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
        return rf"\d[{punct}]\d"

    def _genregex_inword_parenthese(self) -> (str, str):
        """match inside-word parenthese that must be frozen"""
        c = self.chars
        a = rf"[{self.chars.ALPHA}-]"
        parentheses = (
            c.PARENTHESES.replace("\\", ""),
            c.BRACKETS.replace("\\", ""),
            c.BRACES.replace("\\", ""),
        )
        regexes = []
        for left, right in parentheses:
            left = "\\" + left
            right = "\\" + right
            leftpattern = rf"((?<={a}){left}{a}+{right}){a}*"
            rightpattern = rf"((?<={left}){a}+{right}({a}))"
            pattern = r"|".join([leftpattern, rightpattern])
            regexes.append(pattern)
        return r"|".join(regexes)

    def _genregex_abbrev_singleletter(self) -> str:
        """match single letter abbreviations"""
        c = self.chars
        return rf"^[{c.ALPHA}]{c.PERIOD}|^(?<=[^\w{c.PERIOD}])[{c.ALPHA}]{c.PERIOD}"

    def _genregex_abbrevmultipleletters(self) -> str:
        """match longer abbreviations"""
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

        # return rf"{period}(?={firstsuffix}(?={if_group_then}))"
        return rf"{period}({firstsuffix}(?={if_group_then}))"

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

    def _genregex_splitpunct(self):
        """punctuation that usually split and punctuation that only split on boundaries."""
        c = self.chars
        e = c.PERIOD_CENTERED + c.HYPHEN + c.APOSTROPHE
        splitanywhere = rf"[^\w{e}]"
        p = rf"[{e}]"
        splitboundary = rf"^{p}|(?<=\W){p}|{p}(?=\W)|{p}$"
        return r"|".join([splitanywhere, splitboundary])

    def _aggregex_freeze(self):
        regex_freeze = [
            self._genregex_abbrev_singleletter(),
            self._genregex_digitpunct(),
            self._genregex_inword_parenthese(),
        ]
        if self.url is True:
            regex_freeze.append(self.regex_url)
        if self.inclusive is True:
            regex_inclusive = self._genregex_inclusive()
            regex_freeze.append(regex_inclusive)
        if self.abbrev is not None and len(self.abbrev) > 0:
            regex_freeze.append(
                self._genregex_abbrevmultipleletters()
            )
        regex_freeze = r"|".join([rf"(?:{i})" for i in regex_freeze])
        self.re_freeze = re.compile(regex_freeze).finditer

    def _aggregex_split(self):
        regexes = [
            self._genregex_end_sentence(),
            self._genregex_hypheninversion(),
            self._genregex_apostrophe(),
            self._genregex_splitpunct(),
        ]
        regexes = r"|".join([rf"(?:{i})" for i in regexes])
        self.re_splitpunct = re.compile(regexes).finditer

    def makeregexes(self):
        self._update_words()
        self._aggregex_freeze()
        self._aggregex_split()
