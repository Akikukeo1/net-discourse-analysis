import json
import pathlib
import sys
from typing import cast

from nda.normalization.normalizer import URL_PATTERN, ZERO_WIDTH

DEFAULT_INPUT_PATH = pathlib.Path(__file__).resolve().parent / "data" / "samples" / "safe_normalized_samples.jsonl"


def _resolve_input_path(argv: list[str]) -> pathlib.Path:
    if len(argv) > 1:
        return pathlib.Path(argv[1])
    return DEFAULT_INPUT_PATH


def _extract_text(record: dict[str, object]) -> str:
    comment = record.get("comment")
    if isinstance(comment, dict):
        comment_data = cast("dict[str, object]", comment)
        value = comment_data.get("text", "")
        return str(value)
    return str(record.get("text", ""))


def _extract_video_id(record: dict[str, object]) -> str | None:
    meta = record.get("meta")
    if isinstance(meta, dict):
        meta_data = cast("dict[str, object]", meta)
        video_id = meta_data.get("video_id")
        if video_id is not None:
            return str(video_id)
    value = record.get("video_id")
    return None if value is None else str(value)


def _extract_created_at_text(record: dict[str, object]) -> str | None:
    meta = record.get("meta")
    if isinstance(meta, dict):
        meta_data = cast("dict[str, object]", meta)
        extra = meta_data.get("extra")
        if isinstance(extra, dict):
            extra_data = cast("dict[str, object]", extra)
            created_at_text = extra_data.get("created_at_text")
            if created_at_text is not None:
                return str(created_at_text)
    value = record.get("time")
    return None if value is None else str(value)


samples = {"url": [], "unicode": [], "control": []}
input_path = _resolve_input_path(sys.argv)
try:
    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                c = json.loads(line)
                text = _extract_text(c)
                if not text:
                    continue
                if not samples["url"] and URL_PATTERN.search(text):
                    samples["url"].append(c)
                if not samples["unicode"] and any(ord(char) > 0x7F for char in text):
                    samples["unicode"].append(c)
                has_control = any(ord(char) < 32 and char not in "\n\r\t" for char in text)
                has_zero_width = any(ch in text for ch in ZERO_WIDTH)
                is_ctrl = has_control or has_zero_width
                if not samples["control"] and is_ctrl:
                    samples["control"].append(c)
            except (json.JSONDecodeError, ValueError):
                # FIXME: デコード失敗行はスキップする。必要ならログ出力を追加する
                continue
except FileNotFoundError:
    sys.exit(f"エラー: 入力ファイルが見つかりません: {input_path}")

for cat in ["url", "unicode", "control"]:
    if not samples[cat]:
        sys.stdout.write(f"CAT: {cat} | No sample found\n")
    for item in samples[cat]:
        text = _extract_text(item).replace("\n", " ")[:100]
        video_id = _extract_video_id(item)
        created_at_text = _extract_created_at_text(item)
        sys.stdout.write(f"CAT: {cat} | ID: {video_id} | DATE: {created_at_text} | TEXT: {text}\n")
