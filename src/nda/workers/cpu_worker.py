from __future__ import annotations

from dataclasses import dataclass


def cpu_workload(iterations: int) -> int:
    """CPU ベンチマーク用の計算負荷を作る。"""
    value = 0
    for number in range(1, iterations + 1):
        value = (value + number * number) % 1_000_000_007
    return value


@dataclass(slots=True)
class CPUWorker:
    """CPU 負荷を 1 タスクとして実行する worker。"""

    iterations: int

    def run(self) -> int:
        return cpu_workload(self.iterations)
