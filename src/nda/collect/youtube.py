"""YouTube コメントの採取と保存を担当するモジュール。

1. `fetch_comments` で YouTube コメントを取得する
2. `iter_samples` で URL / 非ASCII / 制御文字の代表サンプルを抽出する
3. `sample_and_save` で `data/samples/safe_normalized_samples.jsonl` に JSONL 保存する

正規化はこのモジュールでは実行しない。保存後の `SampleRecord.comment.text` に対して
`nda.normalization.normalizer` の API を適用する運用を想定する。

想定フロー例:

1. `sample_and_save(...)` で JSONL を生成
2. JSONL を読み込む
3. 各レコードの `comment.text` に `normalize_safe` または `normalize_analysis` を適用
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import TypedDict, cast
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from pydantic import BaseModel, ConfigDict
from youtube_comment_downloader import YoutubeCommentDownloader

from nda.models.comment import Annotation, Comment, CommentMeta
from nda.models.external import YouTubeComment
from nda.normalization.labels import NormalizationLabel
from nda.normalization.normalizer import NORMALIZATION_VERSION

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data" / "samples"
DATA_DIR.mkdir(parents=True, exist_ok=True)

URL_LABEL = NormalizationLabel.URL
UNICODE_LABEL = NormalizationLabel.UNICODE
CONTROL_LABEL = NormalizationLabel.CONTROL


class SampleRecord(BaseModel):
    """サンプル出力用の統合レコード。"""

    comment: Comment
    meta: CommentMeta
    annotation: Annotation

    model_config = ConfigDict(extra="forbid")


class SampleSource(TypedDict):
    """採取時に保持する最小限のソース情報。"""

    text: str
    created_at_text: str


def _extract_video_id(video_url: str) -> str | None:
    parsed = urlparse(video_url)
    query_id = parse_qs(parsed.query).get("v")
    if query_id:
        return query_id[0]
    if parsed.netloc.endswith("youtu.be"):
        short_id = parsed.path.lstrip("/")
        return short_id or None
    return None


def _contains_url(text: str) -> bool:
    return "http://" in text or "https://" in text or "www." in text


def _contains_non_ascii(text: str) -> bool:
    """非ASCII文字を含むかを判定する。

    これは Unicode Normalization の検出ではなく、サンプル採取のためのヒューリスティック。
    """
    return any(ord(ch) > 127 for ch in text)


def _contains_control(text: str) -> bool:
return any(ord(ch) < 32 and ch not in "\n\r\t" for ch in text)


def _build_sample_record(
    *,
    text: str,
    label: NormalizationLabel,
    video_id: str | None,
    created_at_text: str,
) -> SampleRecord:
    comment_id = uuid4()
    comment = Comment(
        id=comment_id,
        platform="youtube",
        text=text,
    )
    meta = CommentMeta(
        comment_id=comment_id,
        video_id=video_id,
        extra={"created_at_text": created_at_text},
    )
    annotation = Annotation(
        comment_id=comment_id,
        experiment_id=f"safe-normalized:{NORMALIZATION_VERSION}",
        method="heuristic",
        labels={label.value: 1.0},
        version=NORMALIZATION_VERSION,
    )
    return SampleRecord(comment=comment, meta=meta, annotation=annotation)


def _build_sample_source(*, text: str, created_at_text: str) -> SampleSource:
    """採取時に保持する最小限のソース情報を作る。"""
    return SampleSource(text=text, created_at_text=created_at_text)


def fetch_comments(video_url: str, limit: int = 200) -> Iterable[YouTubeComment]:
    """動画 URL からコメントを取得するジェネレータ。

    取得には `youtube-comment-downloader` を利用する。
    """
    downloader = YoutubeCommentDownloader()
    comments = downloader.get_comments_from_url(video_url)
    for i, c in enumerate(comments):
        if i >= limit:
            break
        yield cast(YouTubeComment, c)


def iter_samples(video_url: str, limit: int = 200) -> Iterable[SampleRecord]:
    """動画 URL から採取したサンプルを逐次生成する。

    この関数は採取とラベル付けのみを行い、`comment.text` は未正規化の生テキストを保持する。
    正規化が必要な場合は、保存後または呼び出し側で
    `nda.normalization.normalizer.normalize_safe` などを適用する。
    """
    video_id = _extract_video_id(video_url)
    found_by_label: dict[NormalizationLabel, SampleSource | None] = {
        URL_LABEL: None,
        UNICODE_LABEL: None,
        CONTROL_LABEL: None,
    }

    # TODO: preserve_newlines=False の切り替えを追加し、行分割特徴も採取できるようにする
    for c in fetch_comments(video_url, limit=limit):
        text = str(c.get("text", ""))
        if not text:
            continue
        created_at_text = str(c.get("time", ""))
        if found_by_label[URL_LABEL] is None and _contains_url(text):
            found_by_label[URL_LABEL] = _build_sample_source(
                text=text,
                created_at_text=created_at_text,
            )
        if found_by_label[UNICODE_LABEL] is None and _contains_non_ascii(text):
            found_by_label[UNICODE_LABEL] = _build_sample_source(
                text=text,
                created_at_text=created_at_text,
            )
        if found_by_label[CONTROL_LABEL] is None and _contains_control(text):
            found_by_label[CONTROL_LABEL] = _build_sample_source(
                text=text,
                created_at_text=created_at_text,
            )
        if all(found_by_label.values()):
            break

    for label in (URL_LABEL, UNICODE_LABEL, CONTROL_LABEL):
        source = found_by_label[label]
        if source is None:
            continue
        yield _build_sample_record(
            text=source["text"],
            label=label,
            video_id=video_id,
            created_at_text=source["created_at_text"],
        )


def sample_and_save(video_url: str, out_path: str | Path | None = None, limit: int = 200) -> Path:
    """安全化サンプルを抽出して JSONL に保存する。

    保存されるフィールドはデータポリシーに合わせる。

    NOTE: この関数は正規化処理を行わない。ここで保存される `comment.text` は採取時点の
    テキストであり、正規化は保存後に `nda.normalization.normalizer` で実行する。
    """
    if out_path is None:
        out_path = DATA_DIR / "safe_normalized_samples.jsonl"
    out_path = Path(out_path)

    with out_path.open("w", encoding="utf-8") as fh:
        for sample in iter_samples(video_url, limit=limit):
            payload = sample.model_dump(mode="json", exclude_none=True)
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")

    return out_path
