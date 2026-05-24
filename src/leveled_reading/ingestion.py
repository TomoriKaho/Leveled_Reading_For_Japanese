from __future__ import annotations

import re
from pathlib import Path

from .models import Chapter, Paragraph


CHAPTER_PATTERN = re.compile(r"^(第[一二三四五六七八九十百千0-9]+[章節]|[0-9]+[.、]\s*.+|Chapter\s+\d+)", re.I)


def normalize_text(text: str) -> str:
    text = text.replace("\ufeff", "")
    text = text.replace("\u3000", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_text(path: str | Path) -> str:
    return normalize_text(Path(path).read_text(encoding="utf-8"))


def split_paragraphs(text: str) -> list[Paragraph]:
    blocks = [block.strip() for block in re.split(r"\n\s*\n|\n", text) if block.strip()]
    return [Paragraph(paragraph_id=f"p{idx:04d}", text=block, index=idx) for idx, block in enumerate(blocks)]


def split_chapters(text: str) -> list[Chapter]:
    paragraphs = split_paragraphs(text)
    if not paragraphs:
        return []

    chapters: list[Chapter] = []
    current_title = "本文"
    current: list[Paragraph] = []
    chapter_index = 1

    for paragraph in paragraphs:
        if CHAPTER_PATTERN.match(paragraph.text) and current:
            chapters.append(
                Chapter(
                    chapter_id=f"ch{chapter_index:02d}",
                    title=current_title,
                    paragraphs=current,
                )
            )
            chapter_index += 1
            current_title = paragraph.text
            current = []
            continue
        if CHAPTER_PATTERN.match(paragraph.text) and not current:
            current_title = paragraph.text
            continue
        current.append(paragraph)

    if current:
        chapters.append(Chapter(chapter_id=f"ch{chapter_index:02d}", title=current_title, paragraphs=current))

    return chapters

