# Source Code Rules

## Python コーディングスタイル

- 型ヒントを使用してください。
- 静的解析ツール Ruff, ty を使用してコード品質を保ってください。
- logging を print の代わりに使用してください。
- エラーハンドリングを適切に行ってください。

```python
# 例: 型エラーと空文字の処理
if not isinstance(text, str):
    # None が渡される可能性があるため、型エラーを明示的に処理する
    raise TypeError(
        f"text は str 型である必要があります。 got: {type(text).__name__}"
    )

if not text or text.isspace():
    # 空文字や空白のみの文字列は早期に処理する
    # strip() より割り当てが少なく高速
    return ""
```

- ヘルパー関数は、可読性や再利用性が向上する場合にのみ使用してください。
- 1回しか使用しない短い処理は、インライン実装も検討してください。
- 過度な抽象化や細かすぎる分割は避けてください。

```python
# ヘルパー関数の例
# インラインで記述するよりも、コードの可読性と再利用性が向上しますが、1回しか使用しない場合はインラインで記述することも検討してください。
def _normalize_whitespace(text: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", text).strip()


def _remove_control_chars(text: str) -> str:
    return CONTROL_PATTERN.sub("", text)
```
