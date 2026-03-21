"""Token storage abstraction for the redcaplite CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional


class TokenStore:
    """Persist API tokens in a local user-scoped file."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        self.config_dir = config_dir or Path.home() / ".config" / "redcaplite"
        self.path = self.config_dir / "tokens.json"

    def _load_all(self) -> Dict[str, str]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def get_token(self, profile_name: str) -> Optional[str]:
        """Return the stored token for a profile, if present."""
        return self._load_all().get(profile_name)

    def save_token(self, profile_name: str, token: str) -> None:
        """Save or replace the token for a profile."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        tokens = self._load_all()
        tokens[profile_name] = token
        self.path.write_text(
            json.dumps(tokens, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.chmod(self.path, 0o600)
