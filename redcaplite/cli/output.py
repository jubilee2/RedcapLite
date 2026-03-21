"""Output helpers for the redcaplite CLI."""

from __future__ import annotations

import sys
from typing import Any, TextIO


def print_error(message: str, hint: str | None = None, stream: TextIO | None = None) -> None:
    """Print a formatted CLI error message."""
    target = stream if stream is not None else sys.stderr
    print(f"Error: {message}", file=target)
    if hint:
        print(f"Hint: {hint}", file=target)


def print_success(message: str, stream: TextIO | None = None) -> None:
    """Print a success message to stdout."""
    target = stream if stream is not None else sys.stdout
    print(message, file=target)


def print_preview(summary: list[str], stream: TextIO | None = None) -> None:
    """Print a multi-line preview summary."""
    target = stream if stream is not None else sys.stdout
    for line in summary:
        print(line, file=target)


def print_table(rows: list[dict[str, Any]], stream: TextIO | None = None) -> None:
    """Print a list of dictionaries in a simple aligned table."""
    if not rows:
        return

    target = stream if stream is not None else sys.stdout
    headers = list(rows[0].keys())
    table_rows = [[str(row.get(header, "")) for header in headers] for row in rows]
    widths = [
        max(len(header), *(len(row[index]) for row in table_rows))
        for index, header in enumerate(headers)
    ]

    print(
        "  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)),
        file=target,
    )
    print("  ".join("-" * width for width in widths), file=target)
    for row in table_rows:
        print(
            "  ".join(value.ljust(widths[index]) for index, value in enumerate(row)),
            file=target,
        )
