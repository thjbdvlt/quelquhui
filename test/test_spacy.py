import spacy
import quelquhui

nlp = spacy.load('fr_core_news_sm')
nlp.tokenizer = quelquhui.Toquenizer(nlp.vocab)
