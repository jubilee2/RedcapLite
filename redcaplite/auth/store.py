from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional

from redcaplite.config.profiles import DEFAULT_APP_DIR, APP_DIR_ENV


TOKENS_FILENAME = "tokens.json"


class TokenStore(ABC):
    """Abstraction around API token persistence for CLI workflows."""

    @abstractmethod
    def get_token(self, key: str) -> Optional[str]:
        """Return the token for *key* if one is stored."""

    @abstractmethod
    def set_token(self, key: str, token: str) -> None:
        """Persist *token* for *key*."""


class FileTokenStore(TokenStore):
    """Simple file-backed token storage with restrictive file permissions."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        self.config_dir = config_dir or self.default_config_dir()
        self.path = self.config_dir / TOKENS_FILENAME

    @staticmethod
    def default_config_dir() -> Path:
        configured_dir = os.getenv(APP_DIR_ENV)
        if configured_dir:
            return Path(configured_dir).expanduser()
        return DEFAULT_APP_DIR

    def get_token(self, key: str) -> Optional[str]:
        return self._read_data().get(key)

    def set_token(self, key: str, token: str) -> None:
        data = self._read_data()
        data[key] = token
        self._write_data(data)

    def _read_data(self) -> Dict[str, str]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write_data(self, data: Dict[str, str]) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        fd = os.open(self.path, flags, 0o600)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, sort_keys=True)
        finally:
            try:
                os.chmod(self.path, 0o600)
            except OSError:
                pass
