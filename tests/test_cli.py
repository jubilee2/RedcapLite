from redcaplite.cli.main import build_parser, main



def test_main_returns_success() -> None:
    assert main([]) == 0



def test_build_parser_uses_rcl_prog() -> None:
    parser = build_parser()

    assert parser.prog == "rcl"
