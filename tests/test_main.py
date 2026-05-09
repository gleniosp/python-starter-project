import pytest

from python_starter_project.main import main


def test_main_prints_hello(capsys: pytest.CaptureFixture[str]) -> None:
    main()

    captured = capsys.readouterr()
    assert captured.out == "Hello word!\n"
