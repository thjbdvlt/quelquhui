import re


def _genregex_emoticons():
    # :-)
    # D-;
    # >:^)
    eyebrowsleft = r">?"
    eyebrowsright = r"<?"
    eyes = r"[\:=;8x]'?"
    nose = r"[-o\^]?"
    mouth = r"[\(\)\]\[\}\{\}dp0o/31\*\|\>x]+"
    sideleft = eyebrowsleft + eyes + nose + mouth
    sideright = mouth + nose + eyes + eyebrowsright
    # o.O
    facemouth = r"(?:\.|_+)"
    faceeyes = [r"[oO0@]", r"[vV]", r"\.", r"-", r";", r"\^", r"[<>]"]
    facesemoticons = [i + facemouth + i for i in faceeyes]
    # any emoticons (face / side)
    anyemoticon = r"|".join(
        [rf"(?:{i})" for i in [sideright, sideleft] + facesemoticons]
    )
    # match emoticon only if they are:
    # - between two spaces
    # - between string boundaries
    # - between string boundaries and space
    # start = r"(?:^|(?<=\s))"
    # end = r"(?:$|(?=\s))"
    start = r""
    end = r""
    regexemoticon = fr"(?:{start}(?:{anyemoticon}){end})"
    return regexemoticon


text = ":warning: alors :happy:? ou non? :-) :) (: (:happy:) (:happy: ...)"  # )))

re.split(_genregex_emoticons(), ":-).")

re.split(_genregex_emoticons(), text)

s = [[i] for i in re.split(r"\s", text)]

for n, i in enumerate(s):
    s[n] = re.split(r"(:\w+:)", i[0])


s = text.split(" ")
for pattern in [r":\w+:", r":\)"]:
    for n, i in enumerate(s):
        s[n] = re.split(rf"({pattern})", i)
    s = [x for y in s for x in y]

s = [i for i in s if i != ""]
s


def split_by_pattern(text: str, patterns: list[str]) -> list[str]:
    s = re.split(rf"({patterns[0]})", text)
    for pattern in patterns[1:]:
        for n, i in enumerate(s):
            s[n] = re.split(rf"({pattern})", i)
        s = [x for y in s for x in y]
    s = [i for i in s if i != ""]
    return s


class Toquenizer:
    def __init__(self, patterns):
        self.patterns = [re.compile(fr"({i})").split for i in patterns]

    def split_by_pattern(self, text: str) -> list[str]:
        patterns = self.patterns
        s = patterns[0](text)
        for pattern in patterns[1:]:
            for n, i in enumerate(s):
                s[n] = pattern(i)
            s = [x for y in s for x in y]
        s = [i for i in s if i != ""]
        return s

    def __call__(self, text):
        return self.split_by_pattern(text)

# li faut compilir


qh = Toquenizer([r":\w+:", r":\)"])

qh(text)
