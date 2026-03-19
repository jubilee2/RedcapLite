from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


CONFIG_DIR_ENV = "REDCAPLITE_CONFIG_DIR"
DEFAULT_CONFIG_DIR = Path.home() / ".config" / "redcaplite"
PROFILES_FILE_NAME = "profiles.json"


@dataclass(frozen=True)
class Profile:
    name: str
    url: str


class ProfileStore:
    def __init__(self, config_dir: Optional[Path] = None) -> None:
        self.config_dir = config_dir or _default_config_dir()
        self.path = self.config_dir / PROFILES_FILE_NAME

    def get(self, profile_name: str) -> Optional[Profile]:
        profiles = self._load()
        profile_data = profiles.get(profile_name)
        if profile_data is None:
            return None
        return Profile(name=profile_name, url=profile_data["url"])

    def save(self, profile: Profile) -> None:
        profiles = self._load()
        profiles[profile.name] = {"url": profile.url}
        self._write(profiles)

    def exists(self, profile_name: str) -> bool:
        return self.get(profile_name) is not None

    def _load(self) -> Dict[str, Dict[str, str]]:
        if not self.path.exists():
            return {}
        with self.path.open("r", encoding="utf-8") as file_obj:
            return json.load(file_obj)

    def _write(self, data: Dict[str, Dict[str, str]]) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file_obj:
            json.dump(data, file_obj, indent=2, sort_keys=True)
            file_obj.write("\n")


def _default_config_dir() -> Path:
    env_value = os.environ.get(CONFIG_DIR_ENV)
    if env_value:
        return Path(env_value).expanduser()
    return DEFAULT_CONFIG_DIR
