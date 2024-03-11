from typing import NamedTuple
import quelquhui
import re
import texts  # pour les tests

Token = NamedTuple("Token", text=str, isspace=bool)


def tokenize(text, re_splitspace, re_freeze, re_splitpunct):
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
doc = tokenize(
    text,
    re_splitspace=re_splitspace,
    re_freeze=re_freeze,
    re_splitpunct=re_punct,
)
"".join([i.text for i in doc]) == text
print("\n".join([i.text for i in doc]))


class Tokenizer:

    chars = quelquhui.chars
    words = quelquhui.words

    regex_url = r"(?:\w+://|www\.)[\S]+[\w/]"
    re_splitspace = re.compile(r"(\s+)").split

    def __init__(
        self,
        abbrev: list[str] = [],
        inclusive: bool = True,
        url: bool = True,
    ):
        self.abbrev = abbrev
        self.inclusive = inclusive
        self.url = url

    def _update_words(self) -> None:
        """format regex words with hyphen and apostrophe"""
        p = self.chars.punct
        hyphen = p.HYPHEN
        apostrophe = p.APOSTROPHE
        self.words.inversion.INVERSION = [
            i.format(hyphen=hyphen, apostrophe=apostrophe)
            for i in self.words.inversion.INVERSION
        ]
        self.words.elision.ELISION = [
            i.format(hyphen=hyphen, apostrophe=apostrophe)
            for i in self.words.elision.ELISION
        ]


    def _genregex_hyphen(self):
        """match hyphen if preceded by letter and followed by registered word"""
        hyphen = self.chars.punct.HYPHEN
        words = self.words.inversion.INVERSION
        words = [rf"\b{i}\b" for i in words]
        words_agg = r"|".join(words)
        lookbehind = r"(?<=[^\W\d])"
        return rf"{lookbehind}[{hyphen}]({words_agg})"

    def _genregex_apostrophe(self):
        """match apostrophe if preceded by registered word."""
        words = self.words.elision.ELISION
        apostrophe = self.chars.punct.APOSTROPHE
        words_agg = r"|".join(words)
        return rf"\b({words_agg})[{apostrophe}]"

    def _genregex_digitpunct(self):
        """match digits and punctuation that needs to be frozen."""
        p = self.chars.punct
        punct = p.COMMA + p.PERIOD + p.SLASH
        return fr'\d+[{punct}]\d+'

    def _genregex_inword_parenthese(self) -> (str, str):
        """match inside-word parenthese that must be frozen"""
        p = self.chars.punct
        parentheses = (p.PARENTHESES, p.BRACKETS, p.BRACES)
        letter = self.chars.alpha.letter
        opening = []
        closing = []
        parentheses = [i.replace("\\", "") for i in parentheses]
        for left, right in parentheses:
            left = "\\" + left
            right = "\\" + right
            opening.append(
                rf"(^{left}(?![{letter}]*{right}.))|^{right}"
            )
            closing.append(
                rf"(^{right}(?![{letter}]*{left}.))|^{left}"
            )
        return r"|".join(opening), r"|".join(closing)

    def _genregex_abbrev_singleletter(self) -> str:
        """match single letter abbreviations"""
        period = self.chars.punct.PERIOD
        letter = self.chars.alpha.LETTER
        return rf"\b[{letter}]{period}(?![{letter}])"

    def _genregex_abbrev_long(self) -> str:
        """match abbreviations"""
        period = self.chars.punct.PERIOD
        letter = self.chars.alpha.LETTER
        abbrev = self.abbrev
        abbrev = r"|".join([rf"({i})" for i in abbrev])
        return rf"\b({abbrev}){period}(?![{letter}])"

    def _genregex_period_digit(self) -> str:
        """match period if between digit and letter"""
        p = self.chars.punct
        period = p.PERIOD
        apostrophe = p.APOSTROPHE
        hyphen = p.HYPHEN
        letter = self.chars.alpha.LETTER
        letters = rf"[{letter}][{letter}{apostrophe}{hyphen}]"
        regexes = [
            rf"(?<=\d){period}(?={letters})",
            rf"(?<={letters}){period}(?=\d)",
        ]
        return r"|".join(regexes)

    def _genregex_inclusive(self):
        """match period if not used as inclusive language sign.

        match cases like:
            - enseignant.e
            - enseignant.e.s
            - enseignant.es
            - enseignant.x.e.s
            - enseignant.xes
            - enseignant.exs
        but not:
            - enseignant.esdepuis ("depuis" isn't a registered suffix)
            - enseignant.sère (plural suff. cannot precedes feminine suff.)
        """
        period = self.chars.punct.PERIOD
        s = self.words.inclusive

        # join all forms for each suffix groups.
        f = r"|".join(s.FEMININE)
        x = r"|".join(s.NON_BINARY)
        s = r"|".join(s.PLURAL)

        # what must be before period. it's here only because else, other regexes wont be used.
        lookbehind = r"(?<=\D)"
        lookahead = r"(?=\D)"

        # create named captures groups, so what can come after period depends on what came before..
        firstsuffix = rf"((?P<x>{x})|(?P<f>{f})|(?P<s>{s}))"

        # for each group, defining what can follow (word+feminine+plural is ok, but not word+plural+feminine, non-binary can be anywhere.).
        if_f = rf"({x}|{s}|\b)"
        if_x = rf"({f}|{s}|\b)"
        if_s = rf"({x}|\b)"

        # aggregate the 'come after' groups
        if_group_then = rf"(?(f){if_f}|(?(x){if_x}|{if_s}))"

        return rf"{lookbehind}{period}(?!{firstsuffix}(?={if_group_then})){lookahead}"

    def _genregex_period_start(self) -> str:
        """match a period at the start of a string if followed by 2 letters"""
        period = self.chars.punct.PERIOD
        letter = self.chars.alpha.LETTER
        return rf"^({period}+)(?=([{letter}]{{2}})|[^{letter}])"

    def _genregex_end_sentence(self):
        """match any number of .?!

        the purpose of this regex is to keep as a single token cases like:
            - ..?
            - ?!
            - !!!
        """
        p = self.chars.punct
        endpunct = rf"[{p.PERIOD + p.QUESTION + p.EXCLAM}]"
        return rf"^{endpunct}+"

    def _genregex_infix_unconditionnal(self):
        """match not-word (\\W) chars that doesn't need specific processing."""
        p = self.chars.punct
        exclude = (
            p.PERIOD
            + p.PERIOD_CENTERED
            + p.PARENTHESES
            + p.HYPHENS
            + p.BRACKETS
            + p.BRACES
            + p.APOSTROPHES
            + p.COMMA
            + p.SLASH
        )
        return rf"[^\s\w{exclude}]"

    def _genregex_prefix_unconditionnal(self):
        """match not-word (\\W) chars that doesn't need specific processing."""
        p = self.chars.punct
        exclude = (
            p.BRACES
            + p.BRACKETS
            + p.PARENTHESES
            + p.APOSTROPHES
            + p.QUESTION
            + p.EXCLAM
        )
        return rf"^[^\s\w{exclude}]"

    def _genregex_reverse_suffix_unconditionnal(self):
        """match not-word (\\W) chars that doesn't need specific processing."""
        p = self.chars.punct
        exclude = (
            p.BRACES
            + p.BRACKETS
            + p.PARENTHESES
            + p.QUESTION
            + p.EXCLAM
        )
        return rf"^[^\s\w{exclude}]"

    # faire les regexes et les aggréger.
    def _aggregex_freeze(self):
        regex_freeze = []
        if self.url is True:
            regex_freeze.append(self.regex_url)
        if self.inclusive is True:
            regex_inclusive = self._genregex_inclusive()
            regex_freeze.append(regex_inclusive)
        regex_freeze = [rf"({i})" for i in regex_freeze]
        regex_freeze = r"|".join(regex_freeze)
        self.re_freeze = re.compile(regex_freeze)
        return None

    # ci-dessous: les fonctions qui split

    def _splitonspace(self, text: str):
        s = self.onspacesplitter.split(text)
        return [
            Token(text=i[0], isspace=i[1], frozen=False)
            for i in zip(s, [False, True] * len(s))
        ]

    def _splitfrozen(self, a: list[Token]):
        b = []
        r = self.re_freeze
        for i in a:
            if i.isspace:
                b.append(i)
            else:
                s = list(r(i.text))
                b.extend([
                    Token(text=i[0], isspace=False, frozen=i[1])
                    for i in zip([], [False, True] * len(s))
                ])
        return b
