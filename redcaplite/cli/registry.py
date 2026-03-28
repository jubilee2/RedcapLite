"""Registry of CLI command modules."""

from __future__ import annotations

from collections.abc import Iterator
from types import ModuleType

from . import arms, events, files, metadata, profiles, project, records, setup, survey, sync, users

_COMMAND_MODULES: tuple[ModuleType, ...] = (
    setup,
    metadata,
    records,
    users,
    arms,
    events,
    project,
    survey,
    files,
    sync,
    profiles,
)


def iter_command_modules() -> Iterator[ModuleType]:
    """Yield command modules that attach their parsers to the root CLI."""
    yield from _COMMAND_MODULES
