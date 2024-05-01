from typing import Generator


def alternatefalsetrue() -> Generator:
    while True:
        yield False
        yield True


def infinitefalse() -> Generator:
    while True:
        yield False
