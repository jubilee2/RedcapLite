from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


APP_DIR_ENV = "REDCAPLITE_CONFIG_DIR"
DEFAULT_APP_DIR = Path.home() / ".config" / "redcaplite"
PROFILES_FILENAME = "profiles.json"


@dataclass
class Profile:
    """Named REDCap connection settings reserved for future CLI phases."""

    name: str
    url: str
    token_key: Optional[str] = None


class ProfileStore:
    """Placeholder profile storage abstraction for future CLI persistence."""

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
        return {}

    def save(self, profiles: Dict[str, Profile]) -> None:
        del profiles
        raise NotImplementedError("Profile persistence will be implemented in a later phase")

    def get(self, name: str) -> Optional[Profile]:
        del name
        return None

    def set(self, profile: Profile) -> Profile:
        del profile
        raise NotImplementedError("Profile persistence will be implemented in a later phase")

    def list(self) -> List[Profile]:
        return []
