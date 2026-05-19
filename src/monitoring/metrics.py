from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class BenchmarkResult:
    """ベンチマーク結果の集約データ。"""

    requested_thread_count: int
    thread_count: int
    throughput_tasks_per_second: float
    average_latency_ms: float
    p95_latency_ms: float
    power_proxy: float | None
    temperature_c: float | None
    score: float

    def format_for_log(self) -> str:
        power_text = f"{self.power_proxy:.2f}%" if self.power_proxy is not None else "取得不可"
        temperature_text = f"{self.temperature_c:.2f}C" if self.temperature_c is not None else "取得不可"
        requested_text = (
            f"requested={self.requested_thread_count}, " if self.requested_thread_count != self.thread_count else ""
        )
        thread_text = f"thread_count={self.thread_count}"
        return (
            f"{requested_text}{thread_text}, "
            f"throughput={self.throughput_tasks_per_second:.2f} tasks/s, "
            f"average_latency={self.average_latency_ms:.2f} ms, "
            f"p95_latency={self.p95_latency_ms:.2f} ms, "
            f"power={power_text}, temperature={temperature_text}, "
            f"score={self.score:.3f}"
        )
