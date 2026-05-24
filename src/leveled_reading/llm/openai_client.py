from __future__ import annotations

import json
import re
from typing import Any

from ..config import Settings
from ..models import AdaptationResult, Annotation, LevelProfile, SceneChunk, ScenePlan, StoryBible, ValidationIssue, to_dict


class OpenAILLMClient:
    provider_name = "openai"

    def __init__(self, settings: Settings):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when SAGAP_LLM_PROVIDER=openai")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("Install the OpenAI dependency with: pip install -e '.[openai]'") from exc

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_name = settings.openai_model
        self.temperature = settings.temperature
        self.max_output_tokens = settings.max_output_tokens

    def plan_scene(self, scene: SceneChunk, story_bible: StoryBible, profile: LevelProfile) -> ScenePlan:
        data = self._complete_json(
            "scene planning",
            {
                "instruction": "Analyze the Japanese literary scene for graded adaptation. Return JSON only.",
                "schema": {
                    "summary": "short source-faithful summary",
                    "must_keep_events": ["events that must not be omitted"],
                    "characters": ["characters in the scene"],
                    "tone": "source tone",
                    "keywords_to_preserve": ["literary/cultural/theme words"],
                    "adaptation_notes": ["concrete rewrite constraints"],
                },
                "target_level": profile.level,
                "level_profile": to_dict(profile),
                "story_bible": to_dict(story_bible),
                "scene": to_dict(scene),
            },
        )
        return ScenePlan(
            scene_id=scene.scene_id,
            summary=str(data.get("summary", "")),
            must_keep_events=list(data.get("must_keep_events", [])),
            characters=list(data.get("characters", scene.characters)),
            tone=str(data.get("tone", "")),
            keywords_to_preserve=list(data.get("keywords_to_preserve", [])),
            adaptation_notes=list(data.get("adaptation_notes", [])),
        )

    def rewrite_scene(
        self,
        scene: SceneChunk,
        plan: ScenePlan,
        story_bible: StoryBible,
        profile: LevelProfile,
    ) -> AdaptationResult:
        data = self._complete_json(
            "graded literary adaptation",
            {
                "instruction": (
                    "Rewrite the scene for the target Japanese learner level. "
                    "Do not summarize. Use minimum necessary adaptation. "
                    "Preserve plot, point of view, character voice, and literary tone. "
                    "Return JSON only."
                ),
                "schema": {
                    "adapted_text": "rewritten Japanese text",
                    "annotations": [
                        {
                            "target_text": "annotated word or phrase",
                            "reading": "kana reading or null",
                            "explanation": "short learner-friendly explanation",
                            "reason": "why this annotation is needed",
                            "level_estimate": "estimated JLPT level or null",
                        }
                    ],
                    "edit_notes": ["important edit decisions"],
                },
                "target_level": profile.level,
                "level_profile": to_dict(profile),
                "story_bible": to_dict(story_bible),
                "scene_plan": to_dict(plan),
                "source_scene": to_dict(scene),
            },
        )
        return _adaptation_from_json(scene.scene_id, profile.level, data)

    def revise_scene(
        self,
        scene: SceneChunk,
        current: AdaptationResult,
        issues: list[ValidationIssue],
        story_bible: StoryBible,
        profile: LevelProfile,
    ) -> AdaptationResult:
        data = self._complete_json(
            "adaptation revision",
            {
                "instruction": (
                    "Revise only the parts needed to fix validation issues. "
                    "Do not make already-simple prose harder. Return JSON only."
                ),
                "schema": {
                    "adapted_text": "revised Japanese text",
                    "annotations": [
                        {
                            "target_text": "annotated word or phrase",
                            "reading": "kana reading or null",
                            "explanation": "short explanation",
                            "reason": "why needed",
                            "level_estimate": "estimated JLPT level or null",
                        }
                    ],
                    "edit_notes": ["revision notes"],
                },
                "target_level": profile.level,
                "level_profile": to_dict(profile),
                "story_bible": to_dict(story_bible),
                "source_scene": to_dict(scene),
                "current_adaptation": to_dict(current),
                "validation_issues": to_dict(issues),
            },
        )
        return _adaptation_from_json(scene.scene_id, profile.level, data)

    def _complete_json(self, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = (
            f"Task: {task}\n"
            "You are a Japanese-language education editor and literary adaptation assistant.\n"
            "Return a single valid JSON object. Do not wrap it in Markdown.\n\n"
            f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
        )
        response = self.client.responses.create(
            model=self.model_name,
            input=prompt,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
        )
        text = getattr(response, "output_text", None)
        if not text:
            text = str(response)
        return _parse_json_object(text)


def _parse_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if match:
            return json.loads(match.group(0))
        raise


def _adaptation_from_json(scene_id: str, target_level: str, data: dict[str, Any]) -> AdaptationResult:
    annotations = []
    for idx, item in enumerate(data.get("annotations", []), start=1):
        annotations.append(
            Annotation(
                annotation_id=f"{scene_id}_ann{idx:03d}",
                scene_id=scene_id,
                target_text=str(item.get("target_text", "")),
                reading=item.get("reading"),
                explanation=str(item.get("explanation", "")),
                reason=str(item.get("reason", "")),
                level_estimate=item.get("level_estimate"),
            )
        )
    return AdaptationResult(
        scene_id=scene_id,
        target_level=target_level,
        adapted_text=str(data.get("adapted_text", "")),
        annotations=annotations,
        edit_notes=list(data.get("edit_notes", [])),
    )

