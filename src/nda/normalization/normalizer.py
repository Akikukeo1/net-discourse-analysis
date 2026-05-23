from __future__ import annotations

import re
import unicodedata
from re import Pattern

URL_PATTERN: Pattern[str] = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
# NOTE: 日本語を含むメンション/ハッシュタグを想定し、空白や区切り記号で終了するようにする
# CHECK: メンションの境界は email 誤爆を避けるため、負の後読みで十分か確認する
MENTION_PATTERN: Pattern[str] = re.compile(r"(?<!\w)@[^\s@#]+", re.UNICODE)
# CHECK: ハッシュタグの境界と末尾句読点の扱いが分析用途で十分か確認する
HASHTAG_PATTERN: Pattern[str] = re.compile(r"(?<!\w)#[^\s#]+", re.UNICODE)
CONTROL_PATTERN: Pattern[str] = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
WHITESPACE_PATTERN: Pattern[str] = re.compile(r"\s+", re.UNICODE)
ZERO_WIDTH = "\u200b\u200c\u200d\ufeff"
URL_TOKEN = "[URL]"
MENTION_TOKEN = "[MENTION]"
HASHTAG_TOKEN = "[HASHTAG]"
NORMALIZATION_VERSION = "nfkc-placeholder-v1"

# NOTE: We prefer to convert enclosed/parenthesized digits to their ASCII
# equivalents via NFKC normalization rather than removing them. Do not strip
# enclosed alphanumerics before normalization.
# Remove RIGHT SINGLE QUOTATION MARK (U+2019) but keep LEFT SINGLE QUOTATION MARK
# when present, to match legacy expectations in tests.
BAD_CHARS = "\u2019"

# TODO: 互換文字の扱いを用途別に切り替える設定を追加したい
# CHECK: NFKC により記号や全角英数が正規化されるため、分析用途で期待通りか確認する
# TODO: preserve_newlines=False の切り替えがあると、改行由来の感情強度分析で扱いやすい


def _remove_zero_width(text: str) -> str:
    for ch in ZERO_WIDTH:
        text = text.replace(ch, "")
    return text


def _normalize_whitespace(text: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", text).strip()


def _remove_control_chars(text: str) -> str:
    return CONTROL_PATTERN.sub("", text)


def _normalize_base(text: str) -> str:
    # Use NFKC to convert enclosed/compatibility characters (e.g. 丸付き数字) to
    # their ASCII equivalents where appropriate.
    text = unicodedata.normalize("NFKC", text)
    text = _remove_zero_width(text)
    # Remove a small set of undesirable punctuation after normalization
    for ch in BAD_CHARS:
        text = text.replace(ch, "")
    return _remove_control_chars(text)


def _strip_trailing_punctuation(token: str) -> tuple[str, str]:
    """トークン末尾の句読点を分離する。"""
    trailing_punctuation = "。、，,.!！?？:：;；)]}）】』」"  # noqa RUF001
    trimmed = token.rstrip(trailing_punctuation)
    return trimmed, token[len(trimmed) :]


def _apply_placeholder_replacements(text: str, *, replace_hashtag: bool = False) -> str:
    """URL とメンション/ハッシュタグをプレースホルダへ置換する。"""
    text = URL_PATTERN.sub(URL_TOKEN, text)

    def replace_mention(match: re.Match[str]) -> str:
        _, suffix = _strip_trailing_punctuation(match.group(0))
        return f"{MENTION_TOKEN}{suffix}"

    def replace_hashtag_token(match: re.Match[str]) -> str:
        body, suffix = _strip_trailing_punctuation(match.group(0))
        if replace_hashtag:
            return f"{HASHTAG_TOKEN}{suffix}"
        return f"{body}{suffix}"

    text = MENTION_PATTERN.sub(replace_mention, text)
    return HASHTAG_PATTERN.sub(replace_hashtag_token, text)


def normalize_safe(text: str) -> str:
    """安全な正規化を行う。

    - Unicode 正規化(NFKC)
    - ゼロ幅文字の削除
    - 制御文字の削除
    - 前後の空白除去
    - 連続空白の正規化
    """
    if not text:
        return text

    text = _normalize_base(text)
    return _normalize_whitespace(text)


def normalize_analysis(text: str, *, replace_hashtag: bool = False) -> str:
    """分析用に正規化する。

    - `normalize_safe` 相当の正規化を行う
    - URL を [URL] に置換
    - メンションを [MENTION] に置換
    - ハッシュタグを必要に応じて [HASHTAG] に置換
    """
    if not text:
        return text

    text = _normalize_base(text)
    text = _apply_placeholder_replacements(text, replace_hashtag=replace_hashtag)
    return _normalize_whitespace(text)
