from __future__ import annotations

from typing import Protocol

from ..models import AdaptationResult, LevelProfile, SceneChunk, ScenePlan, StoryBible, ValidationIssue


class LLMClient(Protocol):
    provider_name: str
    model_name: str

    def plan_scene(self, scene: SceneChunk, story_bible: StoryBible, profile: LevelProfile) -> ScenePlan:
        ...

    def rewrite_scene(
        self,
        scene: SceneChunk,
        plan: ScenePlan,
        story_bible: StoryBible,
        profile: LevelProfile,
    ) -> AdaptationResult:
        ...

    def revise_scene(
        self,
        scene: SceneChunk,
        current: AdaptationResult,
        issues: list[ValidationIssue],
        story_bible: StoryBible,
        profile: LevelProfile,
    ) -> AdaptationResult:
        ...

