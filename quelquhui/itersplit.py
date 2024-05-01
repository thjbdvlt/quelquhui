from typing import Callable, Iterable, Generator


def alternatelabel(label) -> Generator:
    """alternativement un label et None"""
    while True:
        yield None
        yield label


def alternatefalsetrue() -> Generator:
    """alternativement False et True"""
    while True:
        yield False
        yield True
