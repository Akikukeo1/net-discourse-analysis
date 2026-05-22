from __future__ import annotations

from enum import StrEnum


class NormalizationLabel(StrEnum):
    """正規化サンプルのラベル。"""

    URL = "safeNormalized.url"
    UNICODE = "safeNormalized.unicode"
    CONTROL = "safeNormalized.control"
