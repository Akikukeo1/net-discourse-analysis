from __future__ import annotations

import logging as log
from pathlib import Path

from nda.benchmarks.cpu_bench import benchmark
from nda.configs.settings import load_benchmark_settings
from nda.monitoring.logging_config import configure_logging

CONFIG_PATH = Path(__file__).resolve().parent / "configs" / "hardware.yaml"


def main() -> None:
    """設定を読み込み、CPU ベンチマークを実行する。"""
    settings = load_benchmark_settings(CONFIG_PATH)
    configure_logging(settings.log_level)
    log.info(
        (
            "ベンチマーク設定: executor=%s, thread_counts=%s, "
            "use_thread_map=%s, tasks_per_worker=%s, target_task_seconds=%s"
        ),
        settings.executor,
        settings.thread_counts,
        settings.use_thread_map,
        settings.tasks_per_worker,
        settings.target_task_seconds,
    )
    benchmark(
        executor_kind=settings.executor,
        thread_counts=settings.thread_counts,
        use_thread_map=settings.use_thread_map,
        tasks_per_worker=settings.tasks_per_worker,
        target_task_seconds=settings.target_task_seconds,
    )


if __name__ == "__main__":
    main()
