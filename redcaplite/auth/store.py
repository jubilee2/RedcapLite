from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from redcaplite.config.profiles import DEFAULT_APP_DIR


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
    """Placeholder file-backed token store reserved for a future phase."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        self.config_dir = config_dir or DEFAULT_APP_DIR
        self.path = self.config_dir / TOKENS_FILENAME

    def get_token(self, key: str) -> Optional[str]:
        del key
        return None

    def set_token(self, key: str, token: str) -> None:
        del key, token
        raise NotImplementedError("Token persistence will be implemented in a later phase")
