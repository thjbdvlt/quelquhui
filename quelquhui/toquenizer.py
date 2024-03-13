from quelquhui.french import French


class Toquenizer:

    def __init__(self, vocab=None, method: str = 'spacy', **kwargs):

        fr = French(**kwargs)

        if method == 'spacy':
            from quelquhui.tokenizer_spacy import Tokenizer

            self.tokenizer = Tokenizer(
                vocab=vocab,
                re_freeze=fr.re_freeze,
                re_splitpunct=fr.re_splitpunct,
            )
        elif method == 'quelquhui':
            from quelquhui.tokenizer_light import Tokenizer

            self.tokenizer = Tokenizer(
                re_freeze=fr.re_freeze,
                re_splitpunct=fr.re_splitpunct,
                re_splitspace=fr.re_splitspace,
            )
        else:
            raise ValueError('available methods: spacy, quelquhui')

    def __call__(self, text, **kwargs):
        return self.tokenizer(text, **kwargs)
