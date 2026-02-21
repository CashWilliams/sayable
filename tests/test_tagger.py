from sayable.classifier import NaiveBayesTagger
from sayable.config import load_config
from sayable.normalizer import normalize_text
from sayable.tagger import insert_tags


def run_pipeline(text, cfg):
    normalized = normalize_text(text, cfg)
    return insert_tags(normalized, NaiveBayesTagger(), cfg)


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
