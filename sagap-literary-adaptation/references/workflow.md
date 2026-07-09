# SAGAP Workflow

## Purpose

SAGAP is a skill workflow for Japanese literary graded adaptation. It should guide an agent through controlled literary rewriting. It is not primarily a script pipeline.

## Procedure

1. **Source orientation**
   - Identify work, author, genre, narrative voice, target excerpt, and copyright/provenance.
   - Note whether the task is full adaptation, scene adaptation, prompt design, evaluation, or thesis documentation.

2. **Reader Profile**
   - Load or create a Reader Profile.
   - Default to `assets/reader-profiles/n3-literary.json` when the user does not specify a level.
   - Confirm whether the target is strict level control, minimum intervention, or literary preservation.

3. **Scene chunking**
   - Split by narrative units: place/time/person/action/psychological shift.
   - Avoid cutting in the middle of dialogue, a single action, or a key psychological transition.
   - Use paragraph boundaries only as a first approximation.

4. **Story Bible construction**
   - Extract characters, aliases, relations, locations, terms, must-keep events, timeline, and style notes.
   - Mark information that must not be revealed early.
   - Mark ambiguous points that must remain ambiguous.

5. **Scene Plan**
   - Before rewriting each scene, create:
     - short source-faithful summary;
     - must-keep events;
     - characters;
     - tone;
     - keywords to preserve;
     - adaptation notes.

6. **Rewrite**
   - Apply minimum necessary adaptation.
   - Preserve point of view, event order, relation nuance, literary tone, and ambiguity.
   - Simplify excessive sentence complexity.
   - Preserve cultural/symbolic/core terms with annotations when needed.

7. **Validation**
   - Level: sentence length, grammar burden, vocabulary burden, kanji/furigana/annotation load.
   - Fidelity: event coverage, no over-summary, no invented facts.
   - Coherence: terms, names, relations, timeline, hidden information.
   - Literary tone: voice, rhythm, ambiguity, atmosphere, non-childishness.

8. **Revision**
   - Revise only the parts needed to fix validation issues.
   - Do not rewrite stable passages again.
   - Keep an edit note for each major decision.

## Baseline Variants for Experiments

- `direct_prompt`: source + target level only.
- `reader_profile_only`: source + Reader Profile.
- `story_bible_only`: source + Story Bible.
- `full_sagap`: source + Reader Profile + Story Bible + Scene Plan + validation.

Use these variants for ablation-style thesis experiments.

