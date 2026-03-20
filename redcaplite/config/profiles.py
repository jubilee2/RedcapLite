"""Profile persistence for the redcaplite CLI."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class Profile:
    """Named connection profile for a REDCap project."""

    name: str
    url: str


class ProfileStore:
    """Load and save CLI profiles from the local filesystem."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        self.config_dir = config_dir or Path.home() / ".config" / "redcaplite"
        self.path = self.config_dir / "profiles.json"

    def load(self) -> Dict[str, Profile]:
        """Return all stored profiles keyed by profile name."""
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return {
            name: Profile(name=name, url=details["url"])
            for name, details in data.items()
        }

    def save(self, profiles: Dict[str, Profile]) -> None:
        """Persist the provided profiles to disk."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        serialized = {
            name: {key: value for key, value in asdict(profile).items() if key != "name"}
            for name, profile in profiles.items()
        }
        self.path.write_text(
            json.dumps(serialized, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def get(self, name: str) -> Optional[Profile]:
        """Return a stored profile by name, if present."""
        return self.load().get(name)

    def upsert(self, profile: Profile) -> None:
        """Create or update a profile."""
        profiles = self.load()
        profiles[profile.name] = profile
        self.save(profiles)
