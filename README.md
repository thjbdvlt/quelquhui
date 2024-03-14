quelqu'hui
==========

tokenizer for contemporary french.

| text              | tokens                    |
|-------------------|---------------------------|
| autre(s)          | `autre(s)`                |
| (autres)          | `(` `autres` `)`          |
| (autre(s))        | `(` `autre(s)` `)`        |
| mais.maintenant   | `mais` `.` `maintenant`   |
| auteur.rice.s     | `auteur.rice.s`           |
| p.10              | `p.` `10`                 |
| peut-on | `peut` `-on` |
| www<area/>.on-tenk.com. | `www.on-tenk.com` `.`    |
| oui..?            | `oui` `..?`               |
| prends-les        | `prends` `-les`           |
| Villar-les-bois    | `Villar-les-bois`          |
| aujourd'hui       | `aujourd'hui`             |
| c'est             | `c'` `est`                |

usage
-----

...

configuration
-------------

very few options can be set to modify the tokenizer behavior:

1. abbreviations can be added (default tokenizer only manages single-letter abbreviations; others are considered to be context/domain-specific).
2. it's possible to add (regex) patterns to preserve these patterns from being split.
3. characters to be recognized (?) as `HYPHEN`, `APOSTROPHE` (or anything else) can be changed.

how it works
------------

1. _split text on spaces._ spaces are defines by default as `[ \t]+`. newlines are not included because in many contexts they act not only as word separator but also as strong punctuation mark: they end sentences.
2. for each word:
    1. _list characters on which words must be split_. typically: punctuation marks, such as comma or period. let's say they are then considered _boundaries_.
    2. _list characters that must be kept together, even if they have been marked in step 2.i_.
    3. remove 2.i from 2.ii, and split on remainings splitting characters.

### example

in most cases, a period is a token boundary: a final period (ending a sentenc) obviously isn't part of the word. but in some cases, the period actually is a part of the word (abbreviations: _p.10_), and in some other cases, the period and the letters following it must be kept in the token (inclusive language: _auteur.rice.s_). these are exceptions, hence they are handled in 2.ii: i remove them from periods found in 2.i. the pattern in 2.i will be: `\.` (match period wherever it is, without any condition), while the pattern in 2.ii could be (if simplified) `(?<=[^a-z][a-z])\.|\.(?=rice|s)` (match period if preceded by a single letter or followed by _rice_ or _s_.

in most cases, a hyphen isn't a token boundary, because in french the hyphen is a sign that say "these two words are actually one word", such as in "Vaison-la-romaine". but in some cases, they don't: when it's a case of verb-subject inversion (mostly). these cases are easily described and handled with a regular expression, because subjects in these case are always personnal pronoum: `-(?=je|tu|...`. there is also a few cases where the following word is not a pronominalized subject, but a pronominalized object, such as "prends-les", with is also easily handled in a regular expression. hence, the pattern for hyphen in 2.i is not (as for period) unconditional and simple, but rather complex and conditional (match hyphen if followed by pronominalized subject or object).

why don't i just stick to spaCy's tokenizer ?
---------------------------------------------

i wrote this tokenizer because spaCy's french tokenizer currently (2024-03-12) has (to me) two issues:

1. it doesn't manage `-` correctly and uses for that a very long list (15630) of exceptions (probably automatically generated) which is not only gigantic (full of proper names such as "Minaucourt-le-Mesnil-lès-Hurlus"), but also very incomplete, because it's a list of words containing a `-` that must not be split into many tokens. i feel like it's the wrong way, because words containing `-` that must be kept as a single token are virtually infinite in french: proper names (villages, people) and inclusive forms ("auteur-rice"). it results in an inconsistent and non-comprehensive tokenizer: "quelques-uns" will be one token while "quelques-unes" will be 3 tokens ("quelques", "-", "unes") because it's not in the huge list. i feel like it's more practical to use as a rule not to split on "-" (this sign is called in french "trait d'union" -- _union trait_ --, it _unifies_), and as special cases the situations where it must split. because these cases, if they are more frequent, are also much less diverse: they all consists in verb-subject inversions where subject is a pronoun or one of a few adverb list, for a total of 21 words. a small regex and all the 15000 and many more are easily handled.
2. it doesn't manage correctly in-word parentheses, such as "(post)digital" or "quelque(s) personne(s)", producing results like `personne(s`, `)` where the opening parenthesis is a part of the token and the closing parethesis is another token.

dependencies
------------

only `python3` and `re` builtin library.
