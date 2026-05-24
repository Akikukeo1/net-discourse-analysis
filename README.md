# net-discourse-analysis

<!-- NOTE: もし、論文を公開する場合は変更する。 -->

このリポジトリは、個人研究プロジェクトのコードを管理するためのものです。
現在、コードは開発段階にあります。コードの安定性やドキュメントの充実度はまだ十分ではありません。
論文は現在一般公開予定ではありませんが、コードはオープンソースで公開しています。コードの使用や貢献は歓迎しますが、安定性やドキュメントの不足に留意してください。

詳細なデータ取り扱い・制限事項については `DATA_POLICY.md` を参照してください。
このリポジトリへの貢献方法については `CONTRIBUTING.md` を参照してください。
セキュリティ問題の報告については `SECURITY.md` を参照してください。

## 環境構築

このプロジェクトは Python 3.14t を想定しています。環境構築には pip ではなく uv を使用してください。

> [!NOTE]
> Free Threading については、試験的に導入しています。恐らくは Free Threading なしの環境でもコードを一部変更すれば動作するはずですが、動作確認はしていません。

推奨エディターは Visual Studio Code です。

- uv: https://docs.astral.sh/uv/getting-started/installation/#standalone-installer
- visual studio code: https://code.visualstudio.com/

インストール後、以下のコマンドで依存関係をインストールしてください。

```bash
uv venv
uv sync
uv run pre-commit install  # 任意
```

スクリプトの実行は以下のコマンドで行います。

```bash
uv run python hoge.py
```

詳しくは、uv のドキュメントを参照してください。

## コードスタイル・テスト

uv run ruff check\
uv run ruff check --fix\
uv run ruff format\
uv run ty check\
uv run taplo fmt\
uv run mdformat .

uv run pytest tests/

```powershell
uv run ruff check --fix ; uv run ty check ; uv run ruff format ; uv run taplo fmt ; uv run mdformat . ; uv run pytest tests/
```

## ドキュメント

本プロジェクトでは、Sphinx を使用してドキュメントを生成しています。ドキュメントのビルドには以下のコマンドを使用してください。
docs/sphinx ディレクトリ内の `index.rst` を編集できます。

```bash
# HTMLへビルド
uv run sphinx-build -b html docs/sphinx docs/sphinx/_build
```

```bash
# APIドキュメント用定義ファイルを自動生成（上書き）
uv run sphinx-apidoc -f -s generated.rst -o docs/sphinx src/nda

# HTMLへビルド
uv run sphinx-build -b html docs/sphinx docs/sphinx/_build
```
