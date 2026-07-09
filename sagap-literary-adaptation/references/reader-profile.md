# Reader Profile

A Reader Profile is the target reader model. It is broader than a JLPT level label.

## Fields

```json
{
  "name": "N3 literary reader profile",
  "target_level": "N3",
  "description": "reader description",
  "known_vocabulary": ["先生"],
  "preserve_terms": ["先生", "羅生門"],
  "avoid_terms": ["邂逅"],
  "replace_terms": {"常に": "いつも"},
  "annotation_terms": {
    "下宿": {
      "reading": "げしゅく",
      "explanation": "部屋を借りて住むこと。また、その家。",
      "reason": "cultural_term",
      "level_estimate": "N2+"
    }
  },
  "grammar_preferred": ["〜ている", "〜ために"],
  "grammar_avoid": ["〜ざるを得ない"],
  "allow_out_of_level_if": ["proper_noun", "cultural_term", "theme_keyword", "character_title"],
  "sentence_max_chars": 42,
  "preferred_sentence_chars": [20, 42],
  "max_notes_per_500_chars": 5,
  "rewrite_strength": "moderate",
  "style_policy": "Keep literary and natural; avoid childish summary.",
  "preserve_literary_tone": true,
  "do_not_make_childish": true
}
```

## Policy

- Treat target level as reading burden control, not a demand to force all text into a mechanical vocabulary list.
- Grammar control can be stricter than vocabulary control.
- Preserve proper nouns, cultural terms, theme keywords, symbolic terms, repeated core terms, and character titles when they matter.
- Annotate preserved difficult terms briefly.
- For N1, use minimum intervention: do not make simple prose more difficult.
- For N5/N4, expect stronger simplification and more support; avoid claiming literary tone is fully preserved.

## Common Mistakes

- Using “N3” as a vague prompt instead of a profile.
- Replacing every difficult word, including literary keywords.
- Adding too many notes and breaking reading flow.
- Making N1 prose artificially more formal.
- Turning literary prose into a child-facing textbook.

