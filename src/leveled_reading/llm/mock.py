from __future__ import annotations

import re

from ..models import AdaptationResult, Annotation, LevelProfile, SceneChunk, ScenePlan, StoryBible, ValidationIssue
from ..text_utils import extract_keywords, split_sentences


class MockLLMClient:
    provider_name = "mock"
    model_name = "deterministic-mock"

    def plan_scene(self, scene: SceneChunk, story_bible: StoryBible, profile: LevelProfile) -> ScenePlan:
        keywords = [word for word in extract_keywords(scene.text, limit=8) if word in profile.annotation_terms]
        if not keywords:
            keywords = extract_keywords(scene.text, limit=5)
        summary = scene.text.replace("\n", " ")[:120]
        return ScenePlan(
            scene_id=scene.scene_id,
            summary=summary,
            must_keep_events=[summary],
            characters=scene.characters,
            tone="literary, calm, source-faithful",
            keywords_to_preserve=keywords,
            adaptation_notes=[
                "Use minimum necessary adaptation.",
                "Split long sentences before replacing literary keywords.",
                f"Keep the result within {profile.level} reading load.",
            ],
        )

    def rewrite_scene(
        self,
        scene: SceneChunk,
        plan: ScenePlan,
        story_bible: StoryBible,
        profile: LevelProfile,
    ) -> AdaptationResult:
        text = scene.text
        for source, replacement in profile.replace_terms.items():
            text = text.replace(source, replacement)

        sentences = split_sentences(text)
        rewritten: list[str] = []
        for sentence in sentences:
            rewritten.extend(_split_long_sentence(sentence, profile.max_sentence_chars))

        adapted_text = "\n".join(rewritten)
        annotations = _build_annotations(scene.scene_id, adapted_text, profile)
        return AdaptationResult(
            scene_id=scene.scene_id,
            target_level=profile.level,
            adapted_text=adapted_text,
            annotations=annotations,
            edit_notes=["mock: deterministic minimum-necessary rewrite"],
        )

    def revise_scene(
        self,
        scene: SceneChunk,
        current: AdaptationResult,
        issues: list[ValidationIssue],
        story_bible: StoryBible,
        profile: LevelProfile,
    ) -> AdaptationResult:
        text = current.adapted_text
        for issue in issues:
            if issue.category == "sentence_length":
                sentences = split_sentences(text)
                text = "\n".join(
                    part
                    for sentence in sentences
                    for part in _split_long_sentence(sentence, max(18, profile.max_sentence_chars - 8))
                )
            if issue.category == "grammar":
                for pattern in profile.grammar_avoid:
                    text = text.replace(pattern, "")
        annotations = _build_annotations(scene.scene_id, text, profile)
        return AdaptationResult(
            scene_id=scene.scene_id,
            target_level=profile.level,
            adapted_text=text,
            annotations=annotations,
            edit_notes=current.edit_notes + ["mock: revised validation issues"],
        )


def _split_long_sentence(sentence: str, max_chars: int) -> list[str]:
    if len(sentence) <= max_chars:
        return [sentence]

    chunks = [chunk.strip() for chunk in re.split(r"、", sentence) if chunk.strip()]
    if len(chunks) <= 1:
        return [sentence]

    result: list[str] = []
    buffer = ""
    for chunk in chunks:
        candidate = f"{buffer}、{chunk}" if buffer else chunk
        if len(candidate) > max_chars and buffer:
            result.append(_ensure_period(buffer))
            buffer = chunk
        else:
            buffer = candidate
    if buffer:
        result.append(_ensure_period(buffer))
    return result


def _ensure_period(text: str) -> str:
    if text.endswith(("。", "！", "？", "!", "?")):
        return text
    return f"{text}。"


def _build_annotations(scene_id: str, text: str, profile: LevelProfile) -> list[Annotation]:
    annotations: list[Annotation] = []
    for term, data in profile.annotation_terms.items():
        if term not in text:
            continue
        annotations.append(
            Annotation(
                annotation_id=f"{scene_id}_ann{len(annotations) + 1:03d}",
                scene_id=scene_id,
                target_text=term,
                reading=data.get("reading"),
                explanation=data.get("explanation", ""),
                reason=data.get("reason", "out_of_level_or_literary_term"),
                level_estimate=data.get("level_estimate"),
            )
        )
    return annotations

