from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from redcaplite.config.profiles import _default_config_dir


TOKENS_FILE_NAME = "tokens.json"


class TokenStore:
    """Abstraction for storing profile tokens outside the CLI command layer."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        self.config_dir = config_dir or _default_config_dir()
        self.path = self.config_dir / TOKENS_FILE_NAME

    def get(self, profile_name: str) -> Optional[str]:
        return self._load().get(profile_name)

    def save(self, profile_name: str, token: str) -> None:
        tokens = self._load()
        tokens[profile_name] = token
        self._write(tokens)

    def delete(self, profile_name: str) -> None:
        tokens = self._load()
        if profile_name in tokens:
            del tokens[profile_name]
            self._write(tokens)

    def _load(self) -> Dict[str, str]:
        if not self.path.exists():
            return {}
        with self.path.open("r", encoding="utf-8") as file_obj:
            return json.load(file_obj)

    def _write(self, data: Dict[str, str]) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file_obj:
            json.dump(data, file_obj, indent=2, sort_keys=True)
            file_obj.write("\n")
