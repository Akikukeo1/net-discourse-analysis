from __future__ import annotations

import logging as log
import os
from dataclasses import dataclass, replace

import psutil


@dataclass(slots=True)
class CpuInfo:
    """CPU の基本情報。"""

    physical_cores: int | None
    logical_cores: int | None
    frequency_mhz: float | None
    worker_threads: int = 1


def get_cpu_info() -> CpuInfo:
    """取得処理だけを担当する。"""
    frequency = psutil.cpu_freq()
    return CpuInfo(
        physical_cores=psutil.cpu_count(logical=False),
        logical_cores=psutil.cpu_count(logical=True),
        frequency_mhz=frequency.current if frequency else None,
    )


def validate_cpu_info(info: CpuInfo) -> CpuInfo:
    """利用可能なワーカ数へ正規化する。"""
    threads = info.logical_cores or os.cpu_count() or 1
    try:
        threads = int(threads)
    except (TypeError, ValueError):
        threads = 1

    if threads <= 0:
        threads = 1

    return replace(info, worker_threads=threads)


def log_cpu_info(info: CpuInfo) -> None:
    """ログ出力だけを担当する。"""
    log.info("CPU 物理コア数: %s", info.physical_cores)
    log.info("CPU 論理コア数: %s", info.logical_cores)
    if info.frequency_mhz is not None:
        log.info("CPU 周波数: %.2f MHz", info.frequency_mhz)


def monitor_cpu() -> int:
    """互換性のための集約関数。"""
    cpu_info = validate_cpu_info(get_cpu_info())
    log_cpu_info(cpu_info)
    return cpu_info.worker_threads
