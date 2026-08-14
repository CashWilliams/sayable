from sayable import __version__, transform
from sayable.config import load_config


def test_transform_matches_cli_pipeline():
    cfg = load_config(None)
    cfg["tagger_enabled"] = False
    assert transform("AI at 12:00 pm", config=cfg) == "A I at twelve o'clock p m"


def test_transform_keeps_paragraphs_when_chunking():
    cfg = load_config(None)
    cfg["tagger_enabled"] = False
    cfg["chunk_size"] = 80
    assert transform("First paragraph.\n\nSecond paragraph.", config=cfg) == (
        "First paragraph.\n\nSecond paragraph."
    )


def test_package_exports_version():
    assert __version__