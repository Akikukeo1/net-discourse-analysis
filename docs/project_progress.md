# プロジェクト進捗ログ: CLI 修正と Pydantic モデルの活用、およびベンチマーク結果のキャッシュ化

このドキュメントは、プロジェクトの会話が長引いた際の記憶喪失を防ぐため、重要な実装内容や設計意図を記録・更新するファイルです。

______________________________________________________________________

## 1. 実施した修正内容

### A. YouTube コメントの引数不一致修正 (以前の対応)

`src/nda/cli.py` において、`collect` モジュール（`nda.collect.youtube`）の `sample_and_save` を呼び出す部分で、引数の不一致（`max_comments` -> `limit`）によるエラーを解消し、TodoTree コメントを追加しました。

### B. ベンチマーク初回のみ実行・一時キャッシュ（Git管理外）への保存の実装 (今回の対応)

CLI の実行時に毎回 CPU ベンチマークが起動され、起動完了までに時間がかかる問題を解決するため、ベンチマーク結果を Git 管理外の一時キャッシュファイルに永続化する仕組みを導入しました。

#### 修正前の課題 (Bug / Performance Issue & Portability Issue)

- 起動時に毎回 `benchmark(...)` 関数が呼び出され、各スレッド数での処理時間・CPU温度・電力を計測していたため、プログラムの起動自体に 30秒〜1分程度の待ち時間が発生していました。
- 設定ファイル `hardware.yaml` にベンチマーク実行フラグを直接保存すると、別のPCやサーバー環境にコードを移動した際に「ベンチマーク実行済み」と誤認され、その新しいハードウェア環境に最適化されたワーカー数が計測されない（ポータビリティが損なわれる）問題がありました。

#### 修正・設計のアプローチ

- **Git管理除外の一時ディレクトリの活用**: `.gitignore` にすでに定義されている `.cache/` ディレクトリを使用します。このディレクトリは Git バージョン管理の対象外となるため、他の環境にクローンや移動した際にはキャッシュが存在せず、自動的に「初回起動」と判断されて再計測が行われます。
- **キャッシュ用ロード・セーブの実装**: 設定ファイルである `hardware.yaml` には一切変更を加えず、環境固有のベンチマーク実行完了フラグ (`benchmark_run`) と最適なワーカー数 (`workers`) を、`.cache/benchmark_result.yaml` に保存・読み込みします。
- `BenchmarkSettings` クラス（`settings.py`）に `benchmark_run` フィールドを持たせ、`load_benchmark_cache` と `save_benchmark_cache` を実装。
- CLI 実行時 (`cli.py` の `main()`) に `load_benchmark_cache` を使ってキャッシュから結果を読み込んで設定に上書きマージし、キャッシュが見つからないか `benchmark_run` が `False` の場合のみ計測を行い、結果を `.cache/benchmark_result.yaml` に保存します。

______________________________________________________________________

## 2. 変更されたコードの詳細

### 1. `src/nda/configs/settings.py`

- `@dataclass(slots=True)` に `benchmark_run: bool = False` フィールドを追加。
- `_apply_setting` で `benchmark_run` の YAML パースをサポート。
- 一時キャッシュファイルのロードとセーブを行う関数 `load_benchmark_cache` および `save_benchmark_cache` を追加。

```python
def load_benchmark_cache(path: Path, settings: BenchmarkSettings) -> BenchmarkSettings:
    """キャッシュファイルからベンチマーク結果を読み込み、設定に適用する。"""
    if not path.exists():
        return settings

    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        if loaded and isinstance(loaded, Mapping):
            if "workers" in loaded and isinstance(loaded["workers"], int):
                settings.workers = loaded["workers"]
            if "benchmark_run" in loaded and isinstance(loaded["benchmark_run"], bool):
                settings.benchmark_run = loaded["benchmark_run"]
    except Exception as e:
        import logging as log

        log.warning("ベンチマークキャッシュの読み込みに失敗しました: %s", e)

    return settings


def save_benchmark_cache(path: Path, settings: BenchmarkSettings) -> None:
    """ベンチマーク結果をキャッシュファイルに保存する。"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "workers": settings.workers,
            "benchmark_run": settings.benchmark_run,
        }
        path.write_text(yaml.safe_dump(data, default_flow_style=False, allow_unicode=True), encoding="utf-8")
    except Exception as e:
        import logging as log

        log.warning("ベンチマークキャッシュの保存に失敗しました: %s", e)
```

