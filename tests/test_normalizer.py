from __future__ import annotations

from urllib.parse import urlparse

from nda.normalization.normalizer import NORMALIZATION_VERSION, normalize_analysis, normalize_safe

# NOTE: 全角混在入力は可読性のため実文字で記述し、RUF001 を明示的に許可する
# ruff: noqa: RUF001


def test_normalize_safe_url_and_control() -> None:
    """URL を保持し、制御文字が除去されることを確認する。"""
    s = "Check this out https://example.com\nNice"
    out = normalize_safe(s)
    urls = [urlparse(token) for token in out.split() if "://" in token]
    assert any(u.scheme == "https" and u.hostname == "example.com" for u in urls)
    assert "\n" not in out


def test_normalize_safe_unicode() -> None:
    """ゼロ幅文字が除去されることを確認する。"""
    s = "ちくわ\u200b"
    out = normalize_safe(s)
    assert "ちくわ" in out
    assert "\u200b" not in out


def test_normalize_safe_nfkc() -> None:
    """NFKC により互換文字が正規化されることを確認する。"""
    s = "ＡＢＣ ① ｶﾀｶﾅ"
    out = normalize_safe(s)
    assert out == "ABC 1 カタカナ"


def test_normalize_analysis_replacements() -> None:
    """URL とメンションが置換されることを確認する。"""
    s = "@user @ユーザー @名前 See https://example.com now test@example.com"
    out = normalize_analysis(s)
    assert "[MENTION]" in out
    assert "[URL]" in out
    assert "test@example.com" in out


def test_normalize_analysis_hashtag_punctuation() -> None:
    """全角句読点を含むハッシュタグが NFKC 後も期待通り置換されることを確認する。"""
    s = "#AI研究！ これはどうだろう"
    out_keep = normalize_analysis(s)
    out_replace = normalize_analysis(s, replace_hashtag=True)
    assert "#AI研究" in out_keep
    assert "！" not in out_keep
    assert "!" in out_keep
    assert "[HASHTAG]!" in out_replace


def test_normalize_analysis_hashtag_optional() -> None:
    """ハッシュタグの置換がオプションであることを確認する。"""
    s = "#自由研究 discussion"
    out_keep = normalize_analysis(s)
    out_replace = normalize_analysis(s, replace_hashtag=True)
    assert "#自由研究" in out_keep
    assert "[HASHTAG]" in out_replace


def test_normalization_version_exists() -> None:
    """正規化バージョンが定義されていることを確認する。"""
    assert isinstance(NORMALIZATION_VERSION, str)
    assert NORMALIZATION_VERSION
