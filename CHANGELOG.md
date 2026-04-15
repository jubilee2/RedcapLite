# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, with entries listed in reverse chronological order.

## [Unreleased]

### Changed
- Expanded the centralized CSV empty-schema registry and endpoint wiring to include user roles and user-role mappings exports so blank CSV responses now return correctly structured zero-row DataFrames for those fixed-schema APIs.
- Simplified blank CSV handling in `csv_handler` to rely on `pd.DataFrame(columns=empty_columns)`, which naturally preserves the legacy fallback for `None` and schema columns when provided.
- Simplified `Client.post(...)` CSV forwarding further by always passing `empty_columns` (including `None`) directly to `__csv_api`, reducing branching with no behavior change.
- Added optional CSV empty-schema support in the HTTP client/handler pipeline via `empty_columns`, so blank CSV responses can return a zero-row DataFrame with known columns when provided.
- Added a centralized REDCap CSV schema registry and wired fixed-schema export endpoints to pass their empty-column definitions while leaving dynamic exports on the previous empty DataFrame fallback.
- Added regression tests for blank CSV handling with and without schema columns and `RedcapClient` endpoint wiring for empty-column forwarding.

## [2.2.3]

### Changed
- Updated `RedcapClient` JSON-default export helpers (arms, DAGs, user-DAG mappings, events, field names, instruments, form-event mappings, project, repeating forms/events, users, user roles, and user-role mappings) to explicitly expose `format: Literal["json", "csv"] = "json"` and forward it in request payloads, aligning client method defaults with API `@optional_field('format', "json")` behavior.

## [2.2.2]

### Changed
- Replaced hard-coded API payload values of `'format': 'json'` with the shared `@optional_field('format', "json")` decorator across GET API request builders for consistent default handling.
- Updated `data_formatter` to only auto-JSON serialize dict/list payloads when no non-JSON format is explicitly requested, preserving custom payload types (for example, bytes) for caller-selected formats.
- Applied the shared `data_formatter` decorator to metadata and record import API payload builders, removing duplicated manual CSV/JSON serialization logic.
- Renamed shared API JSON formatting decorator references from `json_data_formatter` to `data_formatter` across API modules.
- Added unit tests for `data_formatter` JSON/CSV/string formatting behavior to guard decorator regressions.
- Simplified shared `data_formatter` fallback behavior to rely on `result['format']` defaults (typically set via `@optional_field`) before defaulting to JSON.
- Expanded CLI parser descriptions and help examples across command modules to highlight common usage patterns and command-specific help flows.
- Switched root/setup/metadata help output back to default argparse-generated `usage` formatting.
- Corrected `rcl sync` parser `prog` formatting so positional arguments are not duplicated in generated help usage output.
- Standardized `prog` values for `setup` and `metadata` to base command names so error messages avoid placeholder-style command prefixes.
- Updated DAG import payload formatting to use a shared data_formatter decorator with default format=json handling.
- Updated sync comparison table helpers to accept caller-provided display columns for CLI output formatting.

## [2.2.1]

### Added
- Added `--dry-run` mode to `rcl sync <source_profile> <target_profile>` to preview differences without importing metadata.
- Added optional backup export creation before metadata import during sync operations.
- Added sync summary output with total fields and a concise list of changed field names.

### Changed
- Improved sync comparison output to report identity fields (`field_name`, `form_name`) for additions, removals, and modifications.
- Updated CLI docs and examples for safer metadata sync workflows in this release.

## [2.2.0]

### Added
- Added `rcl profiles` to list saved profile names and configured API URLs.

### Changed
- Standardized CLI documentation on command-first usage: `rcl <command> <profile> ...`.
- Corrected legacy command-order wording from `rcl <profile> metadata pull` to `rcl metadata <profile> pull`.
- Clarified command examples and release notes for the command-first style (for example, `rcl metadata <profile> pull`).

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
