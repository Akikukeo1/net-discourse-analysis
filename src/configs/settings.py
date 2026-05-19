from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from collections.abc import Mapping

import yaml

from src.benchmarks.cpu_bench import (
    DEFAULT_TASKS_PER_WORKER,
    DEFAULT_TARGET_TASK_SECONDS,
    DEFAULT_THREAD_COUNTS,
)


@dataclass(slots=True)
class BenchmarkSettings:
    """ベンチマークの実行設定。"""

    executor: str = "thread"
    workers: int = 16
    affinity: str = "p_core_only"
    thread_counts: tuple[int, ...] = DEFAULT_THREAD_COUNTS
    tasks_per_worker: int = DEFAULT_TASKS_PER_WORKER
    target_task_seconds: float = DEFAULT_TARGET_TASK_SECONDS
    use_thread_map: bool = False
    log_level: str = "INFO"


def _apply_setting(
    settings: BenchmarkSettings, key: str, value: object
) -> BenchmarkSettings:
    if key == "executor" and isinstance(value, str):
        settings.executor = value
    elif key == "workers" and isinstance(value, int):
        settings.workers = value
    elif key == "affinity" and isinstance(value, str):
        settings.affinity = value
    elif key == "thread_counts" and isinstance(value, (list, tuple)):
        thread_counts: list[int] = []
        for item in value:
            if isinstance(item, int):
                thread_counts.append(item)
            elif isinstance(item, str):
                thread_counts.append(int(item))
            else:
                raise ValueError("thread_counts は整数の配列である必要があります。")

        settings.thread_counts = tuple(thread_counts)
    elif key == "tasks_per_worker" and isinstance(value, int):
        settings.tasks_per_worker = value
    elif key == "target_task_seconds" and isinstance(value, (int, float)):
        settings.target_task_seconds = float(value)
    elif key == "use_thread_map" and isinstance(value, bool):
        settings.use_thread_map = value
    elif key == "log_level" and isinstance(value, str):
        settings.log_level = value.strip().upper()
    return settings


def load_benchmark_settings(path: Path) -> BenchmarkSettings:
    """YAML 形式の設定ファイルを読み込む。"""
    settings = BenchmarkSettings()
    if not path.exists():
        return settings

    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if loaded is None:
        return settings

    if not isinstance(loaded, Mapping):
        raise ValueError("設定ファイルは YAML のマッピングである必要があります。")

    for key, value in loaded.items():
        if isinstance(key, str):
            settings = _apply_setting(settings, key.strip(), value)

    return settings
