from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class BenchmarkResult:
    """ベンチマーク結果の集約データ。"""

    thread_count: int
    throughput_tasks_per_second: float
    average_latency_ms: float
    p95_latency_ms: float
    power_proxy: float | None
    temperature_c: float | None
    score: float
