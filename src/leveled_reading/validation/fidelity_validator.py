from __future__ import annotations

from ..models import AdaptationResult, SceneChunk, ValidationIssue
from ..text_utils import extract_keywords, strip_inline_annotation


def validate_fidelity(scene: SceneChunk, adaptation: AdaptationResult) -> tuple[float, list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    source = strip_inline_annotation(scene.text)
    adapted = strip_inline_annotation(adaptation.adapted_text)
    penalty = 0.0

    if len(source) > 80:
        ratio = len(adapted) / max(1, len(source))
        if ratio < 0.45:
            penalty += 35
            issues.append(
                ValidationIssue(
                    issue_id=f"{scene.scene_id}_fid_summary",
                    scene_id=scene.scene_id,
                    severity="error",
                    category="fidelity",
                    message=f"Adapted text is very short relative to source; ratio={ratio:.2f}.",
                    suggestion="Expand the scene as narrative adaptation, not summary.",
                )
            )
        elif ratio < 0.60:
            penalty += 15
            issues.append(
                ValidationIssue(
                    issue_id=f"{scene.scene_id}_fid_compression",
                    scene_id=scene.scene_id,
                    severity="warning",
                    category="fidelity",
                    message=f"Adapted text may be compressed; ratio={ratio:.2f}.",
                    suggestion="Check whether events, reactions, and narration have been omitted.",
                )
            )

    keywords = extract_keywords(source, limit=10)
    if keywords:
        kept = [keyword for keyword in keywords if keyword in adapted]
        coverage = len(kept) / len(keywords)
        if coverage < 0.35:
            penalty += 20
            issues.append(
                ValidationIssue(
                    issue_id=f"{scene.scene_id}_fid_keywords",
                    scene_id=scene.scene_id,
                    severity="warning",
                    category="fidelity",
                    message=f"Low keyword coverage: {coverage:.2f}. Missing examples: {', '.join(keywords[:5])}",
                    suggestion="Verify that key events and terms were not deleted.",
                )
            )

    return max(0.0, 100.0 - penalty), issues

