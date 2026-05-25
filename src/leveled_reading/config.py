from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from .models import LevelProfile


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROFILE_DIR = ROOT / "config" / "level_profiles"


@dataclass
class Settings:
    provider: str = "mock"
    llm_api_key: str | None = None
    llm_model: str = "gpt-4.1-mini"
    llm_base_url: str | None = None
    output_dir: str = "outputs"
    temperature: float = 0.2
    max_output_tokens: int = 4096


def load_env_file(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def load_settings(env_path: str | Path = ".env") -> Settings:
    load_env_file(env_path)
    return Settings(
        provider=os.getenv("SAGAP_LLM_PROVIDER", "mock").strip().lower(),
        llm_api_key=os.getenv("SAGAP_LLM_API_KEY") or None,
        llm_model=os.getenv("SAGAP_LLM_MODEL", "gpt-4.1-mini"),
        llm_base_url=os.getenv("SAGAP_LLM_BASE_URL") or None,
        output_dir=os.getenv("SAGAP_OUTPUT_DIR", "outputs"),
        temperature=float(os.getenv("SAGAP_TEMPERATURE", "0.2")),
        max_output_tokens=int(os.getenv("SAGAP_MAX_OUTPUT_TOKENS", "4096")),
    )


def load_level_profile(level: str, profile_dir: str | Path = DEFAULT_PROFILE_DIR) -> LevelProfile:
    normalized = level.lower()
    path = Path(profile_dir) / f"{normalized}.json"
    if not path.exists():
        available = sorted(p.stem.upper() for p in Path(profile_dir).glob("*.json"))
        raise FileNotFoundError(f"Level profile not found: {path}. Available: {', '.join(available)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return LevelProfile.from_dict(data)
