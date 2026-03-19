from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


APP_DIR_ENV = "REDCAPLITE_CONFIG_DIR"
DEFAULT_APP_DIR = Path.home() / ".config" / "redcaplite"
PROFILES_FILENAME = "profiles.json"


@dataclass
class Profile:
    """Named REDCap connection settings stored separately from tokens."""

    name: str
    url: str
    token_key: Optional[str] = None


class ProfileStore:
    """Persist CLI profiles in a small JSON file."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        self.config_dir = config_dir or self.default_config_dir()
        self.path = self.config_dir / PROFILES_FILENAME

    @staticmethod
    def default_config_dir() -> Path:
        configured_dir = os.getenv(APP_DIR_ENV)
        if configured_dir:
            return Path(configured_dir).expanduser()
        return DEFAULT_APP_DIR

    def load(self) -> Dict[str, Profile]:
        data = self._read_data()
        profiles: Dict[str, Profile] = {}
        for raw_profile in data.get("profiles", []):
            profile = Profile(**raw_profile)
            profiles[profile.name] = profile
        return profiles

    def save(self, profiles: Dict[str, Profile]) -> None:
        payload = {"profiles": [asdict(profile) for profile in profiles.values()]}
        self._write_data(payload)

    def get(self, name: str) -> Optional[Profile]:
        return self.load().get(name)

    def set(self, profile: Profile) -> Profile:
        profiles = self.load()
        profiles[profile.name] = profile
        self.save(profiles)
        return profile

    def list(self) -> List[Profile]:
        return sorted(self.load().values(), key=lambda profile: profile.name)

    def _read_data(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {"profiles": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write_data(self, data: Dict[str, Any]) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
