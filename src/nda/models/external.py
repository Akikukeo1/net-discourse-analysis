from __future__ import annotations

from typing import TypedDict


class YouTubeComment(TypedDict, total=False):
    """youtube-comment-downloader が返すコメントの最小スキーマ。"""

    text: str
    time: str
