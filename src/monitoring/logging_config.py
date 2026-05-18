from __future__ import annotations

import logging as log


def configure_logging() -> None:
    """アプリ全体のログ形式を統一する。"""
    log.basicConfig(level=log.INFO, format="%(asctime)s %(levelname)s %(message)s")
