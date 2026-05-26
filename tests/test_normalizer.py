from __future__ import annotations

import re
import unicodedata

import pytest

from nda.normalization.normalizer import (
    MENTION_TOKEN,
    NORMALIZATION_VERSION,
    URL_TOKEN,
    normalize,
)

# HACK: 全角混在入力は可読性のため実文字で記述し、RUF001 を明示的に許可する
# ruff: noqa: RUF001


@pytest.mark.parametrize(
    "invalid_value",
    [
        pytest.param(None),
        pytest.param(123),
        pytest.param(45.6),
        pytest.param(["strではない文字列リスト"]),
        pytest.param({"k": "v"}),
        pytest.param(True),
    ],
)
def test_normalize_validates_input_type(invalid_value: object) -> None:
    """文字列以外の入力に対して TypeError を送出することを確認する。"""
    with pytest.raises(TypeError):
        # HACK: cast で型を偽造するのは冗長なので、チェッカーを黙らせる
        normalize(invalid_value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("", ""),
        pytest.param(" ", ""),
        pytest.param("     ", ""),
        pytest.param("　", ""),
        pytest.param("\n\n\n\r\n\t", ""),
        pytest.param("   \n", ""),
    ],
)
def test_normalize_returns_empty_for_blank_input(text: str, expected: str) -> None:
    """空文字または実質空文字の入力で空文字を返すことを確認する。"""
    assert normalize(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("http://example.com/page?id=1&name=test#hash", URL_TOKEN),
        pytest.param("HTTPS://EXAMPLE.COM", URL_TOKEN),
        pytest.param("www.example.co.jp/index.html", URL_TOKEN),
        pytest.param("検索はwww.google.comで", f"検索は{URL_TOKEN}"),
        pytest.param("http://a.com http://b.com", f"{URL_TOKEN} {URL_TOKEN}"),
        pytest.param("http://a.comhttp://b.com", URL_TOKEN),
        pytest.param("このサイト見てhttps://omoshi.roi.yo?id=3！！！", f"このサイト見て{URL_TOKEN}"),
    ],
)
def test_normalize_replaces_url(text: str, expected: str) -> None:
    """URL が置換されることを確認する。"""
    assert normalize(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("@user", MENTION_TOKEN),
        pytest.param("@user123!", f"{MENTION_TOKEN}!"),
        pytest.param("@ユーザーです。のです、", f"{MENTION_TOKEN}、"),
        pytest.param("@alice,@bob", f"{MENTION_TOKEN},{MENTION_TOKEN}"),
        pytest.param("info@example.com", "info@example.com"),
        pytest.param("(@user)と[@admin]", f"({MENTION_TOKEN})と[{MENTION_TOKEN}]"),
    ],
)
def test_normalize_replaces_mentions_and_preserves_punctuation(text: str, expected: str) -> None:
    """メンション置換と句読点の分離が仕様どおりに動作することを確認する。"""
    assert normalize(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("こんにちは\u200b世界", "こんにちは世界"),
        pytest.param("A\x00B\x07C\x1fD", "ABCD"),
        pytest.param("\ufeffサロゲートペア等", "サロゲートペア等"),
    ],
)
def test_normalize_removes_invisible_chars(text: str, expected: str) -> None:
    """ゼロ幅文字と制御文字が除去されることを確認する。"""
    assert normalize(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("  連続する   スペースの    削減  ", "連続するスペースの削減"),
        pytest.param("文字の間に\n改行や\tタブが\r\n混ざる", "文字の間に 改行や タブが 混ざる"),
        pytest.param("検索 エンジン", "検索エンジン"),
    ],
)
def test_normalize_normalizes_whitespace(text: str, expected: str) -> None:
    """空白や改行が正規化されることを確認する。"""
    assert normalize(text) == expected


def test_normalize_limits_repetition_marks() -> None:
    """記号連続が正規化されることを確認する。"""
    out = normalize("ああああああああーーーーーーーっっっっっっっっっ！！！！！！！")
    assert out == "あああーっっっ!!!"


@pytest.mark.parametrize(
    "text",
    [
        # NOTE: この2つは見た目は同じでも、中身は異なるので注意。
        pytest.param(
            "\u30c6\u3099\u30a3\u30b9\u30d5\u309a\u30ec\u30a4\u3092\u8cb7\u3063\u305f",
            id="NFD_Mac形式_確定",
        ),
        pytest.param(
            "ディスプレイを買った",
            id="NFC_標準形式_確定",
        ),
    ],
)
def test_normalize_handles_unicode_normalization(text: str) -> None:
    """NFD と NFC のどちらでも同じ結果に正規化されることを確認する。"""
    assert normalize(text) == "ディスプレイを買った"


def test_normalize_all_in_one_case() -> None:
    """複数要素が混在する入力でもトークン置換と不可視文字除去が維持されることを確認する。"""
    text = (
        " \x00  @yamada-san!!（詳細は www.example.com/マニュアル を参照のこと）\u200b\n"
        "失礼しましたーーーっ！！！   "
    )
    assert normalize(text) == f"{MENTION_TOKEN}!!(詳細は{URL_TOKEN}を参照のこと) 失礼しましたーっ!!!"


def test_normalization_version_format() -> None:
    """正規化バージョンが '数字.数字' 形式の文字列であることを確認する。"""
    # メジャー/マイナーともに先頭に不要な0を許可しない
    # 例: "0.1" は有効だが "00.1" や "0.01" は無効とする
    assert re.match(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)$", NORMALIZATION_VERSION) is not None
