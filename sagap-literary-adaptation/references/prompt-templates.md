# Prompt Templates

Use these as patterns, not mandatory full strings.

## Direct Baseline

```text
Task: direct graded literary adaptation
You are a Japanese-language education editor and literary adaptation assistant.
Return JSON only.

以下の日本語文学テキストを、JLPT {target_level} 程度の学習者が読める文章に改編してください。
あらすじだけにせず、物語として読める文章を出力してください。
原文がすでに読みやすい場合は、不必要に難しくしたり簡単にしすぎたりしないでください。

【原文】
{source_scene}
```

## Reader Profile Controlled

```text
Task: Reader-Profile controlled graded literary adaptation
Return JSON only.

以下の Reader Profile に合わせて、原文を分級読解教材として改編してください。

Rules:
- Use minimum necessary adaptation.
- Prefer rewriting ordinary difficult expressions.
- Preserve and annotate literary/cultural/core terms.
- Avoid childish prose and mechanical short sentences.

【Reader Profile】
{reader_profile_json}

【原文】
{source_scene}
```

## Story Bible Controlled

```text
Task: Story-Bible controlled literary adaptation
Return JSON only.

以下の Story Bible と Scene Plan を守り、現在の scene を改編してください。
文学的な曖昧さ、人物関係、語りの視点を壊さないでください。

【Story Bible】
{story_bible_json}

【Scene Plan】
{scene_plan_json}

【原文】
{source_scene}
```

## Full SAGAP

```text
Task: SAGAP full graded literary adaptation
You are a Japanese-language education editor and literary adaptation assistant.
Return a single valid JSON object. Do not wrap it in Markdown.

以下の scene を、Reader Profile と Story Bible と Scene Plan に従って改編してください。

Important rules:
- 原文を単なるあらすじにしないでください。
- 重要な出来事、人物関係、心理の変化、場面の雰囲気を保ってください。
- 文化語・象徴語は、必要に応じて残して短く注釈してください。
- 原文の曖昧さを一つの解釈に固定しないでください。
- 目標読者に難しすぎる語彙・文法・長い修飾は調整してください。
- 原文がすでに十分に読みやすい場合は、書き換えすぎないでください。
- 高いレベルでは、原文をより難しくするのではなく、読解障害だけを最小限に調整してください。

【Reader Profile】
{reader_profile_json}

【Story Bible】
{story_bible_json}

【Scene Plan】
{scene_plan_json}

【原文】
{source_scene}

【Output JSON schema】
{
  "adapted_text": "rewritten Japanese literary graded reader text",
  "annotations": [
    {
      "target_text": "annotated word or phrase",
      "reading": "kana reading or null",
      "explanation": "short learner-friendly explanation",
      "reason": "cultural_term/theme_keyword/proper_noun/etc.",
      "level_estimate": "estimated JLPT level or null"
    }
  ],
  "edit_notes": ["important edit decisions"],
  "self_check": {
    "level_control": "vocabulary, grammar, sentence length, annotation load",
    "fidelity": "events and no over-summary",
    "coherence": "Story Bible terms, names, relations",
    "literary_tone": "voice, ambiguity, rhythm, non-childish style"
  }
}
```

## Revision Prompt

```text
Revise only the parts needed to fix validation issues.
Do not make already-simple prose harder.
Do not rewrite stable passages again.
Return JSON only.

【Current adaptation】
{current_adaptation}

【Validation issues】
{issues}

【Reader Profile / Story Bible / Scene Plan】
{controls}
```

