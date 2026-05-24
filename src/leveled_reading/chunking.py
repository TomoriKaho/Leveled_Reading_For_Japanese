from __future__ import annotations

import re

from .models import Chapter, SceneChunk


SOFT_BOUNDARY_PATTERN = re.compile(r"(その時|翌日|次の日|しばらくして|それから|ある日|夏休み|冬休み|朝|夜|夕方)")
CHARACTER_HINT_PATTERN = re.compile(r"(先生|私|K|奥さん|父|母|友人|学生|主人)")


def extract_character_hints(text: str) -> list[str]:
    seen: list[str] = []
    for match in CHARACTER_HINT_PATTERN.finditer(text):
        value = match.group(1)
        if value not in seen:
            seen.append(value)
    return seen


def chunk_chapters(chapters: list[Chapter], max_scene_chars: int = 2500) -> list[SceneChunk]:
    scenes: list[SceneChunk] = []
    for chapter in chapters:
        buffer: list[str] = []
        start_index = 0
        scene_counter = 1

        for paragraph in chapter.paragraphs:
            candidate = "\n".join(buffer + [paragraph.text])
            should_cut = len(candidate) > max_scene_chars
            soft_cut = bool(buffer and SOFT_BOUNDARY_PATTERN.search(paragraph.text) and len("\n".join(buffer)) > max_scene_chars // 2)

            if should_cut or soft_cut:
                text = "\n".join(buffer).strip()
                scenes.append(
                    SceneChunk(
                        scene_id=f"{chapter.chapter_id}_sc{scene_counter:03d}",
                        chapter_id=chapter.chapter_id,
                        paragraph_start=start_index,
                        paragraph_end=paragraph.index - 1,
                        text=text,
                        characters=extract_character_hints(text),
                    )
                )
                scene_counter += 1
                buffer = [paragraph.text]
                start_index = paragraph.index
            else:
                if not buffer:
                    start_index = paragraph.index
                buffer.append(paragraph.text)

        if buffer:
            text = "\n".join(buffer).strip()
            scenes.append(
                SceneChunk(
                    scene_id=f"{chapter.chapter_id}_sc{scene_counter:03d}",
                    chapter_id=chapter.chapter_id,
                    paragraph_start=start_index,
                    paragraph_end=chapter.paragraphs[-1].index,
                    text=text,
                    characters=extract_character_hints(text),
                )
            )

    return scenes

