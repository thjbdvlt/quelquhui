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

usage
-----

use as a tokenizer in a spacy pipeline:

```python
import quelquhui
import spacy

nlp = spacy.load('fr_core_news_sm')
nlp.tokenizer = quelquhui.Toquenizer(nlp.vocab)
# and then, as you would do with any spacy pipeline, e.g. nlp.pipe, ...
# (if you omit 'vocab', then an empty one will be initiated.)
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
    url = True, # default
    regexurl = r"(?:\w+://|www\.)[\S]+[\w/]", # default
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

why don't i just stick to spaCy's tokenizer ?
---------------------------------------------

i wrote this tokenizer because spaCy's french tokenizer currently (2024-03-12) has (to me) two issues:

1. it doesn't manage hyphen correctly and uses for that a very long list (15630) of exceptions (probably automatically generated) which is not only gigantic (full of proper names such as _Minaucourt-le-Mesnil-lès-Hurlus_), but also very incomplete, because it's a list of words containing a hyphen that must not be split into many tokens. i feel like it's the wrong way, because words containing hyphen that must be kept as a single token are virtually infinite in french: proper names (villages, people) and inclusive forms (_auteur-rice_). therefore, the list has no chance to be exhaustive. it results in an inconsistent tokenizer: _quelques-uns_ will be one token while _quelques-unes_ will be 3 tokens (_quelques_, _-_, _unes_) because it's not in the huge list. i feel like it's more practical to use as a rule not to split on hyphen (this sign is called in french _trait d'union_ -- _union trait_ --, it _unifies_), and as special cases the situations where it must split. because these cases, if they are more frequent, are also much less diverse: as said above, they all consists in verb-subject inversions where subject is a pronoun or one of a few adverb list, for a total of 21 words. a small regex and each of the 15000 and many more are easily handled.
2. it doesn't manage correctly in-word parentheses, such as _(post)digital_ or _quelque(s) personne(s)_, producing results like `personne(s`, `)` where the opening parenthesis is a part of the token and the closing parethesis is another token.

how it works
------------

1. _split text on spaces._
2. for each resulting substring:
    1. _list characters on which words must be split_. typically: punctuation marks, such as comma or period. let's say they are then considered _token boundaries_.
    2. _list characters that must be kept together, even if they have been listed in step 2.i_.
    3. remove 2.i from 2.ii, and split on remainings splitting characters.

in most cases, a period is a token boundary: a final period (ending a sentenc) obviously isn't part of the word. but in some cases, the period actually is a part of the word (abbreviations: _p.10_), and in some other cases, the period and the letters following it must be kept in the token (inclusive language: _auteur.rice.s_). these are exceptions, hence they are handled in 2.ii: i remove them from periods found in 2.i. the pattern in 2.i will be: `\.` (match period wherever it is, without any condition), while the pattern in 2.ii could be (if simplified) `(?<=[^a-z][a-z])\.|\.(?=rice|s)` (match period if preceded by a single letter or followed by _rice_ or _s_).

in most cases, a hyphen isn't a token boundary, because in french the hyphen is a sign that says "these two words are actually one word", such as in _Vaison-la-romaine_. but in some cases, they don't: in case of verb-subject inversion (mostly). these cases are easily described and handled with a regular expression, because subjects in these cases are always personnal pronoums: `-(?=je|tu|...`. there are also a few cases where the following word is not a pronominalized subject, but a pronominalized object, such as _prends-les_, with is also easily handled in a regular expression. hence, the pattern for hyphen in 2.i is not (as for period) unconditional and simple, but rather complex and conditional (match hyphen if followed by pronominalized subject or object).

dependencies
------------

only `python3` and `re` builtin library.

optional: `spacy`.
