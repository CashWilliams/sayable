from sayable.classifier import NaiveBayesTagger
from sayable.config import load_config
from sayable.tagger import insert_tags


def test_tagger_inserts_laugh():
    cfg = load_config(None)
    text = "haha that was funny."
    out = insert_tags(text, NaiveBayesTagger(), cfg)
    assert out.startswith("[laugh] ")
