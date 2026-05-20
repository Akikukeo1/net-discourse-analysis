from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from nda.models.comment import Annotation, Comment, CommentMeta


def test_comment_and_meta_creation() -> None:
    """Comment と CommentMeta の作成を検証する。"""
    cid = uuid4()
    now = datetime.now(UTC)
    c = Comment(id=cid, platform="youtube", text="hello", created_at=now)
    m = CommentMeta(comment_id=cid, likes=10, reposts=2)

    assert c.id == cid
    assert c.platform == "youtube"
    assert c.text == "hello"
    assert m.comment_id == cid
    assert m.likes == 10


def test_annotation_requires_experiment_id() -> None:
    """experiment_id が無い場合に ValidationError を発生させることを検証する。"""
    cid = uuid4()
    with pytest.raises(ValidationError):
        # missing experiment_id should raise — model_validate を使って静的解析エラーを回避
        Annotation.model_validate({"comment_id": cid, "method": "llm"})


def test_annotation_labels_and_fields() -> None:
    """Annotation のラベルとフィールドが正しく設定されることを検証する。"""
    cid = uuid4()
    ann = Annotation(
        comment_id=cid,
        experiment_id="exp-001",
        labels={"sarcasm": 0.6},
        method="llm",
        model="gpt-x",
        version="v1",
        confidence=0.9,
        created_at=datetime.now(UTC),
    )

    assert ann.experiment_id == "exp-001"
    assert isinstance(ann.labels, dict)
    assert ann.labels["sarcasm"] == pytest.approx(0.6)
