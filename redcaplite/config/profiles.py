"""Profile persistence for the redcaplite CLI."""

from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
except ImportError:  # pragma: no cover - exercised when PyYAML is unavailable
    yaml = None


@dataclass
class Profile:
    """Named connection profile for a REDCap project."""

    name: str
    url: str


def get_profiles_path() -> Path:
    """Return the OS-specific path used for persisted CLI profiles."""
    system = platform.system()
    if system == "Windows":
        base_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif system == "Darwin":
        base_dir = Path.home() / "Library" / "Application Support"
    else:
        base_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base_dir / "redcaplite" / "profiles.yml"




def _safe_load_yaml(content: str) -> Any:
    """Load the simple profile YAML structure, with a stdlib fallback."""
    if yaml is not None:
        return yaml.safe_load(content)

    stripped = content.strip()
    if not stripped:
        return None

    parsed: Dict[str, Dict[str, str]] = {}
    current_name: Optional[str] = None
    for raw_line in content.splitlines():
        if not raw_line.strip():
            continue
        if not raw_line.startswith(" "):
            if not raw_line.endswith(":"):
                raise ValueError("Profiles file must contain a mapping of profile names to settings.")
            current_name = raw_line[:-1].strip()
            parsed[current_name] = {}
            continue
        if current_name is None:
            raise ValueError("Profiles file must contain a mapping of profile names to settings.")
        key, separator, value = raw_line.strip().partition(":")
        if separator != ":":
            raise ValueError(f'Profile "{current_name}" must contain a mapping of settings.')
        parsed[current_name][key.strip()] = value.strip()
    return parsed


def _safe_dump_yaml(data: Dict[str, Dict[str, str]]) -> str:
    """Dump the simple profile YAML structure, with a stdlib fallback."""
    if yaml is not None:
        return yaml.safe_dump(data, sort_keys=True)

    lines = []
    for profile_name in sorted(data):
        lines.append(f"{profile_name}:")
        for key, value in data[profile_name].items():
            lines.append(f"  {key}: {value}")
    return "\n".join(lines) + ("\n" if lines else "")

def _validate_profiles(data: Any) -> Dict[str, Dict[str, str]]:
    """Validate the YAML structure used by the profiles file."""
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("Profiles file must contain a mapping of profile names to settings.")

    validated_profiles: Dict[str, Dict[str, str]] = {}
    for name, details in data.items():
        if not isinstance(name, str) or not name:
            raise ValueError("Profile names must be non-empty strings.")
        if not isinstance(details, dict):
            raise ValueError(f'Profile "{name}" must contain a mapping of settings.')

        url = details.get("url")
        if not isinstance(url, str) or not url:
            raise ValueError(f'Profile "{name}" must include a non-empty string "url" value.')
        validated_profiles[name] = {"url": url}
    return validated_profiles


def _dump_profiles_yaml(data: Dict[str, Dict[str, str]]) -> str:
    """Serialize profiles to YAML using PyYAML."""
    validated_profiles = _validate_profiles(data)
    return _safe_dump_yaml(validated_profiles)


def load_profiles(path: Optional[Path] = None) -> Dict[str, Dict[str, str]]:
    """Load all saved profiles from YAML."""
    profiles_path = path or get_profiles_path()
    if not profiles_path.exists():
        return {}
    with profiles_path.open("r", encoding="utf-8") as profiles_file:
        return _validate_profiles(_safe_load_yaml(profiles_file.read()))


def save_profiles(data: Dict[str, Dict[str, str]], path: Optional[Path] = None) -> None:
    """Persist profiles to YAML, creating the parent directory when needed."""
    profiles_path = path or get_profiles_path()
    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    profiles_path.write_text(_dump_profiles_yaml(data), encoding="utf-8")


def get_profile(name: str, path: Optional[Path] = None) -> Optional[Dict[str, str]]:
    """Return a saved profile mapping by name, if present."""
    return load_profiles(path).get(name)


def get_profile_url(name: str, path: Optional[Path] = None) -> Optional[str]:
    """Return the saved URL for a profile, if present."""
    profile = get_profile(name, path)
    if profile is None:
        return None
    return profile["url"]


def set_profile(name: str, url: str, path: Optional[Path] = None) -> None:
    """Create or update a profile entry."""
    profiles = load_profiles(path)
    profiles[name] = {"url": url}
    save_profiles(profiles, path)


def remove_profile(name: str, path: Optional[Path] = None) -> None:
    """Remove a saved profile when it exists."""
    profiles = load_profiles(path)
    if name in profiles:
        del profiles[name]
        save_profiles(profiles, path)


class ProfileStore:
    """Load and save CLI profiles from the local filesystem."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        self.path = (config_dir / "profiles.yml") if config_dir is not None else get_profiles_path()

    @property
    def config_dir(self) -> Path:
        """Return the directory containing the profile file."""
        return self.path.parent

    def load(self) -> Dict[str, Profile]:
        """Return all stored profiles keyed by profile name."""
        return {
            name: Profile(name=name, url=details["url"])
            for name, details in load_profiles(self.path).items()
        }

    def save(self, profiles: Dict[str, Profile]) -> None:
        """Persist the provided profiles to disk."""
        serialized = {name: {"url": profile.url} for name, profile in profiles.items()}
        save_profiles(serialized, self.path)

    def get(self, name: str) -> Optional[Profile]:
        """Return a stored profile by name, if present."""
        url = get_profile_url(name, self.path)
        if url is None:
            return None
        return Profile(name=name, url=url)

    def upsert(self, profile: Profile) -> None:
        """Create or update a profile."""
        set_profile(profile.name, profile.url, self.path)

    def remove(self, name: str) -> None:
        """Remove a stored profile by name."""
        remove_profile(name, self.path)
