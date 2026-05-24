from __future__ import annotations

import json
from pathlib import Path

from .config import Settings
from .models import LevelProfile, PipelineResult, to_dict


def write_outputs(
    result: PipelineResult,
    output_dir: str | Path,
    source_path: str | Path,
    profile: LevelProfile,
    settings: Settings,
) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    (out / "adapted.md").write_text(_render_markdown(result, profile), encoding="utf-8")
    _write_json(out / "story_bible.json", result.story_bible)
    _write_json(out / "manifest.json", _manifest(result, source_path, profile, settings))
    _write_jsonl(out / "scenes.jsonl", result.scenes)
    _write_jsonl(out / "adaptations.jsonl", result.adaptations)
    _write_jsonl(out / "validation.jsonl", result.validations)
    _write_jsonl(out / "costs.jsonl", result.costs)
    return out


def _render_markdown(result: PipelineResult, profile: LevelProfile) -> str:
    lines = [
        f"# {result.story_bible.title}",
        "",
        f"- Target level: `{profile.level}`",
        f"- Scenes: `{len(result.scenes)}`",
        "",
    ]
    validation_by_scene = {report.scene_id: report for report in result.validations}
    for adaptation in result.adaptations:
        report = validation_by_scene.get(adaptation.scene_id)
        lines.append(f"## {adaptation.scene_id}")
        if report:
            lines.append(
                f"`level={report.level_score}` `fidelity={report.fidelity_score}` "
                f"`coherence={report.coherence_score}` `passed={report.passed}`"
            )
        lines.extend(["", adaptation.adapted_text, ""])
        if adaptation.annotations:
            lines.append("### Notes")
            for ann in adaptation.annotations:
                reading = f"（{ann.reading}）" if ann.reading else ""
                level = f" [{ann.level_estimate}]" if ann.level_estimate else ""
                lines.append(f"- **{ann.target_text}**{reading}{level}: {ann.explanation}")
            lines.append("")
        if report and report.issues:
            lines.append("### Validation Issues")
            for issue in report.issues:
                lines.append(f"- `{issue.severity}` `{issue.category}` {issue.message}")
            lines.append("")
    return "\n".join(lines)


def _manifest(result: PipelineResult, source_path: str | Path, profile: LevelProfile, settings: Settings) -> dict:
    actual_provider = result.costs[0].provider if result.costs else settings.provider
    actual_model = result.costs[0].model if result.costs else settings.openai_model
    return {
        "source_path": str(source_path),
        "title": result.story_bible.title,
        "target_level": profile.level,
        "provider": actual_provider,
        "model": actual_model,
        "scene_count": len(result.scenes),
        "adaptation_count": len(result.adaptations),
        "validation_passed": sum(1 for report in result.validations if report.passed),
        "validation_total": len(result.validations),
    }


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(to_dict(value), ensure_ascii=False, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, values: list[object]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for value in values:
            handle.write(json.dumps(to_dict(value), ensure_ascii=False) + "\n")
