#!/usr/bin/env python3
"""Optional smoke harness for the SAGAP skill.

This script is not the primary workflow. It only checks that bundled skill
resources can produce a minimal Story Bible, Scene Plan, and Full SAGAP prompt.
It performs no real LLM generation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SAGAP skill smoke artifacts.")
    parser.add_argument("--skill-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source", type=Path, default=None)
    parser.add_argument("--profile", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    skill_dir = args.skill_dir.resolve()
    source = args.source or skill_dir / "assets" / "samples" / "synthetic-literary-smoke.txt"
    profile_path = args.profile or skill_dir / "assets" / "reader-profiles" / "n3-literary.json"
    output_dir = args.output_dir or skill_dir / "_smoke_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    source_text = source.read_text(encoding="utf-8").strip()
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    scene = {
        "scene_id": "C0001",
        "text": source_text,
    }
    story_bible = build_story_bible(source_text, profile)
    scene_plan = build_scene_plan(source_text, story_bible, profile)
    prompt = build_full_sagap_prompt(source_text, profile, story_bible, scene_plan)

    write_json(output_dir / "reader_profile.json", profile)
    write_json(output_dir / "scene.json", scene)
    write_json(output_dir / "story_bible.json", story_bible)
    write_json(output_dir / "scene_plan.json", scene_plan)
    (output_dir / "full_sagap.prompt.txt").write_text(prompt, encoding="utf-8")

    print(f"Wrote smoke artifacts to {output_dir}")


def build_story_bible(source_text: str, profile: dict) -> dict:
    characters = {}
    for name in ["私", "先生", "下人", "老婆", "君", "あなた"]:
        if name in source_text:
            characters[name] = {
                "aliases": [name],
                "notes": "Auto-detected for smoke check; review manually for real use.",
            }
    terms = {}
    for term in sorted(set(profile.get("preserve_terms", [])) | set(profile.get("annotation_terms", {}))):
        if term in source_text:
            terms[term] = {
                "type": profile.get("annotation_terms", {}).get(term, {}).get("reason", "preserve_term"),
                "policy": "preserve_with_note",
            }
    return {
        "work": {
            "title": "Smoke sample",
            "author": "Synthetic",
            "narrative_voice": "unspecified",
            "style_notes": ["Preserve literary tone and ambiguity."],
        },
        "characters": characters,
        "terms": terms,
        "timeline": [{"scene_id": "C0001", "event": first_sentence(source_text)}],
        "global_constraints": [
            "Do not summarize the scene into a plot outline.",
            "Do not explain literary ambiguity as a single fixed interpretation.",
            "Do not reveal future information early.",
        ],
    }


def build_scene_plan(source_text: str, story_bible: dict, profile: dict) -> dict:
    return {
        "scene_id": "C0001",
        "summary": first_sentence(source_text),
        "must_keep_events": [first_sentence(source_text)],
        "characters": sorted(story_bible["characters"]),
        "tone": "source-faithful, literary, learner-accessible",
        "keywords_to_preserve": sorted(story_bible["terms"]),
        "adaptation_notes": [
            "Use minimum necessary adaptation.",
            "Do not make already-readable prose harder.",
            "Do not make the prose childish or like a plot summary.",
            f"Prefer sentences around {profile.get('preferred_sentence_chars', [20, 42])}.",
        ],
    }


def build_full_sagap_prompt(source_text: str, profile: dict, story_bible: dict, scene_plan: dict) -> str:
    output_schema = {
        "adapted_text": "rewritten Japanese literary graded reader text",
        "annotations": [
            {
                "target_text": "annotated word or phrase",
                "reading": "kana reading or null",
                "explanation": "short learner-friendly explanation",
                "reason": "cultural_term/theme_keyword/proper_noun/etc.",
                "level_estimate": "estimated JLPT level or null",
            }
        ],
        "edit_notes": ["important edit decisions"],
        "self_check": {
            "level_control": "vocabulary, grammar, sentence length, annotation load",
            "fidelity": "events and no over-summary",
            "coherence": "Story Bible terms, names, relations",
            "literary_tone": "voice, ambiguity, rhythm, non-childish style",
        },
    }
    return "\n".join(
        [
            "Task: SAGAP full graded literary adaptation",
            "Return a single valid JSON object. Do not wrap it in Markdown.",
            "",
            "Rules:",
            "- 原文を単なるあらすじにしないでください。",
            "- 原文がすでに十分に読みやすい場合は、書き換えすぎないでください。",
            "- 文化語・象徴語は、必要に応じて残して短く注釈してください。",
            "- 原文の曖昧さを一つの解釈に固定しないでください。",
            "",
            "Reader Profile:",
            json.dumps(profile, ensure_ascii=False, indent=2),
            "",
            "Story Bible:",
            json.dumps(story_bible, ensure_ascii=False, indent=2),
            "",
            "Scene Plan:",
            json.dumps(scene_plan, ensure_ascii=False, indent=2),
            "",
            "Source Scene:",
            source_text,
            "",
            "Output JSON schema:",
            json.dumps(output_schema, ensure_ascii=False, indent=2),
        ]
    )


def first_sentence(text: str) -> str:
    for mark in ["。", "！", "？", "\n"]:
        index = text.find(mark)
        if index > 0:
            return text[: index + 1].strip()
    return text[:100].strip()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

