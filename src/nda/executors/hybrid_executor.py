from __future__ import annotations

from concurrent.futures import Future

from nda.executors.base import Executor
from nda.executors.thread_executor import ThreadExecutor


class HybridExecutor(Executor):
    """将来のハイブリッド実装の差し替え口。"""

    def __init__(self, max_workers: int) -> None:
        self._delegate = ThreadExecutor(max_workers=max_workers)

    def submit(self, worker) -> Future:
        return self._delegate.submit(worker)

    def __enter__(self) -> HybridExecutor:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        self._delegate.close()
