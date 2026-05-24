from __future__ import annotations

from pathlib import Path

from .chunking import chunk_chapters
from .config import Settings, load_level_profile
from .ingestion import load_text, split_chapters
from .llm import build_llm_client
from .models import CostRecord, PipelineResult
from .story import initialize_story_bible, update_story_bible
from .text_utils import rough_token_count
from .validation import validate_scene


def run_pipeline(
    input_path: str | Path,
    level: str,
    settings: Settings,
    title: str | None = None,
    provider: str | None = None,
    max_scene_chars: int = 2500,
    max_revisions: int = 1,
) -> PipelineResult:
    profile = load_level_profile(level)
    text = load_text(input_path)
    chapters = split_chapters(text)
    scenes = chunk_chapters(chapters, max_scene_chars=max_scene_chars)
    story_bible = initialize_story_bible(title or Path(input_path).stem, scenes)
    llm = build_llm_client(settings, provider_override=provider)

    adaptations = []
    validations = []
    costs = []

    for scene in scenes:
        plan = llm.plan_scene(scene, story_bible, profile)
        adaptation = llm.rewrite_scene(scene, plan, story_bible, profile)
        report = validate_scene(scene, adaptation, story_bible, profile)

        revision_count = 0
        while not report.passed and revision_count < max_revisions:
            blocking_issues = [issue for issue in report.issues if issue.severity in {"error", "warning"}]
            adaptation = llm.revise_scene(scene, adaptation, blocking_issues, story_bible, profile)
            report = validate_scene(scene, adaptation, story_bible, profile)
            revision_count += 1

        update_story_bible(story_bible, scene, plan, adaptation)
        adaptations.append(adaptation)
        validations.append(report)
        costs.append(
            CostRecord(
                provider=llm.provider_name,
                model=llm.model_name,
                prompt_tokens=rough_token_count(scene.text),
                completion_tokens=rough_token_count(adaptation.adapted_text),
                total_tokens=rough_token_count(scene.text) + rough_token_count(adaptation.adapted_text),
            )
        )

    return PipelineResult(
        story_bible=story_bible,
        scenes=scenes,
        adaptations=adaptations,
        validations=validations,
        costs=costs,
    )

