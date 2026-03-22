from __future__ import annotations

from redcaplite.cli.main import build_parser, main


def test_main_without_args_prints_help(capsys) -> None:
    assert main([]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl <profile> [-h] {setup,metadata} ..." in captured.out
    assert "setup" in captured.out
    assert "metadata" in captured.out


def test_main_with_version_prints_version(monkeypatch, capsys) -> None:
    monkeypatch.setattr("redcaplite.cli.main.get_version", lambda: "9.9.9")

    assert main(["--version"]) == 0

    captured = capsys.readouterr()
    assert captured.out == "rcl 9.9.9\n"
    assert captured.err == ""


def test_main_with_root_help_flag_prints_root_help(capsys) -> None:
    assert main(["--help"]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl <profile> [-h] {setup,metadata} ..." in captured.out
    assert "Create or update stored access for a REDCap profile." in captured.out
    assert captured.err == ""


def test_main_with_setup_help_prints_setup_help(capsys) -> None:
    assert main(["demo", "setup", "--help"]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl <profile> setup [-h]" in captured.out
    assert "Create or update stored access for a REDCap profile." in captured.out
    assert captured.err == ""


def test_main_with_metadata_help_prints_metadata_help(capsys) -> None:
    assert main(["demo", "metadata", "--help"]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl <profile> metadata [-h]" in captured.out
    assert "Inspect and edit project metadata." in captured.out
    assert captured.err == ""


def test_main_with_metadata_subcommand_help_prints_subcommand_help(capsys) -> None:
    assert main(["demo", "metadata", "show-field", "--help"]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl <profile> metadata show-field [-h] field_name" in captured.out
    assert "field_name" in captured.out
    assert captured.err == ""


def test_main_returns_error_for_missing_profile_subcommand(capsys) -> None:
    assert main(["demo"]) == 2

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "the following arguments are required: command" in captured.err


def test_build_parser_supports_metadata_group() -> None:
    parser = build_parser()

    parsed = parser.parse_args(["demo", "metadata", "list-fields"])

    assert parsed.profile == "demo"
    assert parsed.command == "metadata"
    assert parsed.metadata_command == "list-fields"


def test_build_parser_supports_metadata_list_fields_form_filter() -> None:
    parser = build_parser()

    parsed = parser.parse_args(["demo", "metadata", "list-fields", "--form", "demographics"])

    assert parsed.profile == "demo"
    assert parsed.metadata_command == "list-fields"
    assert parsed.form_name == "demographics"


def test_build_parser_supports_metadata_add_field_flags() -> None:
    parser = build_parser()

    parsed = parser.parse_args(
        [
            "demo",
            "metadata",
            "add-field",
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
    assert parsed.metadata_command == "add-field"
    assert parsed.field_name == "age"
    assert parsed.form_name == "demographics"
    assert parsed.field_flags == ["--field-type", "text", "--field-label", "Age"]


def test_build_parser_supports_metadata_edit_field_flags() -> None:
    parser = build_parser()

    parsed = parser.parse_args(["demo", "metadata", "edit-field", "age", "--field-label", "Participant age"])

    assert parsed.profile == "demo"
    assert parsed.metadata_command == "edit-field"
    assert parsed.field_name == "age"
    assert parsed.field_flags == ["--field-label", "Participant age"]


def test_build_parser_supports_metadata_remove_field_confirmation_flag() -> None:
    parser = build_parser()

    parsed = parser.parse_args(["demo", "metadata", "remove-field", "age", "--yes"])

    assert parsed.profile == "demo"
    assert parsed.metadata_command == "remove-field"
    assert parsed.field_name == "age"
    assert parsed.yes is True


def test_build_parser_supports_setup_command() -> None:
    parser = build_parser()

    parsed = parser.parse_args(["demo", "setup"])

    assert parsed.profile == "demo"
    assert parsed.command == "setup"
    assert callable(parsed.handler)
