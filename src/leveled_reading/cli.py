from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_level_profile, load_settings
from .output import write_outputs
from .pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(prog="sagap", description="Story-aware graded adaptation pipeline for Japanese texts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    adapt = subparsers.add_parser("adapt", help="Run the adaptation pipeline.")
    adapt.add_argument("--input", required=True, help="UTF-8 Japanese source text file.")
    adapt.add_argument("--level", default="N3", help="Target level profile, e.g. N1, N2, N3, N4, N5.")
    adapt.add_argument("--title", default=None, help="Output title. Defaults to input file stem.")
    adapt.add_argument("--output", default=None, help="Output directory. Defaults to SAGAP_OUTPUT_DIR/<input>-<level>.")
    adapt.add_argument("--provider", default=None, choices=["mock", "api"], help="Override SAGAP_LLM_PROVIDER.")
    adapt.add_argument("--env", default=".env", help="Path to .env file.")
    adapt.add_argument("--max-scene-chars", type=int, default=2500, help="Maximum source chars per scene chunk.")
    adapt.add_argument("--max-revisions", type=int, default=1, help="Automatic revision attempts per scene.")

    profiles = subparsers.add_parser("profiles", help="Show a level profile summary.")
    profiles.add_argument("--level", default="N3")

    args = parser.parse_args()

    if args.command == "profiles":
        profile = load_level_profile(args.level)
        print(f"{profile.level}: {profile.description}")
        print(f"max_sentence_chars={profile.max_sentence_chars}")
        print(f"grammar_avoid={', '.join(profile.grammar_avoid) or '(none)'}")
        print(f"annotation_terms={', '.join(profile.annotation_terms) or '(none)'}")
        return

    settings = load_settings(args.env)
    input_path = Path(args.input)
    output = Path(args.output) if args.output else Path(settings.output_dir) / f"{input_path.stem}-{args.level.upper()}"
    result = run_pipeline(
        input_path=input_path,
        level=args.level,
        settings=settings,
        title=args.title,
        provider=args.provider,
        max_scene_chars=args.max_scene_chars,
        max_revisions=args.max_revisions,
    )
    profile = load_level_profile(args.level)
    out = write_outputs(result, output, input_path, profile, settings)
    passed = sum(1 for report in result.validations if report.passed)
    print(f"Wrote outputs to {out}")
    print(f"Scenes: {len(result.scenes)}; validations passed: {passed}/{len(result.validations)}")


if __name__ == "__main__":
    main()
