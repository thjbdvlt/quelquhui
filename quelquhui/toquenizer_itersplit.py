import re

import itersplit

# class QQItersplit:
#     """une autre version du tokenizer qui utilise la fonction re.split() de façon itérative."""


text = """une autre  version du tokenizer qui utilise la fonction re.split() de façon itérative. avec un support pour emoticon :-) et emojit :happy: et qui essaie d'arriver à dissocier les deux (:happy:)"""

s = re.split("(?<=[^ ]) ", text)

for i in zip(s, len(s) * [False]):
    print(i)

itersplit(self=None, text=text, splitspace=re.compile(r"(?<=[^ ]) ").split, itersplit=[re.compile(r'(:\w+:|.ei)').split, re.compile(r"(:-?\|\(:)").split]) # )


itersplit.itersplit(self=None, text=text, splitspace=re.compile(r"(?<=[^ ]) ").split, itersplit=[(re.compile(r'(:\w+:)').split, 'emoji'), (re.compile(r"(:-?\|\(:)").split)])
