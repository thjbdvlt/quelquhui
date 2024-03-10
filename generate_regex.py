import fr


class Tokenizer:

    chars = fr.chars
    words = fr.words

    def __init__(
        self,
        abbrev: list[str],
        inclusive: bool,
        url: bool,
    ):
        self.abbrev = abbrev
        self.inclusive = inclusive
        self.url = url

    def _update_words(self) -> None:
        """format regex words with hyphen and apostrophe"""

        hyphen = self.chars.punct.HYPHEN
        apostrophe = self.chars.punct.APOSTROPHE
        self.words.inversion.INVERSION = [
            i.format(hyphen=hyphen, apostrophe=apostrophe)
            for i in self.words.inversion.INVERSION
        ]
        self.words.elision.ELISION = [
            i.format(hyphen=hyphen, apostrophe=apostrophe)
            for i in self.words.elision.ELISION
        ]

    def gen_regex_hyphen(self):
        """match hyphen if preceded by letter and followed by registered word"""
        hyphen = self.chars.punct.HYPHEN
        words = self.words.inversion.INVERSION
        words = [rf"\b{i}\b" for i in words]
        words_agg = r"|".join(words)
        lookbehind = r"(?<=[^\W\d])"
        return rf"{lookbehind}[{hyphen}]({words_agg})"

    def gen_regex_apostrophe(self):
        """match apostrophe if preceded by registered word."""
        words = self.words.elision.ELISION
        apostrophe = self.chars.punct.APOSTROPHE
        words_agg = r"|".join(words)
        return rf"\b({words_agg})[{apostrophe}]"

    def gen_regex_between_digit(self):
        """match comma/slash if not between two digits"""
        punct = self.chars.punct.COMMA + self.chars.punct.SLASH
        groupname = "comma"
        lookbehind = rf"(?<=(?P<{groupname}>\d)|\D)"
        lookahead = rf"(?=(?({groupname})\D|.))"
        return rf"{lookbehind}{punct}{lookahead}"

    def gen_regex_parenthese(self) -> (str, str):
        """match parenthese if corresponding parenthese is not inside the same string"""
        parentheses = (
            self.chars.punct.PARENTHESES,
            self.chars.punct.BRACKETS,
            self.chars.punct.BRACES,
        )
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

    def gen_regex_period_abbrev(self) -> str:
        """match period if preceded by single letter and not followed by letter"""
        period = self.chars.punct.PERIOD
        letter = self.chars.alpha.LETTER
        return rf"\b[{letter}]{period}(?![{letter}])"

    def gen_regex_period_digit(self) -> str:
        """match period if between digit and letter"""
        period = self.chars.punct.PERIOD
        letter = self.chars.alpha.LETTER
        apostrophe = self.chars.punct.APOSTROPHE
        hyphen = self.chars.punct.HYPHEN
        letters = rf"[{letter}][{letter}{apostrophe}{hyphen}]"
        regexes = [
            rf"(?<=\d){period}(?={letters})",
            rf"(?<={letters}){period}(?=\d)",
        ]
        return r"|".join(regexes)

    def gen_regex_period_suffix_inclusive(self):
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
        feminine = self.words.inclusive.FEMININE
        non_binary = self.words.inclusive.NON_BINARY
        plural = self.words.inclusive.PLURAL

        # join all forms for each suffix groups.
        f = r"|".join(feminine)
        x = r"|".join(non_binary)
        s = r"|".join(plural)

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

    def gen_regex_period_start(self) -> str:
        """match a period at the start of a string if followed by 2 letters"""
        period = self.chars.punct.PERIOD
        letter = self.chars.alpha.LETTER
        return rf"^({period}+)(?=([{letter}]{{2}})|[^{letter}])"

    def gen_regex_end_sentence(self):
        """match any number of .?!

        the purpose of this regex is to keep as a single token cases like:
            - ..?
            - ?!
            - !!!
        """
        p = self.chars.punct
        endpunct = rf"[{p.PERIOD + p.QUESTION + p.EXCLAM}]"
        return rf"^{endpunct}+"

    def gen_regex_infix_unconditionnal(self):
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

    def gen_regex_prefix_unconditionnal(self):
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

    def gen_regex_reverse_suffix_unconditionnal(self):
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
