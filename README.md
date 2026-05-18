# net-discourse-analysis

詳細なデータ取り扱い・制限事項については `DATA_POLICY.md` を参照してください。
このリポジトリへの貢献方法については `CONTRIBUTING.md` を参照してください。
セキュリティ問題の報告については `SECURITY.md` を参照してください。

## 環境構築

このプロジェクトは Python 3.14t を想定しています。環境構築には pip ではなく uv を使用してください。
> [!NOTE]
> Free Threading については、試験的に導入しています。恐らくは Free Threading なしの環境でも動作するはずですが、動作確認はしていません。
推奨エディターは Visual Studio Code で、Python 拡張機能をインストールして使用してください。

uv: https://docs.astral.sh/uv/getting-started/installation/#standalone-installer
visual studio code: https://code.visualstudio.com/

インストール後、以下のコマンドで依存関係をインストールしてください。

```bash
uv sync
```

スクリプトの実行は以下のコマンドで行います。

```bash
uv run python hoge.py
```

その他のコマンドについては、 uv のドキュメントを参照してください。

## コードスタイル

uv run ruff check
uv run ruff --fix
uv run ruff format
uv run ty check
