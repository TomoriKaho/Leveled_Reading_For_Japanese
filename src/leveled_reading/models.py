from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class LevelProfile:
    level: str
    description: str
    max_sentence_chars: int
    preferred_sentence_chars: tuple[int, int]
    grammar_preferred: list[str] = field(default_factory=list)
    grammar_avoid: list[str] = field(default_factory=list)
    replace_terms: dict[str, str] = field(default_factory=dict)
    annotation_terms: dict[str, dict[str, str]] = field(default_factory=dict)
    allow_out_of_level_if: list[str] = field(default_factory=list)
    max_notes_per_500_chars: int = 5
    preserve_literary_tone: bool = True
    do_not_make_childish: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LevelProfile":
        preferred = data.get("preferred_sentence_chars", [20, 45])
        return cls(
            level=data["level"],
            description=data.get("description", ""),
            max_sentence_chars=int(data.get("max_sentence_chars", 45)),
            preferred_sentence_chars=(int(preferred[0]), int(preferred[1])),
            grammar_preferred=list(data.get("grammar_preferred", [])),
            grammar_avoid=list(data.get("grammar_avoid", [])),
            replace_terms=dict(data.get("replace_terms", {})),
            annotation_terms=dict(data.get("annotation_terms", {})),
            allow_out_of_level_if=list(data.get("allow_out_of_level_if", [])),
            max_notes_per_500_chars=int(data.get("max_notes_per_500_chars", 5)),
            preserve_literary_tone=bool(data.get("preserve_literary_tone", True)),
            do_not_make_childish=bool(data.get("do_not_make_childish", True)),
        )


@dataclass
class Paragraph:
    paragraph_id: str
    text: str
    index: int


@dataclass
class Chapter:
    chapter_id: str
    title: str
    paragraphs: list[Paragraph]


@dataclass
class SceneChunk:
    scene_id: str
    chapter_id: str
    paragraph_start: int
    paragraph_end: int
    text: str
    characters: list[str] = field(default_factory=list)
    location_hint: str | None = None


@dataclass
class StoryBible:
    title: str
    characters: dict[str, dict[str, Any]] = field(default_factory=dict)
    terms: dict[str, dict[str, Any]] = field(default_factory=dict)
    style_notes: list[str] = field(default_factory=list)
    timeline: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ScenePlan:
    scene_id: str
    summary: str
    must_keep_events: list[str]
    characters: list[str]
    tone: str
    keywords_to_preserve: list[str]
    adaptation_notes: list[str]


@dataclass
class Annotation:
    annotation_id: str
    scene_id: str
    target_text: str
    reading: str | None
    explanation: str
    reason: str
    level_estimate: str | None = None


@dataclass
class AdaptationResult:
    scene_id: str
    target_level: str
    adapted_text: str
    annotations: list[Annotation] = field(default_factory=list)
    edit_notes: list[str] = field(default_factory=list)


@dataclass
class ValidationIssue:
    issue_id: str
    scene_id: str
    severity: str
    category: str
    message: str
    suggestion: str | None = None


@dataclass
class ValidationReport:
    scene_id: str
    level_score: float
    fidelity_score: float
    coherence_score: float
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(issue.severity != "error" for issue in self.issues)


@dataclass
class CostRecord:
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float | None = None


@dataclass
class PipelineResult:
    story_bible: StoryBible
    scenes: list[SceneChunk]
    adaptations: list[AdaptationResult]
    validations: list[ValidationReport]
    costs: list[CostRecord] = field(default_factory=list)


def to_dict(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, list):
        return [to_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: to_dict(item) for key, item in value.items()}
    return value

