from sayable.classifier import NaiveBayesTagger
from sayable.config import load_config
from sayable.tagger import insert_tags


def test_tagger_inserts_sigh():
    cfg = load_config(None)
    text = "sorry about that."
    out = insert_tags(text, NaiveBayesTagger(), cfg)
    assert out.startswith("[sigh] ")
