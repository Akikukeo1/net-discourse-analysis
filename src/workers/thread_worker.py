from __future__ import annotations

import logging as log
from dataclasses import dataclass


@dataclass(slots=True)
class ThreadWorker:
    """デバッグ用の単純な worker。"""

    thread_id: int

    def run(self) -> int:
        log.info("Thread %s is running.", self.thread_id)
        return self.thread_id
