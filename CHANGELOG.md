# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, with entries listed in reverse chronological order.

## [2.1.1]

### Added
- Added `output_file` support for export and get APIs that return CSV, JSON, XML, or text responses.
- Added `rcl <profile> metadata pull` to export project metadata to a timestamped file and print the saved file name and total field count.
- Added tests covering saved output behavior for the shared HTTP handlers and client export flow.

### Changed
- Refactored raw response file writing into a dedicated `@output_handler` decorator.
- Expanded API docstrings, CLI docs, and README examples to document `output_file` and `metadata pull`.

## [2.1.0]

### Added
- Added the integrated `rcl` CLI workflow for REDCap profile-based operations.
- Added a metadata sync command to compare metadata between profiles and import reviewed changes into a target project.
- Added CI workflow improvements for concurrency and broader branch coverage.

### Changed
- Renamed metadata subcommands to shorter command names.
- Unified the package around both Python API usage and CLI workflows.

## [2.0.0]

### Added
- Added the integrated `rcl` CLI with profile setup support.
- Added metadata management commands to the CLI.

### Changed
- Introduced the 2.x package line centered on combined REDCap API and CLI support.
