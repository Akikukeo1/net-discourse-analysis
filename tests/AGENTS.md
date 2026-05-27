# Test Rules

## テストコードのコーディングスタイル

- テストには、pytest を使用してください。
- テスト関数は、test\_ で始まる名前にしてください。
- 複数のテストケースがある場合は、pytest.mark.parametrize を使用して、テストコードの重複を避けてください。

```python
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
        normalize(invalid_value)  # type: ignore  # noqa: PGH003
```

- 戻り値を検証するテストでは、expected を使用した比較を優先してください。
- pytest.raises は、例外検証が必要な場合にのみ使用してください。

```python
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
```

- fixture は、重複削減や可読性向上に明確な効果がある場合のみ使用してください。
- 過度な fixture のネストや依存は避けてください。
