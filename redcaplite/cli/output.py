"""Output helpers for the redcaplite CLI."""

from __future__ import annotations

import sys
from typing import Optional, TextIO



def print_error(message: str, hint: Optional[str] = None, stream: Optional[TextIO] = None) -> None:
    """Print a formatted CLI error message."""
    target = stream if stream is not None else sys.stderr
    print(f"Error: {message}", file=target)
    if hint:
        print(f"Hint: {hint}", file=target)
