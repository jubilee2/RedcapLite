from __future__ import annotations

from pathlib import Path
from typing import Dict


class MetadataTransformError(ValueError):
    """Raised when metadata transformation cannot continue."""


def transform_metadata_file(source: Path, destination: Path) -> Dict[str, str]:
    """Placeholder transform hook for future metadata workflows."""

    return {
        "source": str(source),
        "destination": str(destination),
        "status": "not_implemented",
        "message": "Metadata transformation will be implemented in a later phase.",
    }
