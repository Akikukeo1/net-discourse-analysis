from __future__ import annotations

import re
import unicodedata
from re import Pattern
from typing import Final

import neologdn  # HACK: 誤検知を黙らせる # type: ignore # noqa: PGH003

NORMALIZATION_VERSION: Final[str] = "0.1"

URL_TOKEN: Final[str] = "[URL]"
MENTION_TOKEN: Final[str] = "[MENTION]"

TRAILING_PUNCTUATION: Final[str] = (
    "。、，,"  # 読点・カンマ  # noqa RUF001
    "!！?？"  # 感嘆符・疑問符  # noqa RUF001
    ":：;；"  # コロン・セミコロン  # noqa RUF001
    ")}]）】』」"  # 閉じ括弧系  # noqa RUF001
)

URL_PATTERN: Pattern[str] = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)

# FIXME: youtube.pyのリファクタまで、一時的にこの2つを追加しておく。
# FIXME: 絶対に消す!!!!!
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


def _extract_trailing_punctuation(token: str) -> str:
    """トークン末尾の句読点部分『のみ』を抽出して返す。"""
    trimmed = token.rstrip(TRAILING_PUNCTUATION)
    return token[len(trimmed) :]


def _mention_replacer(match: re.Match[str]) -> str:
    """MENTION_PATTERN にマッチした文字列から末尾の句読点のみを抽出し、置換トークンと結合する。"""
    suffix = _extract_trailing_punctuation(match.group(0))
    return f"{MENTION_TOKEN}{suffix}"


def _replace_urls(text: str) -> str:
    return URL_PATTERN.sub(URL_TOKEN, text)


def _replace_mentions(text: str) -> str:
    """テキスト内のメンションを [MENTION] に置換する(末尾の句読点は維持)。"""
    return MENTION_PATTERN.sub(_mention_replacer, text)


def normalize(text: str) -> str:
    """正規化を行う。"""
    if not isinstance(text, str):
        raise TypeError(f"text は str 型である必要があります。 got: {type(text).__name__}")

    if not text or text.isspace():
        return ""

    text = _replace_urls(text)
    text = _replace_mentions(text)

    text = unicodedata.normalize("NFKC", text)

    text = neologdn.normalize(text, tilde="normalize", repeat=3)

    text = _remove_invisible_chars(text)
    return _normalize_whitespace(text)
