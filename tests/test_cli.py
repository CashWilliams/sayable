import json

from sayable.cli import (
    EXIT_BAD_ARGS_OR_CONFIG,
    EXIT_INPUT_READ,
    EXIT_MODEL_LOAD,
    EXIT_OUTPUT_WRITE,
    main,
)


def test_cli_stdin_stdout_success(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin.read", lambda: "AI at 12:00 pm")
    assert main(["--no-tags"]) == 0
    captured = capsys.readouterr()
    assert "A I at twelve o'clock p m" in captured.out
    assert captured.err == ""


def test_cli_config_failure_stderr_only(tmp_path, capsys, monkeypatch):
    config = tmp_path / "bad.json"
    config.write_text(json.dumps({"output_mode": "bad"}), encoding="utf-8")
    monkeypatch.setattr("sys.stdin.read", lambda: "hello")
    assert main(["--config", str(config)]) == EXIT_BAD_ARGS_OR_CONFIG
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "config error:" in captured.err


def test_cli_missing_config_file_is_bad_config(capsys):
    assert main(["--config", "/definitely/missing.json"]) == EXIT_BAD_ARGS_OR_CONFIG
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "config error:" in captured.err


def test_cli_malformed_json_config_is_bad_config(tmp_path, capsys, monkeypatch):
    path = tmp_path / "bad.json"
    path.write_text("{nope", encoding="utf-8")
    monkeypatch.setattr("sys.stdin.read", lambda: "hello")
    assert main(["--config", str(path)]) == EXIT_BAD_ARGS_OR_CONFIG
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "config error:" in captured.err


def test_cli_missing_input_file(capsys):
    assert main(["--input", "/definitely/missing/input.txt"]) == EXIT_INPUT_READ
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "input read failed" in captured.err


def test_cli_unwritable_output_path(tmp_path, capsys, monkeypatch):
    output_dir = tmp_path / "out-dir"
    output_dir.mkdir()
    monkeypatch.setattr("sys.stdin.read", lambda: "hello")
    assert main(["--no-tags", "--output", str(output_dir)]) == EXIT_OUTPUT_WRITE
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "output write failed" in captured.err


def test_cli_malformed_model(tmp_path, capsys, monkeypatch):
    model = tmp_path / "bad-model.json"
    model.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr("sys.stdin.read", lambda: "hello")
    assert main(["--model", str(model)]) == EXIT_MODEL_LOAD
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "model load failed" in captured.err


def test_cli_help(capsys):
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    captured = capsys.readouterr()
    assert "Clean text" in captured.out
