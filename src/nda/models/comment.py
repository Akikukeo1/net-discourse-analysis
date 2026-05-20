from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Comment(BaseModel):
    """コメント(投稿)を表すモデル。

    Attributes:
        id: コメントの UUID。
        platform: プラットフォーム名(例: "youtube")。
        text: コメント本文。
        created_at: 作成日時(任意)。
        classification_label: 分類ラベル(任意)。

    """

    id: UUID
    platform: str
    text: str
    created_at: datetime | None = None
    classification_label: str | None = None


class CommentMeta(BaseModel):
    """コメントに紐づくメタ情報。

    Attributes:
        comment_id: 対応するコメントの UUID。
        likes: いいね数(任意)。
        reposts: リポスト数(任意)。
        replies: 返信数(任意)。
        video_id: 動画 ID(任意)。
        author_id: 投稿者 ID(任意)。
        extra: その他の任意メタ情報。

    """

    comment_id: UUID
    likes: int | None = None
    reposts: int | None = None
    replies: int | None = None
    video_id: str | None = None
    author_id: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class Annotation(BaseModel):
    """コメントに対するアノテーション情報。

    Attributes:
        comment_id: 注釈対象のコメント UUID。
        experiment_id: 実験やデータセットの識別子。
        classification_label: 全体の分類ラベル(任意)。
        labels: ラベルとスコアの辞書。
        method: アノテーション取得方法(例: "llm")。
        model: 使用モデル(任意)。
        version: モデルのバージョン(任意)。
        confidence: 信頼度(任意)。
        created_at: 作成日時(任意)。

    """

    comment_id: UUID
    experiment_id: str
    classification_label: str | None = None
    labels: dict[str, float] = Field(default_factory=dict)
    method: str
    model: str | None = None
    version: str | None = None
    confidence: float | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")
