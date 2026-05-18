from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.benchmarks.cpu_bench import DEFAULT_TASKS_PER_WORKER, DEFAULT_TARGET_TASK_SECONDS, DEFAULT_THREAD_COUNTS


@dataclass(slots=True)
class BenchmarkSettings:
    """ベンチマークの実行設定。"""

    executor: str = "thread"
    workers: int = 16
    affinity: str = "p_core_only"
    thread_counts: tuple[int, ...] = DEFAULT_THREAD_COUNTS
    tasks_per_worker: int = DEFAULT_TASKS_PER_WORKER
    target_task_seconds: float = DEFAULT_TARGET_TASK_SECONDS


def _parse_scalar(raw_value: str) -> object:
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
        return text.strip('"\'')


def _apply_setting(settings: BenchmarkSettings, key: str, value: object) -> BenchmarkSettings:
    if key == "executor" and isinstance(value, str):
        settings.executor = value
    elif key == "workers" and isinstance(value, int):
        settings.workers = value
    elif key == "affinity" and isinstance(value, str):
        settings.affinity = value
    elif key == "thread_counts" and isinstance(value, tuple):
        settings.thread_counts = tuple(int(item) for item in value)
    elif key == "tasks_per_worker" and isinstance(value, int):
        settings.tasks_per_worker = value
    elif key == "target_task_seconds" and isinstance(value, (int, float)):
        settings.target_task_seconds = float(value)
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
