from __future__ import annotations

import logging as log
import os
import statistics
import time
from typing import Iterable

import psutil

from src.executors import create_executor
from src.hardware.cpu_info import monitor_cpu
from src.monitoring.metrics import BenchmarkResult
from src.workers.cpu_worker import CPUWorker

DEFAULT_THREAD_COUNTS = (1, 4, 8, 16, 28)
DEFAULT_TASKS_PER_WORKER = 8
DEFAULT_TARGET_TASK_SECONDS = 0.05


def _read_temperature_c() -> float | None:
    """取得できる場合だけ CPU 温度を返す。"""
    try:
        sensors = psutil.sensors_temperatures(fahrenheit=False) or {} # pyright: ignore[reportAttributeAccessIssue]
    except (AttributeError, NotImplementedError):
        return None

    values: list[float] = []
    preferred_sources = ("coretemp", "cpu_thermal", "acpitz", "k10temp", "soc_thermal")

    for source in preferred_sources:
        for sensor in sensors.get(source, []):
            if sensor.current is not None:
                values.append(float(sensor.current))

    if not values:
        for sensor_list in sensors.values():
            for sensor in sensor_list:
                if sensor.current is not None:
                    values.append(float(sensor.current))

    if not values:
        return None

    return max(values)


def _calibrate_iterations(target_task_seconds: float) -> int:
    """1 タスクの実行時間が目標値に近づくように反復回数を決める。"""
    sample_iterations = 50_000
    started_at = time.perf_counter()
    CPUWorker(sample_iterations).run()
    elapsed = time.perf_counter() - started_at

    if elapsed <= 0:
        return sample_iterations

    iterations_per_second = sample_iterations / elapsed
    calibrated = int(iterations_per_second * target_task_seconds)
    return max(calibrated, 1_000)


def _percentile(values: list[float], ratio: float) -> float:
    """単純なパーセンタイルを返す。"""
    if not values:
        return 0.0

    ordered = sorted(values)
    index = min(int(round((len(ordered) - 1) * ratio)), len(ordered) - 1)
    return ordered[index]


def _collect_benchmark_metrics(
    executor_kind: str,
    worker_count: int,
    task_iterations: int,
    tasks_per_worker: int,
) -> BenchmarkResult:
    """指定ワーカー数で負荷を実行し、性能指標を収集する。"""
    process = psutil.Process()
    logical_cpu_count = psutil.cpu_count(logical=True) or os.cpu_count() or 1

    start_cpu_times = process.cpu_times()
    start_temperature = _read_temperature_c()
    started_at = time.perf_counter()

    task_latencies: list[float] = []
    total_tasks = max(worker_count * tasks_per_worker, 1)

    with create_executor(executor_kind, max_workers=worker_count) as executor:
        futures: list[tuple[object, float]] = []
        for _ in range(total_tasks):
            task_started_at = time.perf_counter()
            future = executor.submit(CPUWorker(task_iterations))
            futures.append((future, task_started_at))

        for future, task_started_at in futures:
            future.result()
            task_finished_at = time.perf_counter()
            task_latencies.append(task_finished_at - task_started_at)

    elapsed = time.perf_counter() - started_at
    end_cpu_times = process.cpu_times()
    end_temperature = _read_temperature_c()

    cpu_time_seconds = (
        (end_cpu_times.user + end_cpu_times.system)
        - (start_cpu_times.user + start_cpu_times.system)
    )
    power_proxy = None
    if elapsed > 0:
        power_proxy = (cpu_time_seconds / elapsed) * 100.0 / max(logical_cpu_count, 1)

    temperatures = [value for value in (start_temperature, end_temperature) if value is not None]
    temperature_c = max(temperatures) if temperatures else None

    throughput_tasks_per_second = total_tasks / elapsed if elapsed > 0 else 0.0
    average_latency_ms = statistics.fmean(task_latencies) * 1000.0 if task_latencies else 0.0
    p95_latency_ms = _percentile(task_latencies, 0.95) * 1000.0 if task_latencies else 0.0

    return BenchmarkResult(
        thread_count=worker_count,
        throughput_tasks_per_second=throughput_tasks_per_second,
        average_latency_ms=average_latency_ms,
        p95_latency_ms=p95_latency_ms,
        power_proxy=power_proxy,
        temperature_c=temperature_c,
        score=0.0,
    )


