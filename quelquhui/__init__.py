try:
    import quelquhui.toquenizer

    Toquenizer = quelquhui.toquenizer.Toquenizer

except ModuleNotFoundError:
    import quelquhui.light

    Toquenizer = quelquhui.light.Toquenizer
