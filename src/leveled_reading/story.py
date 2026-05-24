from __future__ import annotations

from .models import AdaptationResult, SceneChunk, ScenePlan, StoryBible


def initialize_story_bible(title: str, scenes: list[SceneChunk]) -> StoryBible:
    bible = StoryBible(
        title=title,
        style_notes=[
            "Maintain the narrator's point of view unless the source scene changes it.",
            "Prefer minimum necessary adaptation over rewriting already-simple prose.",
            "Preserve recurring literary keywords through annotation when replacement would weaken the work.",
        ],
    )
    for scene in scenes:
        for character in scene.characters:
            bible.characters.setdefault(character, {"aliases": [character], "notes": []})
    return bible


def update_story_bible(bible: StoryBible, scene: SceneChunk, plan: ScenePlan, adaptation: AdaptationResult) -> None:
    for character in plan.characters:
        bible.characters.setdefault(character, {"aliases": [character], "notes": []})

    for keyword in plan.keywords_to_preserve:
        bible.terms.setdefault(keyword, {"reason": "preserve_keyword", "seen_in": []})
        if scene.scene_id not in bible.terms[keyword]["seen_in"]:
            bible.terms[keyword]["seen_in"].append(scene.scene_id)

    bible.timeline.append(
        {
            "scene_id": scene.scene_id,
            "summary": plan.summary,
            "characters": plan.characters,
            "adapted_chars": len(adaptation.adapted_text),
        }
    )

