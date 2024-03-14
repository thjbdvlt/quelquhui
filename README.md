quelqu'hui
==========

tokenizer for contemporary french.

| text                    | tokens                      |
| ----------------------- | --------------------------- |
| autre(s)                | `autre(s)`                  |
| (autres)                | `(` `autres` `)`            |
| (autre(s))              | `(` `autre(s)` `)`          |
| mais.maintenant         | `mais` `.` `maintenant`     |
| relecteur.rice.s        | `relecteur.rice.s`          |
| 10.2                    | `10.2`                      |
| p.10                    | `p.` `10`                   |
| peut-on                 | `peut` `-on`                |
| www<area/>.on-tenk.com. | `www.on-tenk.com` `.`       |
| oui..?                  | `oui` `..?`                 |
| prends-les              | `prends` `-les`             |
| Villar-les-bois         | `Villar-les-bois`           |
| aujourd'hui             | `aujourd'hui`               |
| c'est                   | `c'` `est`                  |
| dedans/dehors           | `dedans` `/` `dehors`       |
| 02/10/2024              | `02/10/2024`                |
| :-)                     | `:-)`                       |

usage
-----

use as a tokenizer in a spacy pipeline:

```python
import quelquhui
import spacy

nlp = spacy.load('fr_core_news_sm')
nlp.tokenizer = quelquhui.Toquenizer(nlp.vocab)
```

use as a independant tokenizer:

```python
import quelquhui

qh = quelquhui.Toquenizer(method='quelquhui')
doc = qh("la machine à (b)rouiller le temps s'est peut-être dérailler...")
```

very few options can be set to modify the tokenizer behavior:

```python
import quelquhui

qh = quelquhui.Toquenizer(
    abbrev = ["ref", "ed[s]"], # support regex
    inclusive = True, # default
    emoticon = True, # default
    url = True, # default
    regexurl = r"(?:\w+://|www\.)[\S]+[\w/]", # default
    regexemoticon = r":-?[\)\(]", # (default one is too long to be reproduced here.)
    chars = {
        "APOSTROPHE": "'`´’" # default
        "HYPHEN": "-–—",  # default
        # signs you'll set here will replace defaults.
        # other won't be changed.
        # complete list with default values can be found with
        # `quelquhui.default.Chars.__dict__`
    }
    words = {
        "ELISION": ["j", "s", "c"], # ...
        "INVERSION": ["je", "tu", "on"], # ...
        "SUFF_FEMININE": ["e", "rice", "ère"], # ...
        "SUFF_NONBINARY": ["x"],
        "SUFF_PLURAL": ["s", "x"],
        # there's only these 5. 
        # (default lists for the first three are longer.)
    }
)
```

the _quelquhui_ version of the tokenizer aims to be as minimal as possible. it outputs a list of tuple indicating the position of each token. unlike in the spaCy-compatible version of the tokenizer, spaces are never considered as token (but newlines are, because they often end sentences, so they are punctuation and not only word separator).

```python
import quelquhui
qh = quelquhui.Toquenizer(method='quelquhui')
qh("et les autres  autrent")

[(0, 2), (3, 6), (7, 13), (15, 22)]
```


why don't i just stick to spaCy's tokenizer ?
---------------------------------------------

i wrote this tokenizer because spaCy's french tokenizer currently (2024-03-12) has (to me) two issues:

1. it doesn't manage hyphen correctly and uses for that a very long list (15630) of exceptions (probably automatically generated) which is not only gigantic (full of proper names such as _Minaucourt-le-Mesnil-lès-Hurlus_), but also very incomplete, because it's a list of words containing a hyphen that must not be split into many tokens. i feel like it's the wrong way, because words containing hyphen that must be kept as a single token are virtually infinite in french: proper names (villages, people) and inclusive forms (_auteur-rice_). therefore, the list has no chance to be exhaustive. it results in an inconsistent tokenizer: _quelques-uns_ will be one token while _quelques-unes_ will be 3 tokens (_quelques_, _-_, _unes_) because it's not in the huge list. i feel like it's more practical to use as a rule not to split on hyphen (this sign is called in french _trait d'union_ -- _union trait_ --, it _unifies_), and as special cases the situations where it must split. because these cases, if they are more frequent, are also much less diverse: as said above, they all consists in verb-subject inversions where subject is a pronoun or one of a few adverb list, for a total of 21 words. a small regex and each of the 15000 and many more are easily handled.
2. it doesn't manage correctly in-word parentheses, such as _(post)digital_ or _quelque(s) personne(s)_, producing results like `personne(s`, `)` where the opening parenthesis is a part of the token and the closing parethesis is another token.

how it works
------------

1. _split text on spaces._
2. for each resulting substring:
    1. *list characters on which words must be split*. typically: punctuation marks, such as comma or period. let's say they are then considered *token boundaries*.
    2. *list characters that must be kept together, even if they have been listed in step __2.i__*.
    3. remove __2.i__ from __2.ii__, and split on remainings splitting characters.

in most cases, a period is a token from the word it follows: a period ending a sentence obviously isn't part of the word it follows. but in some  cases, a period actually is a part of a word (abbreviations: _p.10_), and in some other cases, the period _and the letters following it_ must be kept in the token (inclusive language: _auteur.rice.s_). these cases are exceptions, hence they are handled in __2.ii__: i remove them from periods found in 2.i. the pattern in __2.i__ will be: `\.` (match period wherever it is, without any condition), while the pattern in __2.ii__ could be (if simplified) `(?<=[^a-z][a-z])\.|\.(?=rice|s)` (match period if preceded by a single letter or followed by _rice_ or _s_).

in most cases, a hyphen isn't a token boundary, because in french the hyphen is a sign that says "these two words are actually one word", such as in _Vaison-la-romaine_. but in some cases, they don't: in case of verb-subject inversion (mostly). these cases are easily described and handled with a regular expression, because subjects in these cases are always personnal pronoums: `-(?=je|tu|...`. there are also a few cases where the following word is not a pronominalized subject, but a pronominalized object, such as _prends-les_, with is also easily handled in a regular expression. hence, the pattern for hyphen in __2.i__ is not (as for period) unconditional and simple, but rather complex and conditional (match hyphen if followed by pronominalized subject or object).

dependencies
------------

only `python3` and `re` builtin library.

optional: `spacy`.
