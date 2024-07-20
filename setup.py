from setuptools import setup

setup(
    name="quelquhui",
    entry_points={
        "spacy_tokenizers": [
            "quelquhui_tokenizer = quelquhui.toquenizer:create_quelquhui_tokenizer"
        ]
    },
)
