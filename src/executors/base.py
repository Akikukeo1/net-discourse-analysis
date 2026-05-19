from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import Future


class Executor(ABC):
    """worker を受け取って実行する共通 API。"""

    @abstractmethod
    def submit(self, worker) -> Future:
        """Worker の run を実行キューに入れる。"""

    def __enter__(self) -> Executor:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    @abstractmethod
    def close(self) -> None:
        """必要なら後始末する。"""


def create_executor(kind: str, max_workers: int) -> Executor:
    """実行方式を設定で切り替える。"""
    normalized_kind = kind.strip().lower()
    if normalized_kind == "process":
        from src.executors.process_executor import ProcessExecutor

        return ProcessExecutor(max_workers=max_workers)
    if normalized_kind == "hybrid":
        from src.executors.hybrid_executor import HybridExecutor

        return HybridExecutor(max_workers=max_workers)

    from src.executors.thread_executor import ThreadExecutor

    return ThreadExecutor(max_workers=max_workers)
