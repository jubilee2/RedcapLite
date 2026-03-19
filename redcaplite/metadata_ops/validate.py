from __future__ import annotations

from pathlib import Path
from typing import Dict


class MetadataValidationError(ValueError):
    """Raised when metadata validation cannot continue."""


def validate_metadata_file(path: Path) -> Dict[str, str]:
    """Return a lightweight validation result for metadata workflows."""

    if not path.exists():
        raise MetadataValidationError(f"Metadata file not found: {path}")
    return {
        "path": str(path),
        "status": "pending",
        "message": "Validation rules will be added in a future phase.",
    }
