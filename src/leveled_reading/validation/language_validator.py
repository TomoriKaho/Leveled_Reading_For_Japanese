from __future__ import annotations

from ..models import AdaptationResult, LevelProfile, SceneChunk, ValidationIssue
from ..text_utils import split_sentences


def validate_language(scene: SceneChunk, adaptation: AdaptationResult, profile: LevelProfile) -> tuple[float, list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    penalty = 0.0
    text = adaptation.adapted_text

    for idx, sentence in enumerate(split_sentences(text), start=1):
        if len(sentence) > profile.max_sentence_chars:
            penalty += min(18, (len(sentence) - profile.max_sentence_chars) * 0.6)
            issues.append(
                ValidationIssue(
                    issue_id=f"{scene.scene_id}_lang_len_{idx:03d}",
                    scene_id=scene.scene_id,
                    severity="warning" if len(sentence) < profile.max_sentence_chars * 1.4 else "error",
                    category="sentence_length",
                    message=f"Sentence {idx} is {len(sentence)} chars; target max is {profile.max_sentence_chars}.",
                    suggestion="Split the sentence or reduce embedded modifiers.",
                )
            )

    for pattern in profile.grammar_avoid:
        if pattern and pattern in text:
            penalty += 8
            issues.append(
                ValidationIssue(
                    issue_id=f"{scene.scene_id}_lang_grammar_{len(issues) + 1:03d}",
                    scene_id=scene.scene_id,
                    severity="warning",
                    category="grammar",
                    message=f"Potentially over-level grammar pattern appears: {pattern}",
                    suggestion="Rewrite with a simpler construction unless it is deliberately preserved.",
                )
            )

    annotated_terms = {annotation.target_text for annotation in adaptation.annotations}
    for term, data in profile.annotation_terms.items():
        if term in text and term not in annotated_terms:
            penalty += 5
            issues.append(
                ValidationIssue(
                    issue_id=f"{scene.scene_id}_lang_annotation_{len(issues) + 1:03d}",
                    scene_id=scene.scene_id,
                    severity="warning",
                    category="annotation",
                    message=f"Term appears without structured annotation: {term}",
                    suggestion=data.get("explanation", "Add a short learner-facing note."),
                )
            )

    notes_limit = max(1, (len(text) // 500 + 1) * profile.max_notes_per_500_chars)
    if len(adaptation.annotations) > notes_limit:
        penalty += 6
        issues.append(
            ValidationIssue(
                issue_id=f"{scene.scene_id}_lang_annotation_density",
                scene_id=scene.scene_id,
                severity="warning",
                category="annotation_density",
                message=f"Too many annotations: {len(adaptation.annotations)} notes, recommended <= {notes_limit}.",
                suggestion="Prefer rewriting ordinary difficult terms and annotating only literary/cultural keywords.",
            )
        )

    return max(0.0, 100.0 - penalty), issues

