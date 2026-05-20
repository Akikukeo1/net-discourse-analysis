from __future__ import annotations

from concurrent.futures import Future, ProcessPoolExecutor

from nda.executors.base import Executor


class ProcessExecutor(Executor):
    """ProcessPoolExecutor を隠蔽する実装。"""

    def __init__(self, max_workers: int) -> None:
        self._executor = ProcessPoolExecutor(max_workers=max_workers)

    def submit(self, worker) -> Future:
        return self._executor.submit(worker.run)

    def close(self) -> None:
        self._executor.shutdown(wait=True, cancel_futures=False)
