import json
import pathlib
import re
import sys

samples = {"url": [], "unicode": [], "control": []}
try:
    with pathlib.Path("comments.jsonl").open("r", encoding="utf-8") as f:
        for line in f:
            try:
                c = json.loads(line)
                text = c.get("text", "")
                if not text:
                    continue
                if not samples["url"] and re.search(r"https?://[^\s]+", text):
                    samples["url"].append(c)
                if not samples["unicode"] and any(ord(char) > 0x7F for char in text):
                    samples["unicode"].append(c)
                is_ctrl = (
any(ord(char) < 32 and char not in "\n\r\t" for char in text) or "\u200b" in text
                )
                if not samples["control"] and is_ctrl:
                    samples["control"].append(c)
            except (json.JSONDecodeError, ValueError):
                # FIXME: デコード失敗行はスキップする。必要ならログ出力を追加する
                continue
except FileNotFoundError:
    sys.exit("Error: comments.jsonl not found")

for cat in ["url", "unicode", "control"]:
    if not samples[cat]:
        sys.stdout.write(f"CAT: {cat} | No sample found\n")
    for item in samples[cat]:
        t = item.get("text", "").replace("\n", " ")[:100]
        sys.stdout.write(f"CAT: {cat} | ID: {item.get('video_id')} | DATE: {item.get('time')} | TEXT: {t}\n")
