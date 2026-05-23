import json

import pytest

from sayable.config import ConfigError, load_config, validate_config


def test_default_config_validates():
    cfg = load_config(None)
    assert validate_config(cfg) is cfg


def test_invalid_enum_names_field_and_values():
    cfg = load_config(None)
    cfg["time_style"] = "military-ish"
    with pytest.raises(ConfigError, match="time_style.*12h.*24h"):
        validate_config(cfg)


def test_invalid_numeric_bounds():
    cfg = load_config(None)
    cfg["tag_min_confidence"] = 1.5
    with pytest.raises(ConfigError, match="tag_min_confidence"):
        validate_config(cfg)

    cfg = load_config(None)
    cfg["chunk_size"] = -1
    with pytest.raises(ConfigError, match="chunk_size"):
        validate_config(cfg)


def test_invalid_collection_types():
    cfg = load_config(None)
    cfg["allowed_tags"] = "[sigh]"
    with pytest.raises(ConfigError, match="allowed_tags"):
        validate_config(cfg)

    cfg = load_config(None)
    cfg["label_to_tag"] = []
    with pytest.raises(ConfigError, match="label_to_tag"):
        validate_config(cfg)


def test_load_config_raises_catchable_error(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"output_mode": "wav"}), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)
