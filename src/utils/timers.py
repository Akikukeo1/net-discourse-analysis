from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter
from typing import Iterator


@contextmanager
def elapsed_timer() -> Iterator[callable]:
    """経過時間を測る簡易コンテキスト。"""
    started_at = perf_counter()

    def elapsed() -> float:
        return perf_counter() - started_at

    yield elapsed
