from quelquhui.default import Chars, Words
import re


class French:
    """regexes for french tokenization."""

    def __init__(
        self,
        abbrev: list[str] = [],
        inclusive: bool = True,
        emoticon: bool = True,
        emoji: bool = True,
        url: bool = True,
        chars: dict = [],
        words: dict = [],
        regexspace: str = r"([ \t]+)",
        regexurl: str = r"(?:\w+://|www\.)[\S]+[\w/]",
        regexemoji: str = r":\w+:",
        regexemoticon: str = None,
    ):
        # import default chars and words
        self.chars = Chars
        self.words = Words

        # update chars and words with ones submitted in argument. and update words lists that depends on hyphen and apostrophes (inversion, elision).
        for i in chars:
            setattr(self.chars, i, chars[i])
        for i in words:
            setattr(self.words, i, words[i])
        self._update_words()

        # there are 4 regexes that are only build and used by the tokenizer if an option is set to True (which is the default, for all). it's mostly because theses four kind of textual things (inclusive language, url, emoticon, emoji) are only recent things, thus there are a lot of text in which we are sure they won't by in. there is no function for url, only a default value. same for emoji (textemoji, like :happy:). if no regex is submitted for emoticon in argument, then it generates one, which is probably not perfect but match a long list of abbreviations that i found somewhere.
        self.inclusive = (
            self._genregex_inclusive() if inclusive is True else None
        )
        self.emoticon = (
            self._genregex_emoticons() if emoticon is True else None
        )
        self.emoji = regexemoji if emoji is True else None
        self.url = regexurl if url is True else None
        self.arrows = (
            self._genregex_arrows() if emoticon is True else None
        )

        # plus another one that could be optional (not for now) because i think it's not an obvious choice: it's to tokenize "12km" as two words [12, km] and 2h as [2, h]. it may lead to annoying results when tokenizing texts that may have words containing digits (but it's unusual, that's why the default behaviour is to split "3h" into two tokens, like in "trois heures").
        self.number = r"(?<!\w)\d+[\d\W]*"

        # other are not optional because they defines the syntax of common written french.
        self.elision = self._genregex_apostrophe()
        self.inversion = self._genregex_hypheninversion()
        self.usual_punct = self._genregex_usualpunct()
        self.inword_parenthese = self._genregex_inword_parenthese()
        self.end_sentence = self._genregex_end_sentence()

        # generate regex using options. for many regexes, the only parts dynamically generated are relative to chars or words (e.g.: what must be considered as a hyphen, which suffixes needs to be used as inclusive language markers, etc.).
        self.abbrev_single_letter = (
            self._genregex_abbrev_singleletter()
        )

        # multi-letters abbreviation regex is only generated if some abbreviations are set in argument.
        if abbrev is not None and len(abbrev) > 0:
            self.abbrev_multiple_letter = (
                self._genregex_abbrevmultipleletters(abbrev)
            )
        else:
            self.abbrev_multiple_letter = None

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
        words_agg = r"|".join(words)
        lookbehind = r"(?<=[^\W\d])"
        return rf"{lookbehind}[{hyphen}]\b(?:{words_agg})\b"

    def _genregex_apostrophe(self):
        """match apostrophe if preceded by registered word."""
        words = self.words.ELISION
        apostrophe = self.chars.APOSTROPHE
        words_agg = r"|".join(words)
        return rf"\b(?:{words_agg})[{apostrophe}]"

        return

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
        """match single letter abbreviations (any)."""
        c = self.chars
        return rf"^[{c.ALPHA}]{c.PERIOD}|^(?<=[^\w{c.PERIOD}])[{c.ALPHA}]{c.PERIOD}"

    def _genregex_abbrevmultipleletters(self, abbrev) -> str:
        """match longer abbreviations (from list of abbreviations)."""
        c = self.chars
        period = c.PERIOD
        abbrev = r"|".join([rf"(?:{i})" for i in abbrev])
        return rf"\b({abbrev}){period}"

    def _genregex_inclusive(self, chars: str = r'[\-\.\·]'):
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

        return rf"{chars}({firstsuffix}(?={if_group_then}))"

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

    def _genregex_usualpunct(self):
        """punctuation that usually split and punctuation that only split on boundaries."""
        c = self.chars
        e = c.PERIOD_CENTERED + c.HYPHEN + c.APOSTROPHE
        splitanywhere = rf"[^\w{e}]"
        p = rf"[{e}]"
        splitboundary = rf"^{p}|(?<=\W){p}|{p}(?=\W)|{p}$"
        return r"|".join([splitanywhere, splitboundary])

    def _genregex_emoticons(self):
        # :-)
        # D-;
        # >:^)
        eyebrowsleft = r">?"
        eyebrowsright = r"<?"
        eyes = r"[\:=;8x]'?"
        nose = r"[-o\^]?"
        mouth = r"[\(\)\]\[\}\{\}dp0o/31\*\|\><x]+"
        sideleft = eyebrowsleft + eyes + nose + mouth
        sideright = mouth + nose + eyes + eyebrowsright

        # o.O
        facemouth = r"(?:\.|_+)"
        faceeyes = [
            r"[oO0@]",
            r"[vV]",
            r"\.",
            r"-",
            r";",
            r"\^",
            r"[<>]",
        ]
        facesemoticons = [i + facemouth + i for i in faceeyes]

        # any emoticons (face / side)
        anyemoticon = r"|".join(
            [
                rf"(?:{i})"
                for i in [sideright, sideleft] + facesemoticons
            ]
        )

        # match emoticon only if they are:
        # - between two spaces
        # - between string boundaries
        # - between string boundaries and space
        start = r"(?:^|(?<=\s))"
        end = r"(?:$|(?=\s))"
        regexemoticon = rf"(?:{start}(?:{anyemoticon}){end})"

        return regexemoticon

    def _genregex_arrows(self):
        """-> => <--"""

        return r"(?:[-=]+>)|(?:<[-=]+)"

    def _aggregex_splitfuncs(self):
        patterns = [
            self.emoji,
            self.emoticon,
            self.url,
            self.number,
        ]
        patterns = [i for i in patterns if i is not None]
        self.itersplit = [re.compile(rf"({i})") for i in patterns]

    def _aggregex_freeze(self):
        """aggregate regexes that performs as exceptions finder (that prevent tokenization on some pattern)."""
        regex_freeze = [
            # always
            self.abbrev_single_letter,
            self.inword_parenthese,
            # optional
            self.inclusive,
            self.abbrev_multiple_letter,
            self.arrows,
        ]
        # keeps no-None values, and join them in a regex compiled with ignore case flag.
        regex_freeze = [i for i in regex_freeze if i is not None]
        regex_freeze = r"|".join([rf"(?:{i})" for i in regex_freeze])
        self.findexcept = re.compile(regex_freeze, re.I)

    def _aggregex_findborder(self):
        regexes = [
            self.end_sentence,
            self.inversion,
            self.elision,
            self.usual_punct,
        ]
        regexes = [i for i in regexes if i is not None]
        regexes = r"|".join([rf"(?:{i})" for i in regexes])
        self.findborder = re.compile(regexes, re.I)

    def makeregexes(self):
        self._aggregex_freeze()
        self._aggregex_splitfuncs()
        self._aggregex_findborder()
