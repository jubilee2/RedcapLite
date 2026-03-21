from __future__ import annotations

from redcaplite.cli.main import build_parser, build_profile_parser, main


def test_main_without_args_prints_help(capsys) -> None:
    assert main([]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl" in captured.out
    assert "rcl <profile> metadata add-field <field_name> <form_name> [flags]" in captured.out


def test_main_with_version_prints_version(monkeypatch, capsys) -> None:
    monkeypatch.setattr("redcaplite.cli.main.get_version", lambda: "9.9.9")

    assert main(["--version"]) == 0

    captured = capsys.readouterr()
    assert captured.out == "rcl 9.9.9\n"
    assert captured.err == ""


def test_main_with_root_help_flag_prints_root_help(capsys) -> None:
    assert main(["--help"]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl" in captured.out
    assert captured.err == ""


def test_main_with_access_help_prints_access_help(capsys) -> None:
    assert main(["access", "--help"]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl access" in captured.out
    assert "Create or update stored access for a REDCap profile." in captured.out
    assert captured.err == ""


def test_main_with_metadata_help_prints_metadata_help(capsys) -> None:
    assert main(["demo", "metadata", "--help"]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl demo metadata" in captured.out
    assert "Inspect and edit project metadata." in captured.out
    assert captured.err == ""


def test_main_with_metadata_subcommand_help_prints_subcommand_help(capsys) -> None:
    assert main(["demo", "metadata", "show-field", "--help"]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl demo metadata show-field" in captured.out
    assert "field_name" in captured.out
    assert captured.err == ""


def test_main_returns_error_for_missing_profile_subcommand(capsys) -> None:
    assert main(["demo"]) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "the following arguments are required: command" in captured.err


def test_build_parser_uses_rcl_prog() -> None:
    parser = build_parser()

    assert parser.prog == "rcl"


def test_build_profile_parser_supports_metadata_group() -> None:
    parser = build_profile_parser("demo")

    parsed = parser.parse_args(["metadata", "list-fields"])

    assert parsed.command == "metadata"
    assert parsed.metadata_command == "list-fields"


def test_build_profile_parser_supports_metadata_list_fields_form_filter() -> None:
    parser = build_profile_parser("demo")

    parsed = parser.parse_args(["metadata", "list-fields", "--form", "demographics"])

    assert parsed.metadata_command == "list-fields"
    assert parsed.form_name == "demographics"


def test_build_profile_parser_supports_metadata_add_field_flags() -> None:
    parser = build_profile_parser("demo")

    parsed = parser.parse_args(
        [
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

    assert parsed.command == "metadata"
    assert parsed.metadata_command == "add-field"
    assert parsed.field_name == "age"
    assert parsed.form_name == "demographics"
    assert parsed.field_flags == ["--field-type", "text", "--field-label", "Age"]


def test_build_profile_parser_supports_metadata_edit_field_flags() -> None:
    parser = build_profile_parser("demo")

    parsed = parser.parse_args(["metadata", "edit-field", "age", "--field-label", "Participant age"])

    assert parsed.metadata_command == "edit-field"
    assert parsed.field_name == "age"
    assert parsed.field_flags == ["--field-label", "Participant age"]


def test_build_profile_parser_supports_metadata_remove_field_confirmation_flag() -> None:
    parser = build_profile_parser("demo")

    parsed = parser.parse_args(["metadata", "remove-field", "age", "--yes"])

    assert parsed.metadata_command == "remove-field"
    assert parsed.field_name == "age"
    assert parsed.yes is True
