# Leveled Reading For Japanese

This repository is now organized as a Codex skill package, not as a script-first application.

Primary artifact:

```text
sagap-literary-adaptation/SKILL.md
```

The skill contains the SAGAP workflow for Japanese literary graded adaptation:

- scene chunking;
- Story Bible construction;
- Reader Profile control;
- literary-preserving adaptation;
- learner annotations;
- evaluation and revision.

Optional helper:

```text
sagap-literary-adaptation/scripts/smoke_harness.py
```

The helper script is only for deterministic smoke checks and artifact generation. It is not the core method and should not be treated as the whole workflow.

To use the package in Codex, reference the skill folder directly or copy `sagap-literary-adaptation/` into a discoverable skills directory such as `~/.codex/skills/`.

