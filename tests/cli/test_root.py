from __future__ import annotations

from redcaplite.cli.main import build_parser, main


def test_main_without_args_prints_help(capsys) -> None:
    assert main([]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl [-h] {setup,metadata,sync,profiles} ..." in captured.out
    assert "setup" in captured.out
    assert "metadata" in captured.out
    assert "sync" in captured.out


def test_main_with_version_prints_version(monkeypatch, capsys) -> None:
    monkeypatch.setattr("redcaplite.cli.main.get_version", lambda: "9.9.9")

    assert main(["--version"]) == 0

    captured = capsys.readouterr()
    assert captured.out == "rcl 9.9.9\n"
    assert captured.err == ""


def test_main_with_root_help_flag_prints_root_help(capsys) -> None:
    assert main(["--help"]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl [-h] {setup,metadata,sync,profiles} ..." in captured.out
    assert "Create or update stored access for a REDCap profile." in captured.out
    assert "sync" in captured.out
    assert captured.err == ""


def test_main_with_setup_help_prints_setup_help(capsys) -> None:
    assert main(["setup", "demo", "--help"]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl setup <profile> [-h]" in captured.out
    assert "Create or update stored access for a REDCap profile." in captured.out
    assert captured.err == ""


def test_main_with_metadata_help_prints_metadata_help(capsys) -> None:
    assert main(["metadata", "demo", "--help"]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl metadata <profile> [-h]" in captured.out
    assert "Inspect and edit project metadata." in captured.out
    assert captured.err == ""


def test_main_with_metadata_subcommand_help_prints_subcommand_help(capsys) -> None:
    assert main(["metadata", "demo", "list", "--help"]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl metadata <profile> list [-h]" in captured.out
    assert "--field FIELD_NAMES" in captured.out
    assert "--form FORM_NAMES" in captured.out
    assert captured.err == ""


def test_main_with_metadata_pull_help_prints_subcommand_help(capsys) -> None:
    assert main(["metadata", "demo", "pull", "--help"]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl metadata <profile> pull [-h]" in captured.out
    assert captured.err == ""


def test_main_returns_error_for_missing_command(capsys) -> None:
    assert main([]) == 0

    captured = capsys.readouterr()
    assert captured.err == ""


def test_main_returns_error_for_missing_profile_for_setup(capsys) -> None:
    assert main(["setup"]) == 2

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "the following arguments are required: <profile>" in captured.err


def test_build_parser_supports_metadata_group() -> None:
    parser = build_parser()

    parsed = parser.parse_args(["metadata", "demo", "list"])

    assert parsed.profile == "demo"
    assert parsed.command == "metadata"
    assert parsed.metadata_command == "list"


def test_build_parser_supports_metadata_pull() -> None:
    parser = build_parser()

    parsed = parser.parse_args(["metadata", "demo", "pull"])

    assert parsed.profile == "demo"
    assert parsed.command == "metadata"
    assert parsed.metadata_command == "pull"


def test_build_parser_supports_metadata_list_fields_filters() -> None:
    parser = build_parser()

    parsed = parser.parse_args(
        ["metadata", "demo", "list", "--form", "demographics", "--field", "age"]
    )

    assert parsed.profile == "demo"
    assert parsed.metadata_command == "list"
    assert parsed.form_names == ["demographics"]
    assert parsed.field_names == ["age"]


def test_build_parser_supports_metadata_add_field_flags() -> None:
    parser = build_parser()

    parsed = parser.parse_args(
        [
            "metadata",
            "demo",
            "add",
            "age",
            "demographics",
            "--field-type",
            "text",
            "--field-label",
            "Age",
        ]
    )

    assert parsed.profile == "demo"
    assert parsed.command == "metadata"
    assert parsed.metadata_command == "add"
    assert parsed.field_name == "age"
    assert parsed.form_name == "demographics"
    assert parsed.field_flags == ["--field-type", "text", "--field-label", "Age"]


def test_build_parser_supports_metadata_edit_field_flags() -> None:
    parser = build_parser()

    parsed = parser.parse_args(["metadata", "demo", "edit", "age", "--field-label", "Participant age"])

    assert parsed.profile == "demo"
    assert parsed.metadata_command == "edit"
    assert parsed.field_name == "age"
    assert parsed.field_flags == ["--field-label", "Participant age"]


def test_build_parser_supports_metadata_remove_field_confirmation_flag() -> None:
    parser = build_parser()

    parsed = parser.parse_args(["metadata", "demo", "remove", "age", "--yes"])

    assert parsed.profile == "demo"
    assert parsed.metadata_command == "remove"
    assert parsed.field_name == "age"
    assert parsed.yes is True


def test_build_parser_supports_setup_command() -> None:
    parser = build_parser()

    parsed = parser.parse_args(["setup", "demo"])

    assert parsed.profile == "demo"
    assert parsed.command == "setup"
    assert callable(parsed.handler)


def test_build_parser_supports_sync_command() -> None:
    parser = build_parser()

    parsed = parser.parse_args(
        [
            "sync",
            "profile1",
            "profile2",
            "--yes",
            "--dry-run",
            "--summary-only",
            "--diff-by",
            "field_name",
            "--backup-file",
            "backup.csv",
        ]
    )

    assert parsed.profile == "profile1"
    assert parsed.command == "sync"
    assert parsed.target_profile == "profile2"
    assert parsed.yes is True
    assert parsed.dry_run is True
    assert parsed.summary_only is True
    assert parsed.diff_by == "field_name"
    assert parsed.backup_file == "backup.csv"


def test_build_parser_supports_profiles_command() -> None:
    parser = build_parser()

    parsed = parser.parse_args(["profiles"])

    assert parsed.command == "profiles"
    assert callable(parsed.handler)
