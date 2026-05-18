from __future__ import annotations

from pathlib import Path

from src.benchmarks.cpu_bench import benchmark
from src.configs.settings import load_benchmark_settings
from src.monitoring.logging_config import configure_logging

CONFIG_PATH = Path(__file__).resolve().parent / "configs" / "hardware.yaml"


def main() -> None:
    """設定を読み込み、CPU ベンチマークを実行する。"""
    configure_logging()
    settings = load_benchmark_settings(CONFIG_PATH)
    benchmark(
        executor_kind=settings.executor,
        thread_counts=settings.thread_counts,
        tasks_per_worker=settings.tasks_per_worker,
        target_task_seconds=settings.target_task_seconds,
    )


if __name__ == "__main__":
    main()
