quelqu'hui
==========

tokenizer for contemporary french.

| text                    | tokens                      |
| ----------------------- | --------------------------- |
| peut-on                 | `peut` `-on`                |
| prends-les              | `prends` `-les`             |
| Villar-les-bois         | `Villar-les-bois`           |
| lecteur-rice-x-s        | `lecteur-rice-x-s`          |
| correcteur·rices        | `correcteur·rices`          |
| mais.maintenant         | `mais` `.` `maintenant`     |
| relecteur.rice.s        | `relecteur.rice.s`          |
| autre(s)                | `autre(s)`                  |
| (autres)                | `(` `autres` `)`            |
| (autre(s))              | `(` `autre(s)` `)`          |
| www<area/>.on-tenk.com. | `www.on-tenk.com` `.`       |
| oui..?                  | `oui` `..?`                 |
| aujourd'hui             | `aujourd'hui`               |
| c'est                   | `c'` `est`                  |
| dedans/dehors           | `dedans` `/` `dehors`       |
| 02/10/2024              | `02/10/2024`                |
| :-)                     | `:-)`                       |
| (:happy:)               | `(` `:happy:` `)`           |

usage
-----

use as a tokenizer in a [spacy](https://spacy.io/api) pipeline:

```python
import quelquhui
import spacy

nlp = spacy.load('fr_core_news_sm')
nlp.tokenizer = quelquhui.Toquenizer(nlp.vocab)
```

if you save the pipeline and want to load it back:

```python
nlp2 = spacy.load("./model_output", config={
    "nlp": {"tokenizer": {"@tokenizers": "quelquhui_tokenizer"}}
})
```

use as a independant tokenizer (with no dependencies):

```python
import quelquhui

qh = quelquhui.light.Toquenizer()
doc = qh("la machine à (b)rouiller le temps s'est peut-être dérailler...")
```

installation
------------

```bash
pip install git+https://github.com/thjbdvlt/quelquhui
```

configuration
-------------

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
        "ELISION": ["j", "s", "jusqu"], # ...
        "INVERSION": ["on", "y", "ci"], # ...
        "SUFF_FEMININE": ["e", "rice", "ère"], # ...
        "SUFF_NONBINARY": ["x"],
        "SUFF_PLURAL": ["s", "x"],
        # there's only these 5. 
        # (default lists for the first three are longer.)
    }
)
```


how it works
------------

1. _split text on spaces._
2. it re-splits using a few functions (looped) that produced _frozen_ tokens which won't be tokenized by next functions/steps (typically: urls, or text-emoji like `:happy:`, which may be hard to tokenized in cases like `(:happy:)`; we don't want the regex looking for _emoticons_ to match `:)`: i need to defines rules to be applied in a specific order).
2. for each resulting substring:
    1. *list characters on which words must be split*. typically: punctuation marks, such as comma or period. let's say they are then considered *token boundaries*.
    2. *list characters that must be kept together, even if they have been listed in step __2.i__*.
    3. remove __2.i__ from __2.ii__, and split on remainings splitting characters.

### period

in most cases, a period is a token distinct from the word it follows: a period ending a sentence obviously isn't part of the word it follows. but in some  cases, a period actually is a part of a word (abbreviations: _p. 10_), and in some other cases, the period _and the letters following it_ must be kept in the token (inclusive language: _auteur.rice.s_). these cases are exceptions, hence they are handled in __2.ii__: i remove them from periods found in 2.i. the pattern in __2.i__ will be: `\.` (match period wherever it is, without any condition), while the pattern in __2.ii__ could be (if simplified) `(?<=[^a-z][a-z])\.|\.(?=rice|s)` (match period if preceded by a single letter or followed by _rice_ or _s_).

### hyphen

in most cases, a hyphen isn't a token boundary, because in french the hyphen is a sign that says "these two words are actually one word", such as in _Vaison-la-romaine_. but in some cases, they don't: in case of verb-subject inversion (mostly). these cases are easily described and handled with a regular expression, because subjects in these cases are always personnal pronoums: `-(?=je|tu|...`. there are also a few cases where the following word is not a pronominalized subject, but a pronominalized object, such as _prends-les_, with is also easily handled in a regular expression. hence, the pattern for hyphen in __2.i__ is not (as for period) unconditional and simple, but rather complex and conditional (match hyphen if followed by pronominalized subject or object).

dependencies
------------

- python3
- optionnel: [spacy](https://spacy.io/api)
