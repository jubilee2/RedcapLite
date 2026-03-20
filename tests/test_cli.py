import pytest

from redcaplite.cli.main import (
    build_access_parser,
    build_metadata_parser,
    build_parser,
    build_profile_parser,
    main,
)


def test_main_returns_success() -> None:
    assert main([]) == 0


def test_build_parser_uses_rcl_prog() -> None:
    parser = build_parser()

    assert parser.prog == "rcl"


def test_access_command_parses_profile() -> None:
    assert main(["access", "data_project"]) == 0


def test_profile_metadata_command_parses_subcommand() -> None:
    assert main(["data_project", "metadata", "export"]) == 0


def test_access_help_works(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_access_parser().parse_args(["data_project", "--help"])

    captured = capsys.readouterr()

    assert exc_info.value.code == 0
    assert "usage: rcl access" in captured.out


def test_metadata_help_works(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_profile_parser("data_project").parse_args(["metadata", "--help"])

    captured = capsys.readouterr()

    assert exc_info.value.code == 0
    assert "usage: rcl data_project metadata" in captured.out


def test_invalid_top_level_command_has_friendly_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_profile_parser("data_project").parse_args(["unknown"])

    captured = capsys.readouterr()

    assert exc_info.value.code == 2
    assert "unknown command 'unknown'" in captured.err


def test_missing_access_profile_has_friendly_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["access"])

    captured = capsys.readouterr()

    assert exc_info.value.code == 2
    assert "access requires a profile" in captured.err


def test_missing_metadata_subcommand_has_friendly_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_metadata_parser("data_project").parse_args([])

    captured = capsys.readouterr()

    assert exc_info.value.code == 2
    assert "metadata requires a subcommand" in captured.err
