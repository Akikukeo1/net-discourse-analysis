from __future__ import annotations

import logging as log


def configure_logging(log_level: str = "INFO") -> None:
    """アプリ全体のログ形式を統一する。"""
    normalized_level = getattr(log, log_level.upper(), log.INFO)
    log.basicConfig(level=normalized_level, format="%(asctime)s|%(levelname)s| %(message)s")
