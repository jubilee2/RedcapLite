from __future__ import annotations

import argparse
from pathlib import Path

from redcaplite.cli.output import CliError, format_json
from redcaplite.metadata_ops import (
    MetadataTransformError,
    MetadataValidationError,
    transform_metadata_file,
    validate_metadata_file,
)


def build_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("metadata", help="Metadata workflow commands")
    metadata_subparsers = parser.add_subparsers(dest="metadata_command", required=True)

    validate_parser = metadata_subparsers.add_parser("validate", help="Validate metadata input")
    validate_parser.add_argument("path", help="Path to metadata file")
    validate_parser.set_defaults(handler=handle_validate)

    transform_parser = metadata_subparsers.add_parser("transform", help="Transform metadata input")
    transform_parser.add_argument("source", help="Source metadata file")
    transform_parser.add_argument("destination", help="Destination path")
    transform_parser.set_defaults(handler=handle_transform)


def handle_validate(args: argparse.Namespace) -> int:
    try:
        result = validate_metadata_file(Path(args.path))
    except MetadataValidationError as error:
        raise CliError(str(error)) from error
    print(format_json(result))
    return 0


def handle_transform(args: argparse.Namespace) -> int:
    try:
        result = transform_metadata_file(Path(args.source), Path(args.destination))
    except MetadataTransformError as error:
        raise CliError(str(error)) from error
    print(format_json(result))
    return 0
