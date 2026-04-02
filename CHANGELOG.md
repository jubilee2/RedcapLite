# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, with entries listed in reverse chronological order.

## [Unreleased]

### Changed
- Expanded CLI parser descriptions and help examples across command modules to highlight common usage patterns and command-specific help flows.
- Restored explicit `usage` output ordering for `rcl setup` and `rcl metadata` help text to preserve existing CLI test expectations.
- Corrected `rcl sync` parser `prog` formatting so positional arguments are not duplicated in generated help usage output.
- Standardized `prog` values for `setup` and `metadata` to base command names so error messages avoid placeholder-style command prefixes.

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
