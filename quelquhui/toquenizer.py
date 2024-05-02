from quelquhui.french import French
import re


class Toquenizer:
    def __init__(self, vocab=None, method: str = "spacy", **kwargs):
        fr = French(**kwargs)

        if method == "spacy":
            from quelquhui.toquenizer_spacy import QQSpacyToquenizer

            self.toquenizer = QQSpacyToquenizer(
                vocab=vocab,
                findfreeze=fr.freeze.finditer,
                findborder=fr.findborder.finditer,
                splitspace=re.compile(r"(?<=[^ ]) ").split,
                splitwords=fr.splitpatterns
            )
        elif method == "quelquhui":
            from quelquhui.toquenizer_light import QQHuiToquenizer

            self.toquenizer = QQHuiToquenizer(
                findfreeze=fr.freeze.finditer,
                findborder=fr.findborder.finditer,
                splitspace=re.compile(r"(?<=[^ ]) ").split,
                # splitspace=re.compile("[^\t ]+").finditer,
                splitwords=fr.splitpatterns,
            )
        else:
            raise ValueError("available methods: spacy, quelquhui")

    def __call__(self, text, **kwargs):
        return self.toquenizer(text, **kwargs)



