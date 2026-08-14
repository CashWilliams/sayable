import csv
import json
import subprocess
import sys

import pytest

from sayable.classifier import NaiveBayesTagger
from sayable.config import load_config
from sayable.normalizer import normalize_text
from sayable.tagger import insert_tags


def run_pipeline(text, cfg):
    normalized = normalize_text(text, cfg)
    return insert_tags(normalized, NaiveBayesTagger(), cfg)


def test_tagger_preserves_paragraph_breaks():
    cfg = load_config(None)
    cfg["tagger_enabled"] = True
    out = insert_tags("sorry about that.\n\nlet us continue.", NaiveBayesTagger(), cfg)
    assert "\n\n" in out


def test_tagger_inserts_sigh():
    cfg = load_config(None)
    text = "sorry about that."
    out = run_pipeline(text, cfg)
    assert out.startswith("[sigh] ")


def test_tagger_uses_gasp_for_exciting_ai_news():
    cfg = load_config(None)
    out = run_pipeline("This is some cool A.I. news...", cfg)
    assert out.startswith("[gasp] ")
    assert "[groan]" not in out


def test_tagger_uses_gasp_for_surprise_phrases():
    cfg = load_config(None)
    assert run_pipeline("Wow, I did not expect this", cfg).startswith("[gasp] ")
    assert run_pipeline("I can't believe this", cfg).startswith("[gasp] ")


def test_tagger_avoids_groan_for_interesting_sentence():
    cfg = load_config(None)
    out = run_pipeline("Wow! This is something interesting.", cfg)
    assert "[groan]" not in out
    assert "[gasp]" in out


def test_rules_strategy_and_tag_limit():
    cfg = load_config(None)
    cfg["tagger_strategy"] = "rules"
    cfg["tag_max_per_chunk"] = 1
    out = run_pipeline("Ahem. Shh. Ugh.", cfg)
    assert out.count("[clear throat]") == 1
    assert "[shush]" not in out
    assert "[groan]" not in out


def test_neutral_command_text_is_not_tagged():
    cfg = load_config(None)
    for text in ["uv run pytest", "git status", "curl https://example.com"]:
        out = run_pipeline(text, cfg)
        assert "[" not in out


def test_neutral_documentation_text_is_not_tagged():
    cfg = load_config(None)
    text = "Install dependencies and call normalize_text with a config object."
    out = run_pipeline(text, cfg)
    assert "[" not in out


def test_default_confidence_skips_weak_groan():
    cfg = load_config(None)
    assert cfg["tag_min_confidence"] == 0.55
    out = insert_tags("This is interesting.", NaiveBayesTagger(), cfg)
    assert "[groan]" not in out


def test_disabled_tags_are_never_emitted():
    cfg = load_config(None)
    cfg["label_to_tag"] = {"sigh": "[sigh]", "none": ""}
    cfg["disabled_tags"] = ["[sigh]"]
    classifier = NaiveBayesTagger()
    out = insert_tags("sorry about that.", classifier, cfg)
    assert "[sigh]" not in out


def test_default_tagger_uses_bundled_model():
    tagger = NaiveBayesTagger()
    assert "ssml" in tagger.model["vocab"]
    assert "clear_throat" in tagger.model["labels"]


def test_model_loader_accepts_metadata_wrapper(tmp_path):
    base = NaiveBayesTagger().model
    path = tmp_path / "model.json"
    path.write_text(json.dumps({"metadata": {"schema_version": 1}, "model": base}), encoding="utf-8")
    assert NaiveBayesTagger.from_json(path).predict("sorry about that")[0] == "sigh"


def test_model_loader_rejects_missing_inference_fields(tmp_path):
    path = tmp_path / "bad-model.json"
    path.write_text(json.dumps({"foo": 1}), encoding="utf-8")
    with pytest.raises(ValueError, match="labels"):
        NaiveBayesTagger.from_json(path)


def test_saved_model_contains_every_training_label(tmp_path):
    out = tmp_path / "model.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/train_tag_model.py",
            "--data",
            "data/tag_train.csv",
            "--out",
            str(out),
            "--seed",
            "7",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    csv_labels = set()
    with open("data/tag_train.csv", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            csv_labels.add(row["label"].strip())
    assert set(payload["model"]["labels"]) == csv_labels
    assert "clear_throat" in payload["model"]["labels"]


def test_training_script_writes_metadata_and_metrics(tmp_path):
    out = tmp_path / "model.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/train_tag_model.py",
            "--data",
            "data/tag_train.csv",
            "--out",
            str(out),
            "--seed",
            "7",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["metadata"]["schema_version"] == 1
    assert payload["metadata"]["training_rows"] > 0
    assert payload["metadata"]["label_counts"]["none"] > 0
    assert payload["metadata"]["seed"] == 7
    assert "accuracy" in payload["metrics"]
    assert "none_false_positives" in payload["metrics"]
    assert "label_counts" in result.stdout
