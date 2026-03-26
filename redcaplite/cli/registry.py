"""Registry of CLI command modules."""

from __future__ import annotations

from collections.abc import Iterator
from types import ModuleType

from . import metadata, profiles, setup, sync

_COMMAND_MODULES: tuple[ModuleType, ...] = (setup, metadata, sync, profiles)


def iter_command_modules() -> Iterator[ModuleType]:
    """Yield command modules that attach their parsers to the root CLI."""
    yield from _COMMAND_MODULES
