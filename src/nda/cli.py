from __future__ import annotations

import logging as log
from pathlib import Path

from nda.benchmarks.cpu_bench import benchmark
from nda.configs.settings import load_benchmark_cache, load_benchmark_settings, save_benchmark_cache
from nda.monitoring.logging_config import configure_logging

CONFIG_PATH = Path(__file__).resolve().parent / "configs" / "hardware.yaml"
# NOTE: ベンチマーク結果はユーザーごとのキャッシュ配下へ保存する
CACHE_PATH = Path.home() / ".cache" / "net-discourse-analysis" / "benchmark_result.yaml"


def main() -> None:
    """メイン処理"""
    settings = load_benchmark_settings(CONFIG_PATH)
    settings = load_benchmark_cache(CACHE_PATH, settings)
    configure_logging(settings.log_level)

    # NOTE: すでにベンチマークが実行されている場合は、再実行をスキップして保存された設定を使用します。
    if settings.benchmark_run:
        log.info(
            "ベンチマークは実行済みです。スキップします。現在のワーカー数 (workers): %s",
            settings.workers,
        )
    else:
        log.info("初回起動のため、CPUベンチマークを実行して最適なワーカー数を決定します。")
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
        best_result = benchmark(
            executor_kind=settings.executor,
            thread_counts=settings.thread_counts,
            use_thread_map=settings.use_thread_map,
            tasks_per_worker=settings.tasks_per_worker,
            target_task_seconds=settings.target_task_seconds,
        )
        # NOTE: 最適なワーカー数と実行済みフラグを一時キャッシュファイルに保存します。
        settings.workers = best_result.thread_count
        settings.benchmark_run = True
        save_benchmark_cache(CACHE_PATH, settings)
        log.info(
            "最適なワーカー数 (%s) を一時キャッシュファイル (%s) に保存しました。",
            settings.workers,
            CACHE_PATH.name,
        )

    # NOTE: YouTube コメントのサンプリングと保存を行います。
    # sample_and_save(
    #     video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    #     limit=100,
    # )


if __name__ == "__main__":
    main()
