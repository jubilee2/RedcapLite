from __future__ import annotations

from pathlib import Path
from typing import Dict


class MetadataTransformError(ValueError):
    """Raised when metadata transformation cannot continue."""


def transform_metadata_file(source: Path, destination: Path) -> Dict[str, str]:
    """Return a lightweight transform result for future metadata workflows."""

    if not source.exists():
        raise MetadataTransformError(f"Metadata file not found: {source}")
    return {
        "source": str(source),
        "destination": str(destination),
        "status": "pending",
        "message": "Transformation rules will be added in a future phase.",
    }
