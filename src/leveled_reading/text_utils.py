from __future__ import annotations

import re


SENTENCE_END_PATTERN = re.compile(r"(?<=[。！？!?])\s*")


def split_sentences(text: str) -> list[str]:
    parts = [part.strip() for part in SENTENCE_END_PATTERN.split(text) if part.strip()]
    return parts or [text.strip()]


def strip_inline_annotation(text: str) -> str:
    return re.sub(r"（[^）]{1,80}）", "", text)


def rough_token_count(text: str) -> int:
    return max(1, len(text) // 2)


def extract_keywords(text: str, limit: int = 12) -> list[str]:
    candidates = re.findall(r"[一-龯ぁ-んァ-ンー]{2,}", text)
    stop = {"これ", "それ", "ため", "よう", "こと", "もの", "ここ", "そこ", "ただ"}
    counts: dict[str, int] = {}
    for candidate in candidates:
        if candidate in stop or len(candidate) > 12:
            continue
        counts[candidate] = counts.get(candidate, 0) + 1
    return [item for item, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]]