def _score_results(results: list[BenchmarkResult]) -> None:
    """指標を正規化して比較スコアを付ける。"""
    if not results:
        return

    max_throughput = max(result.throughput_tasks_per_second for result in results) or 1.0
    positive_latencies = [result.average_latency_ms for result in results if result.average_latency_ms > 0]
    min_latency = min(positive_latencies) if positive_latencies else 1.0

    power_values = [result.power_proxy for result in results if result.power_proxy is not None and result.power_proxy > 0]
    temperature_values = [result.temperature_c for result in results if result.temperature_c is not None and result.temperature_c > 0]

    min_power = min(power_values) if power_values else None
    min_temperature = min(temperature_values) if temperature_values else None

    for result in results:
        factors: list[tuple[float, float]] = []

        throughput_score = max(result.throughput_tasks_per_second / max_throughput, 1e-9)
        factors.append((throughput_score, 0.5))

        if result.average_latency_ms > 0:
            latency_score = max(min_latency / result.average_latency_ms, 1e-9)
            factors.append((latency_score, 0.3))

        if min_power is not None and result.power_proxy is not None and result.power_proxy > 0:
            power_score = max(min_power / result.power_proxy, 1e-9)
            factors.append((power_score, 0.2))

        if min_temperature is not None and result.temperature_c is not None and result.temperature_c > 0:
            temperature_score = max(min_temperature / result.temperature_c, 1e-9)
            factors.append((temperature_score, 0.1))

        weight_total = sum(weight for _, weight in factors) or 1.0
        normalized_score = 1.0
        for value, weight in factors:
            normalized_score *= value ** (weight / weight_total)

        result.score = normalized_score


def benchmark(
    executor_kind: str = "thread",
    thread_counts: Iterable[int] | None = None,
    tasks_per_worker: int = DEFAULT_TASKS_PER_WORKER,
    target_task_seconds: float = DEFAULT_TARGET_TASK_SECONDS,
) -> BenchmarkResult:
    """複数の実行ワーカー数で CPU ベンチマークを実行し、最適な値を返す。"""
    log.info("CPU ベンチマークを開始します。")

    monitor_cpu()
    candidate_thread_counts = tuple(thread_counts or DEFAULT_THREAD_COUNTS)
    task_iterations = _calibrate_iterations(target_task_seconds)

    log.info("ベンチマーク候補ワーカー数: %s", candidate_thread_counts)
    log.info("1タスクの反復回数: %s", task_iterations)

    results: list[BenchmarkResult] = []
    for worker_count in candidate_thread_counts:
        if worker_count <= 0:
            continue

        log.info("ワーカー数 %s で計測を開始します。", worker_count)
        result = _collect_benchmark_metrics(executor_kind, worker_count, task_iterations, tasks_per_worker)
        results.append(result)

        power_text = f"{result.power_proxy:.2f}%" if result.power_proxy is not None else "取得不可"
        temperature_text = f"{result.temperature_c:.2f}C" if result.temperature_c is not None else "取得不可"
        log.info(
            "ワーカー数 %s: throughput=%.2f tasks/s, latency=%.2f ms, p95=%.2f ms, power=%s, temperature=%s",
            result.thread_count,
            result.throughput_tasks_per_second,
            result.average_latency_ms,
            result.p95_latency_ms,
            power_text,
            temperature_text,
        )

    if not results:
        raise ValueError("ベンチマーク対象のワーカー数がありません。")

    _score_results(results)
    best_result = max(results, key=lambda item: item.score)

    log.info(
        "最適なワーカー数は %s です。throughput=%.2f tasks/s, latency=%.2f ms, score=%.3f",
        best_result.thread_count,
        best_result.throughput_tasks_per_second,
        best_result.average_latency_ms,
        best_result.score,
    )
    if best_result.power_proxy is None:
        log.info("電力計測はこの環境では取得できませんでした。CPU使用率ベースの代理指標も使用しませんでした。")
    if best_result.temperature_c is None:
        log.info("温度計測はこの環境では取得できませんでした。")

    log.info("CPU ベンチマークが完了しました。")
    return best_result
