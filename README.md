quelqu'hui
==========

tokenizer for contemporary french.

| text              | tokens                    |
|-------------------|---------------------------|
| autre(s)          | `autre(s)`                |
| (autres)          | `(`, `autres`, `)`        |
| (autre(s))        | `(`, `autre(s)`, `)`      |
| mais.maintenant   | `mais`, `.`, `maintenant` |
| auteur.rice.s     | `auteur.rice.s`           |
| p.10              | `p.`, `10`                |
| www.birdsong.com. | `www.birdsong.com`, `.`   |
| oui..?            | `oui`, `..?`              |
| peut-on           | `peut`, `-on`             |
| Merlin-sur-mer    | `Merlin-sur-mer`          |
| prends-les        | `prends`, `-les`          |
| Villar-le-bois    | `Villar-le-bois`          |
| aujourd'hui       | `aujourd'hui`             |
| c'est             | `c'`, `est`               |

usage
-----

...

configuration
-------------

a very few options can be set to modify the tokenizer behavior:

1. abbreviations can be added (default tokenizer only manages single-letter abbreviations; others are considered to be context/domain-specific).
2. it's possible to add (regex) patterns to preserve these patterns from being split.
3. characters to be recognized as `HYPHEN`, `APOSTROPHE` (or anything else) can be changed.

how it works
------------

1. _splits text on spaces._ (using `re.split`) spaces are defines by default as `[ \t]+`. newlines are not included because in many contexts they act not only as word separator but also as strong punctuation mark: they end sentences.
2. for each word:
    1. _localises characters on which it must split the word_ (.`re.finditer`) typically: punctuation marks, such as `,`, `.` let's say they are then considered _boundaries_.
    2. _localises characters that must be kept together, even if they have been marked in step 2_ (using `re.finditer`).
    3. splits on remainings splitting characters (2 - 3).

__example__: as most `.` must result in splitting a substring into many (rule rather than exception), in step 2.1 all `.` are marked as _boundaries_. exceptions such as inclusive language (auteur.rice) or abbreviations (p. 10) are removed from the _boundaries_ list in step 2.2. for hyphens (`-`), it's the opposite, because in most cases, hyphen must not result in splitting a substring into many. so while in 2.1 the regex for period is `\.` (match dots wherever they are), the regex for hyphen is conditionnal (thus more complex): a hyphen is marked as a _boundary_ if and only if it's followed by some pattern.

why i just don't stick to spaCy's tokenizer ?
---------------------------------------------

i wrote this tokenizer because spaCy's french tokenizer currently (2024-03-12) has (to me) two issues:

1. it doesn't manage `-` correctly and uses for that a very long list (15630) of exceptions (probably automatically generated) which is not only gigantic (full of proper names such as "Minaucourt-le-Mesnil-lès-Hurlus"), but also very incomplete, because it's a list of words containing a `-` that must not be split into many tokens. i feel like it's the wrong way, because words containing `-` that must be kept as a single token are virtually infinite in french: proper names (villages, people) and inclusive forms ("auteur-rice"). it results in an inconsistent and non-comprehensive tokenizer: "quelques-uns" will be one token while "quelques-unes" will be 3 tokens ("quelques", "-", "unes") because it's not in the huge list. i feel like it's more practical to use as a rule not to split on "-" (this sign is called in french "trait d'union" -- _union trait_ --, it _unifies_), and as special cases the situations where it must split. because these cases, if they are more frequent, are also much less diverse: they all consists in verb-subject inversions where subject is a pronoun or one of a few adverb list, for a total of 21 words. a small regex and all the 15000 and many more are easily handled.
2. it doesn't manage correctly in-word parentheses, such as "(post)digital" or "quelque(s) personne(s)", producing results like `personne(s`, `)` where the opening parenthese is a part of the token and the closing parethese is another token.

dependancies
------------

only `python3` and `re` builtin library.