### 2. `src/nda/cli.py`

- キャッシュファイルの保存パス `CACHE_PATH` を定義。
- `main()` 内で `load_benchmark_cache` を呼び出して設定をマージし、`settings.benchmark_run` を判定。

```python
# キャッシュファイルのパス定義 (.cache ディレクトリ以下)
CACHE_PATH = Path(__file__).resolve().parent.parent.parent / ".cache" / "benchmark_result.yaml"


def main() -> None:
    """設定を読み込み、CPU ベンチマークを実行する。"""
    settings = load_benchmark_settings(CONFIG_PATH)
    # NOTE: 一時キャッシュからベンチマーク情報をロードして上書きマージします
    settings = load_benchmark_cache(CACHE_PATH, settings)
    configure_logging(settings.log_level)

    # NOTE: すでにベンチマークが実行されている場合は、再実行をスキップして保存された設定を使用します。
    if settings.benchmark_run:
        log.info(
            "ベンチマークは実行済みです。スキップします。現在のワーカー数（workers）: %s",
            settings.workers,
        )
    else:
        log.info("初回起動のため、CPUベンチマークを実行して最適なワーカー数を決定します。")
        ...
        best_result = benchmark(...)
        # NOTE: 最適なワーカー数と実行済みフラグを一時キャッシュファイルに保存します。
        settings.workers = best_result.thread_count
        settings.benchmark_run = True
        save_benchmark_cache(CACHE_PATH, settings)
        log.info(
            "最適なワーカー数 (%s) を一時キャッシュファイル（%s）に保存しました。",
            settings.workers,
            CACHE_PATH.name,
        )
```

______________________________________________________________________

## 3. Pydantic モデルの活用について

YouTube コメントの保存処理（`sample_and_save` 内）では、`src/nda/models/comment.py` に定義されている **Pydantic モデル** を活用しています。

### 使用されている主なモデル

- **`Comment`**: コメント自体の ID、投稿プラットフォーム、本文テキスト、作成日時を保持するモデル。
- **`CommentMeta`**: いいね数や動画ID、投稿者IDなどの補助的メタ情報を保持するモデル。
- **`Annotation`**: 機械学習やLLMなどを用いてコメントを分類した際のアノテーション情報（信頼度やラベルなど）を保持するモデル。
- **`SampleRecord`**: 上記の `Comment`, `CommentMeta`, `Annotation` を1つのレコードに統合した、JSONL保存用のモデル。

### なぜ Pydantic なのか？ (初心者向け解説)

Pydantic を使うことで、外部から取得したデータが正しい型（UUID が文字列ではなく UUID 型になっているか、いいね数が負の数になっていないかなど）であるかを自動的にバリデーション（検証）できます。
また、`model_dump(mode="json")` を使うことで、複雑な Python オブジェクトを簡単に JSON 形式に変換（シリアライズ）してファイル保存できます。

______________________________________________________________________

## 4. 今後の作業・検証ポイント

- [ ] **CHECK**: 実際の YouTube 動画 URL を指定した場合に、スクレイピングツール（`youtube-comment-downloader`）が正しく動作するかどうかの環境依存テストを行う。
- [ ] **TODO**: 保存先のパス（`safe_normalized_samples.jsonl`）やサンプリングするコメントの上限値を、ハードコードではなく `hardware.yaml` 等の設定ファイルから動的に制御できるように設計を見直す。
- [ ] **NOTE**: 今後ベンチマークを意図的に再実行したいときのために、コマンドライン引数（例: `--force-benchmark`）でフラグをリセットできるような機能を追加してもよい。
- [x] **FIXED**: プロジェクトルートで `python main.py` を実行した際、`src` ディレクトリが Python のライブラリ検索パスに含まれず `ModuleNotFoundError: No module named 'nda'` が発生する問題。
  - **解決策**: `main.py` の冒頭部で `sys.path.insert(0, str(src_path))` を使って動的に `src` の絶対パスを追加する修正を施し、別の環境に移しても環境変数（`PYTHONPATH`）の設定なしでポータブルに起動できるよう改善しました。
