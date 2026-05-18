from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

Scalar: TypeAlias = str | bool | int | float | tuple[int, ...]

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


def _parse_scalar(raw_value: str) -> Scalar:
    text = raw_value.strip()
    if not text:
        return ""

    if text.startswith("[") and text.endswith("]"):
        items = [item.strip() for item in text[1:-1].split(",") if item.strip()]
        return tuple(int(item) for item in items)

    lower = text.lower()
    if lower in {"true", "false"}:
        return lower == "true"

    try:
        if "." in text or "e" in lower:
            return float(text)
        return int(text)
    except ValueError:
        return text.strip("\"'")


def _apply_setting(
    settings: BenchmarkSettings, key: str, value: object
) -> BenchmarkSettings:
    if key == "executor" and isinstance(value, str):
        settings.executor = value
    elif key == "workers" and isinstance(value, int):
        settings.workers = value
    elif key == "affinity" and isinstance(value, str):
        settings.affinity = value
    elif key == "thread_counts" and isinstance(value, tuple):
        settings.thread_counts = tuple(
            int(item) for item in value if isinstance(item, (int, str))
        )
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
    """簡易 YAML 形式の設定ファイルを読み込む。"""
    settings = BenchmarkSettings()
    if not path.exists():
        return settings

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if ":" not in line:
            continue

        key, raw_value = line.split(":", 1)
        settings = _apply_setting(settings, key.strip(), _parse_scalar(raw_value))

    return settings
