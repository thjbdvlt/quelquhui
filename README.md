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
| www.on<area/>-tenk.com. | `www.on-tenk.com` `.`    |
| oui..?            | `oui` `..?`               |
| prends-les        | `prends` `-les`           |
| Villar-le-bois    | `Villar-le-bois`          |
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
    1. _localise characters on which words must be split_. typically: punctuation marks, such as comma or period. let's say they are then considered _boundaries_.
    2. _localise characters that must be kept together, even if they have been marked in step 2.i_.
    3. split on remainings splitting characters (2.i - 2.ii).

__example__: as most periods must (?) result in splitting a substring into many (rule rather than exception), in step 2.1 all `.` are marked as _boundaries_. exceptions such as inclusive language ("auteur.rice") or abbreviations ("p. 10") are removed from the _boundaries_ list in step 2.2. (?)(PEUTETRE AJOUTE UN POINT PUISQUE PAS DE MAJUSCULE) 

for hyphens (`-`) it's the opposite, because in most cases, hyphen must (?) not result in splitting a substring into many words. so while in 2.1 the regex for period is `\.` (match dots wherever they are), the regex for hyphen is conditionnal (thus more complex): a hyphen is marked as a _boundary_ if and only if it's a case of verb-subject inversion (identified by the presence of a personnal pronoun, or a few other things).

why don't i just stick to spaCy's tokenizer ?
---------------------------------------------

i wrote this tokenizer because spaCy's french tokenizer currently (2024-03-12) has (to me) two issues:

1. it doesn't manage `-` correctly and uses for that a very long list (15630) of exceptions (probably automatically generated) which is not only gigantic (full of proper names such as "Minaucourt-le-Mesnil-lès-Hurlus"), but also very incomplete, because it's a list of words containing a `-` that must not be split into many tokens. i feel like it's the wrong way, because words containing `-` that must be kept as a single token are virtually infinite in french: proper names (villages, people) and inclusive forms ("auteur-rice"). it results in an inconsistent and non-comprehensive tokenizer: "quelques-uns" will be one token while "quelques-unes" will be 3 tokens ("quelques", "-", "unes") because it's not in the huge list. i feel like it's more practical to use as a rule not to split on "-" (this sign is called in french "trait d'union" -- _union trait_ --, it _unifies_), and as special cases the situations where it must split. because these cases, if they are more frequent, are also much less diverse: they all consists in verb-subject inversions where subject is a pronoun or one of a few adverb list, for a total of 21 words. a small regex and all the 15000 and many more are easily handled.
2. it doesn't manage correctly in-word parentheses, such as "(post)digital" or "quelque(s) personne(s)", producing results like `personne(s`, `)` where the opening parenthesis is a part of the token and the closing parethesis is another token.

dependencies
------------

only `python3` and `re` builtin library.
