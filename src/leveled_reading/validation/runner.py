from __future__ import annotations

from ..models import AdaptationResult, LevelProfile, SceneChunk, StoryBible, ValidationReport
from .coherence_validator import validate_coherence
from .fidelity_validator import validate_fidelity
from .language_validator import validate_language


def validate_scene(
    scene: SceneChunk,
    adaptation: AdaptationResult,
    story_bible: StoryBible,
    profile: LevelProfile,
) -> ValidationReport:
    level_score, language_issues = validate_language(scene, adaptation, profile)
    fidelity_score, fidelity_issues = validate_fidelity(scene, adaptation)
    coherence_score, coherence_issues = validate_coherence(scene, adaptation, story_bible)
    return ValidationReport(
        scene_id=scene.scene_id,
        level_score=round(level_score, 2),
        fidelity_score=round(fidelity_score, 2),
        coherence_score=round(coherence_score, 2),
        issues=language_issues + fidelity_issues + coherence_issues,
    )

