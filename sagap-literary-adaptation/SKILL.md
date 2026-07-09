---
name: sagap-literary-adaptation
description: Use for Japanese literary graded-reader adaptation with SAGAP: scene chunking, Story Bible, Reader Profile, literary-preserving rewrite, annotations, and evaluation. Trigger when adapting Japanese novels or stories for JLPT/learner levels, designing prompts or rubrics for literary simplification, building Story Bible/Reader Profile materials, or reviewing outputs for fidelity, readability, coherence, and literary tone.
---

# SAGAP Literary Adaptation

Use this skill to adapt Japanese literary texts into leveled reading materials. The primary mode is an agent workflow, not a script. Scripts are optional helpers for smoke checks or artifact generation.

## Core Stance

Treat the task as literary intralingual translation, not ordinary summarization.

Preserve:
- plot events and causal order;
- point of view and character voice;
- character names, titles, and relations;
- cultural terms and symbolic terms when they matter;
- ambiguity, silence, rhythm, and aftertaste.

Control:
- learner level;
- sentence length and grammar burden;
- kanji/furigana or annotation burden;
- cultural explanations;
- over-rewriting and over-summarization.

## Default Workflow

1. Identify the target reader.
   - If unspecified, assume an N3 literary learner.
   - Use a Reader Profile, not just a level label.
   - Read `references/reader-profile.md` when creating or revising a profile.

2. Segment the source into scenes.
   - Prefer narrative scene boundaries over fixed character counts.
   - Keep dialogue, action, and psychological movement intact.
   - Read `references/workflow.md` for chunking and scene planning details.

3. Build or update a Story Bible.
   - Track characters, aliases, relations, key events, cultural/symbolic terms, timeline, style, and constraints.
   - Read `references/story-bible.md` when extracting or validating Story Bible content.

4. Create a Scene Plan before rewriting.
   - Include summary, must-keep events, characters, tone, keywords to preserve, and adaptation notes.
   - Use this plan to prevent summary-like rewrites.

5. Rewrite with minimum necessary adaptation.
   - Do not make already-readable prose harder.
   - Do not make prose childish.
   - Preserve literary ambiguity; do not explain one interpretation as fact.
   - Read `references/prompt-templates.md` when constructing formal prompts.

6. Add learner support.
   - Annotate cultural terms, symbolic terms, proper nouns, recurring core terms, and character titles when needed.
   - Prefer rewriting ordinary difficult expressions and annotating literary/cultural terms.
   - Keep annotation density low enough not to break reading.

7. Evaluate and revise.
   - Check level fit, fidelity, coherence, literary tone, natural Japanese, and annotation usefulness.
   - Read `references/evaluation-rubric.md` for a rubric and failure taxonomy.

## Required Output Shape

For an adapted scene, provide:

```json
{
  "adapted_text": "rewritten Japanese text",
  "annotations": [
    {
      "target_text": "term",
      "reading": "かな or null",
      "explanation": "short learner-facing explanation",
      "reason": "cultural_term/theme_keyword/proper_noun/etc.",
      "level_estimate": "N2+ or null"
    }
  ],
  "edit_notes": ["important edit decisions"],
  "self_check": {
    "level_control": "...",
    "fidelity": "...",
    "coherence": "...",
    "literary_tone": "..."
  }
}
```

When the user wants prose rather than JSON, still use this structure internally and present a readable version.

## Use Tools Selectively

Do not default to running a script for the whole task. Use normal reading, analysis, and generation first.

Use `scripts/smoke_harness.py` only when:
- the user wants reproducible local artifacts;
- you need to sanity-check a Reader Profile / Story Bible / prompt package;
- you want a deterministic mock run before connecting a real LLM.

If running the script, say clearly that it is a smoke harness, not a real LLM experiment.

## Bundled Resources

- `references/workflow.md`: SAGAP procedure, scene planning, revision loop.
- `references/reader-profile.md`: Reader Profile schema and policy.
- `references/story-bible.md`: Story Bible schema and extraction rules.
- `references/prompt-templates.md`: Direct, Reader Profile, Story Bible, and Full SAGAP prompt patterns.
- `references/evaluation-rubric.md`: automatic and human-oriented evaluation criteria.
- `assets/reader-profiles/n3-literary.json`: starter N3 literary Reader Profile.
- `assets/templates/`: JSON templates for Story Bible, Scene Plan, and adaptation output.
- `assets/samples/synthetic-literary-smoke.txt`: tiny synthetic sample for smoke checks.
- `scripts/smoke_harness.py`: optional standard-library-only artifact generator.

