try:
    import quelquhui.toquenizer_spacy

    Toquenizer = quelquhui.toquenizer_spacy.Toquenizer

except ModuleNotFoundError:
    import quelquhui.toquenizer_light

    Toquenizer = quelquhui.toquenizer_light.Toquenizer
