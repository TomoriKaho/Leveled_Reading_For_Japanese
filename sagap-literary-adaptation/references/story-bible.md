# Story Bible

Story Bible is the external narrative memory for adaptation. It is not a plot summary.

## Minimal Schema

```json
{
  "work": {
    "title": "こころ",
    "author": "夏目漱石",
    "narrative_voice": "一人称回想",
    "style_notes": ["心理描写", "含蓄", "関係の変化"]
  },
  "characters": {
    "先生": {
      "aliases": ["先生"],
      "role": "中心人物",
      "relation_rules": ["語り手との距離感を保つ"],
      "do_not_reveal": ["過去の秘密を早く説明しない"]
    }
  },
  "terms": {
    "下宿": {
      "type": "cultural_term",
      "policy": "preserve_with_note"
    }
  },
  "timeline": [
    {
      "scene_id": "C0001",
      "event": "語り手が先生に会う",
      "revealed_to_reader": true
    }
  ],
  "global_constraints": [
    "Do not explain ambiguity as a single fixed interpretation.",
    "Do not reveal future information early.",
    "Do not flatten psychological description into direct explanation."
  ]
}
```

## Extraction Rules

Track:
- characters and aliases;
- relation changes;
- scene events and causal links;
- locations and cultural objects;
- symbols and repeated motifs;
- narration style;
- ambiguity and hidden information.

Mark:
- `must_keep`: facts or terms that should survive adaptation;
- `preserve_with_note`: hard but important terms;
- `do_not_reveal`: information not yet available in the scene;
- `do_not_flatten`: psychological or symbolic ambiguity.

## Use During Adaptation

Before rewriting a scene, inject only relevant Story Bible entries:
- current characters;
- current relation state;
- must-keep events;
- terms appearing in scene;
- style constraints;
- hidden information constraints.

Avoid flooding the prompt with the entire story when only a few facts are needed.

