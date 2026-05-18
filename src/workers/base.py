from __future__ import annotations

from typing import Protocol


class Worker(Protocol):
    """Executor が受け取る実行単位の共通インターフェース。"""

    def run(self) -> object:
        """仕事を実行する。"""
