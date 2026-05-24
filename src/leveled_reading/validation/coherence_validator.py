from __future__ import annotations

from ..models import AdaptationResult, SceneChunk, StoryBible, ValidationIssue


def validate_coherence(scene: SceneChunk, adaptation: AdaptationResult, story_bible: StoryBible) -> tuple[float, list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    penalty = 0.0

    for character in scene.characters:
        aliases = story_bible.characters.get(character, {}).get("aliases", [character])
        if not any(alias in adaptation.adapted_text for alias in aliases):
            penalty += 8
            issues.append(
                ValidationIssue(
                    issue_id=f"{scene.scene_id}_coh_character_{len(issues) + 1:03d}",
                    scene_id=scene.scene_id,
                    severity="warning",
                    category="coherence",
                    message=f"Source character hint is not visible in adaptation: {character}",
                    suggestion="Check whether the character mention was omitted or renamed inconsistently.",
                )
            )

    for term, info in story_bible.terms.items():
        seen_in = info.get("seen_in", [])
        if seen_in and scene.scene_id in seen_in and term not in adaptation.adapted_text:
            penalty += 5
            issues.append(
                ValidationIssue(
                    issue_id=f"{scene.scene_id}_coh_term_{len(issues) + 1:03d}",
                    scene_id=scene.scene_id,
                    severity="warning",
                    category="coherence",
                    message=f"Previously preserved term is absent in this scene: {term}",
                    suggestion="Confirm whether the omission is intentional.",
                )
            )

    return max(0.0, 100.0 - penalty), issues

