"""tokenizer for french"""

from quelquhui.french import French
import re


class Toquenizer:
    def __init__(self, vocab=None, method: str = "spacy", **kwargs):
        fr = French(**kwargs)

        if method == "spacy":
            from quelquhui.toquenizer_spacy import QQSpacyToquenizer

            self.toquenizer = QQSpacyToquenizer(
                vocab=vocab,
                freeze=fr.freeze,
                findborder=fr.findborder,
                split_space=re.compile(r"(?<=[^ ]) ").split,
                split_patterns=fr.split_patterns
            )
        elif method == "quelquhui":
            from quelquhui.toquenizer_light import QQHuiToquenizer

            self.toquenizer = QQHuiToquenizer(
                freeze=fr.freeze,
                findborder=fr.findborder,
                findnonspace=re.compile("[^\t ]+").finditer,
            )
        else:
            raise ValueError("available methods: spacy, quelquhui")

    def __call__(self, text, **kwargs):
        return self.toquenizer(text, **kwargs)
