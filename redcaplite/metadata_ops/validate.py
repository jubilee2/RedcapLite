from __future__ import annotations

from pathlib import Path
from typing import Dict


class MetadataValidationError(ValueError):
    """Raised when metadata validation cannot continue."""


def validate_metadata_file(path: Path) -> Dict[str, str]:
    """Placeholder validation hook for future metadata workflows."""

    return {
        "path": str(path),
        "status": "not_implemented",
        "message": "Metadata validation will be implemented in a later phase.",
    }
