from __future__ import annotations

import re
import unicodedata
from re import Pattern
from typing import Final

import neologdn  # type: ignore # noqa: PGH003

NORMALIZATION_VERSION: Final[str] = "0.1"

URL_TOKEN: Final[str] = "[URL]"
MENTION_TOKEN: Final[str] = "[MENTION]"
TRAILING_PUNCTUATION: Final[str] = "。、，,.!！?？:：;；)]}）】』」"  # noqa RUF001

URL_PATTERN: Pattern[str] = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
CONTROL_PATTERN: Pattern[str] = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
ZERO_WIDTH: tuple[str, ...] = ("\u200b", "\u200c", "\u200d", "\ufeff")
# NOTE: 日本語を含むメンション/ハッシュタグを想定し、空白や区切り記号で終了するようにする
# NOTE: メンションの境界は email 誤爆を避けるため、負の後読みで十分か確認する
MENTION_PATTERN: Pattern[str] = re.compile(r"(?<!\w)@[^\s@#()\[\]\{\}（）［］｛｝、，,]+", re.UNICODE)  # noqa RUF001
WHITESPACE_PATTERN: Pattern[str] = re.compile(r"\s+", re.UNICODE)
INVISIBLE_PATTERN: Pattern[str] = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F\u200b\u200c\u200d\ufeff]")


def _normalize_whitespace(text: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", text).strip()


def _remove_invisible_chars(text: str) -> str:
    return INVISIBLE_PATTERN.sub("", text)


def _strip_trailing_punctuation(token: str) -> tuple[str, str]:
    """トークン末尾の句読点を分離する。"""
    trimmed = token.rstrip(TRAILING_PUNCTUATION)
    return trimmed, token[len(trimmed) :]


def _replace_urls(text: str) -> str:
    return URL_PATTERN.sub(URL_TOKEN, text)


def _mention_replacer(match: re.Match[str]) -> str:
    """MENTION_PATTERN にマッチした文字列から末尾の句読点を分離し、置換トークンを生成する。"""
    _, suffix = _strip_trailing_punctuation(match.group(0))
    return f"{MENTION_TOKEN}{suffix}"


def _replace_mentions(text: str) -> str:
    """テキスト内のメンションを [MENTION] に置換する(末尾の句読点は維持)。"""
    return MENTION_PATTERN.sub(_mention_replacer, text)


def normalize(text: str) -> str:
    """正規化を行う。

    - URL を [URL] に置換
    - メンションを [MENTION] に置換
    - neologdn による日本語テキスト正規化
    - ゼロ幅文字と制御文字の削除
    - 空白の正規化
    """
    if not isinstance(text, str):
        raise TypeError(f"text は str 型である必要があります。 got: {type(text).__name__}")
    if not text.strip():
        return ""

    text = _replace_urls(text)
    text = _replace_mentions(text)
    text = neologdn.normalize(text, tilde="normalize", repeat=3)
    text = _remove_invisible_chars(text)
    text = _normalize_whitespace(text)
    return unicodedata.normalize("NFC", text)
